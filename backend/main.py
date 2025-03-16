from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal, Optional
import os
import json
from datetime import datetime
import uuid

# Azure SDKs
from azure.cosmos import CosmosClient
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# OpenAI
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ========== Configuración de Clientes ==========
#
def create_clients():
    try:
        # Azure Cosmos DB
        cosmos_client = CosmosClient(
            os.getenv("COSMOS_ENDPOINT"), 
            credential=os.getenv("COSMOS_KEY")
        )
        database = cosmos_client.get_database_client("PromptAnalysis")
        container = database.get_container_client("Analytics")

        # Azure Content Safety
        content_safety_client = ContentSafetyClient(
            endpoint=os.getenv("CONTENT_SAFETY_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("CONTENT_SAFETY_KEY"))
        )

        # Azure Text Analytics
        text_analytics_client = TextAnalyticsClient(
            endpoint=os.getenv("TEXT_ANALYTICS_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("TEXT_ANALYTICS_KEY"))
        )

        # OpenAI
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        return container, content_safety_client, text_analytics_client, openai_client
    except Exception as e:
        print(f"Error creating clients: {str(e)}")
        raise

container, content_safety_client, text_analytics_client, openai_client = create_clients()

# ========== Modelos Pydantic ==========
class TextAnalyticsPII(BaseModel):
    text: str
    category: str

class AzureSafetyAnalysis(BaseModel):
    hate_severity: Optional[int] = None
    self_harm_severity: Optional[int] = None
    sexual_severity: Optional[int] = None
    violence_severity: Optional[int] = None

class TextAnalyticsResult(BaseModel):
    detected_pii: Optional[List[TextAnalyticsPII]] = None
    sentiment: Optional[dict] = None
    key_phrases: Optional[List[str]] = None

class AnalysisResponse(BaseModel):
    improvedPrompt: str
    openaiAnalysis: dict
    azureSafety: Optional[AzureSafetyAnalysis] = None
    textAnalytics: Optional[TextAnalyticsResult] = None

class PromptRequest(BaseModel):
    prompt: str

# ========== Funciones Auxiliares ==========
async def analyze_content_safety(text: str) -> AzureSafetyAnalysis:
    try:
        request = AnalyzeTextOptions(text=text)
        response = content_safety_client.analyze_text(request)
        
        return AzureSafetyAnalysis(
            hate_severity=response.categories_analysis[0].severity,
            self_harm_severity=response.categories_analysis[1].severity,
            sexual_severity=response.categories_analysis[2].severity,
            violence_severity=response.categories_analysis[3].severity
        )
    except Exception as e:
        print(f"Content Safety Error: {str(e)}")
        return AzureSafetyAnalysis()

async def analyze_text_features(text: str) -> TextAnalyticsResult:
    try:
        # Detección de entidades PII
        entities = text_analytics_client.recognize_entities([text])[0]
        detected_pii = [
            TextAnalyticsPII(text=entity.text, category=entity.category)
            for entity in entities.entities
        ]
        
        # Análisis de sentimiento
        sentiment = text_analytics_client.analyze_sentiment([text])[0]
        sentiment_scores = {
            "positive": sentiment.confidence_scores.positive,
            "neutral": sentiment.confidence_scores.neutral,
            "negative": sentiment.confidence_scores.negative
        }
        
        # Frases clave
        key_phrases = text_analytics_client.extract_key_phrases([text])[0]
        
        return TextAnalyticsResult(
            detected_pii=detected_pii,
            sentiment={
                "score": sentiment_scores,
                "label": sentiment.sentiment
            },
            key_phrases=key_phrases.key_phrases
        )
    except Exception as e:
        print(f"Text Analytics Error: {str(e)}")
        return TextAnalyticsResult()

# ========== Configuración FastAPI ==========
app = FastAPI(title="Azure Prompt Guardian API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar el router de dashboard
from dashboard_routes import router as dashboard_router 

# Agregar el router a la aplicación
app.include_router(dashboard_router)

@app.post("/analyze-prompt", response_model=AnalysisResponse)
async def analyze_prompt(request: PromptRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt requerido")
    
    try:
        # Paso 1: Análisis con Azure
        azure_safety = await analyze_content_safety(request.prompt)
        text_analytics = await analyze_text_features(request.prompt)
        
        # Paso 2: Análisis con OpenAI
        openai_response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": """Eres Azure Prompt Guardian API. Analiza prompts y devuelve JSON con:
                    {
                        "issues": [{"type": "...", "description": "...", "severity": "low|medium|high"}],
                        "improvements": ["..."],
                        "safetyScore": 0-10,
                        "clarityScore": 0-10,
                        "improvedPrompt": "..."
                    }"""
                },
                {
                    "role": "user",
                    "content": f"""Prompt a analizar: "{request.prompt}"
                    
                    Considera estos análisis previos de Azure:
                    - Severidad contenido peligroso: {azure_safety.dict() if azure_safety else None}
                    - PII detectado: {text_analytics.detected_pii if text_analytics else None}
                    """
                }
            ],
            response_format={"type": "json_object"}
        )
        
        # Procesar respuesta OpenAI
        openai_data = json.loads(openai_response.choices[0].message.content)
        
        # Paso 3: Guardar en CosmosDB
        analysis_doc = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "original_prompt": request.prompt,
            "openai_analysis": openai_data,
            "azure_metrics": {
                "content_safety": azure_safety.dict(),
                "text_analytics": text_analytics.dict()
            }
        }
        container.upsert_item(analysis_doc)
        
        # Construir respuesta
        return {
            "improvedPrompt": openai_data["improvedPrompt"],
            "openaiAnalysis": {
                "issues": openai_data.get("issues", []),
                "improvements": openai_data.get("improvements", []),
                "safetyScore": openai_data.get("safetyScore", 0),
                "clarityScore": openai_data.get("clarityScore", 0)
            },
            "azureSafety": azure_safety.dict(),
            "textAnalytics": text_analytics.dict()
        }
        
    except Exception as e:
        print(f"Error completo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")

@app.get("/")
async def health_check():
    return {"status": "OK", "version": "2.1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)