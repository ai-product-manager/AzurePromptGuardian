from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional
import json
from datetime import datetime
import uuid
import logging
import hashlib
from functools import lru_cache
import asyncio

# Azure SDKs
from azure.cosmos import CosmosClient
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from openai import AzureOpenAI

# Optimización
from tenacity import retry, stop_after_attempt, wait_exponential
from aiocache import Cache, cached
from aiocache.serializers import JsonSerializer

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== Configuración Segura ==========
class SecureConfig:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.secret_client = SecretClient(
            vault_url="https://keyvaultgrupo12.vault.azure.net/",
            credential=self.credential
        )
    
    @lru_cache(maxsize=1)
    def get_secret_cached(self, secret_name: str) -> str:
        try:
            return self.secret_client.get_secret(secret_name).value
        except Exception as e:
            logger.error(f"Error obteniendo secreto {secret_name}: {str(e)}")
            raise

config = SecureConfig()

# Umbrales de seguridad
SAFETY_THRESHOLDS = {
    "Hate": 4,
    "SelfHarm": 2,
    "Sexual": 3,
    "Violence": 3
}

# ========== Clientes con Conexiones Persistentes ==========
@lru_cache(maxsize=1)
def get_cosmos_client():
    return CosmosClient(
        config.get_secret_cached("COSMOS-ENDPOINT"),
        credential=config.get_secret_cached("COSMOS-kEY")
    )

@lru_cache(maxsize=1)
def get_openai_client():
    return AzureOpenAI(
        azure_endpoint=config.get_secret_cached("AZURE-OPENAI-ENDPOINT"),
        api_key=config.get_secret_cached("AZURE-OPENAI-KEY"),
        api_version="2024-05-01-preview"
    )

# ========== Modelos Pydantic ==========
class AnalysisIssue(BaseModel):
    type: Literal["fairness", "safety", "privacy", "inclusiveness", "bias", "other"]
    description: str
    severity: Literal["low", "medium", "high"]
    mitigation: str

class AnalysisResponse(BaseModel):
    analysis_id: str
    improved_prompt: Optional[str] = None
    fairness_score: float = Field(..., ge=0, le=1)
    safety_score: float = Field(..., ge=0, le=1)
    inclusivity_score: float = Field(..., ge=0, le=1)
    privacy_measures: List[str]
    transparency_report: dict
    accountability_id: str
    error: Optional[str] = None

class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=2000)
    
    @validator('prompt')
    def validate_prompt_length(cls, v):
        if len(v) < 10:
            raise ValueError("El prompt debe tener al menos 10 caracteres")
        if len(v) > 2000:
            raise ValueError("El prompt no puede exceder 2000 caracteres")
        return v

# ========== Funciones Principales ==========
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def analyze_content_safety(text: str) -> dict:
    try:
        client = ContentSafetyClient(
            endpoint=config.get_secret_cached("CONTENT-SAFETY-ENDPOINT"),
            credential=AzureKeyCredential(config.get_secret_cached("CONTENT-SAFETY-KEY"))
        )
        response = client.analyze_text(AnalyzeTextOptions(text=text))
        return {c.category: c.severity for c in response.categories_analysis}
    except Exception as e:
        logger.error(f"Content Safety Error: {str(e)}")
        raise

@retry(stop=stop_after_attempt(3), reraise=True)
async def analyze_text_features(text: str) -> dict:
    try:
        client = TextAnalyticsClient(
            endpoint=config.get_secret_cached("TEXT-ANALYTICS-ENDPOINT"),
            credential=AzureKeyCredential(config.get_secret_cached("TEXT-ANALYTICS-KEY"))
        )
        
        entities = await asyncio.to_thread(client.recognize_entities, documents=[text])
        sentiment = await asyncio.to_thread(client.analyze_sentiment, documents=[text])
        phrases = await asyncio.to_thread(client.extract_key_phrases, documents=[text])
        
        return {
            "pii": [{"text": e.text, "category": e.category} for e in entities[0].entities],
            "sentiment": {
                "label": sentiment[0].sentiment,
                "scores": {
                    "positive": sentiment[0].confidence_scores.positive,
                    "neutral": sentiment[0].confidence_scores.neutral,
                    "negative": sentiment[0].confidence_scores.negative
                }
            },
            "key_phrases": phrases[0].key_phrases
        }
    except Exception as e:
        logger.error(f"Text Analytics Error: {str(e)}", exc_info=True)
        raise

async def log_rejected_prompt(analysis_id: str, prompt: str, safety_data: dict):
    container = get_cosmos_client().get_database_client("PromptAnalysis").get_container_client("RejectedPrompts")
    audit_doc = {
        "id": analysis_id,
        "timestamp": datetime.utcnow().isoformat(),
        "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest(),
        "safety_analysis": safety_data,
        "status": "rejected"
    }
    await asyncio.to_thread(container.upsert_item, audit_doc)

def check_safety_violations(safety_results: dict) -> Optional[str]:
    for category, severity in safety_results.items():
        if SAFETY_THRESHOLDS.get(category, 6) <= severity:
            return f"Contenido no permitido en categoría: {category}"
    return None

# ========== Configuración FastAPI ==========
app = FastAPI(
    title="Azure Prompt Guardian API",
    version="4.0",
    docs_url="/docs",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://frontend.example.com"],
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization"],
    max_age=600
)

# Importar el router de dashboard
from dashboard_routes import router as dashboard_router 

# Agregar el router a la aplicación
app.include_router(dashboard_router)

# ========== Endpoints ==========
@app.post("/analyze-prompt", response_model=AnalysisResponse)
async def analyze_prompt(request: PromptRequest):
    try:
        # Validación inicial
        clean_prompt = request.prompt.strip()
        if len(clean_prompt) < 10:
            raise HTTPException(400, "Prompt inválido")
        
        # Análisis de seguridad
        safety_results = await analyze_content_safety(clean_prompt)
        
        # Verificar violaciones
        if error_msg := check_safety_violations(safety_results):
            analysis_id = str(uuid.uuid4())
            await log_rejected_prompt(analysis_id, clean_prompt, safety_results)
            return AnalysisResponse(
                analysis_id=analysis_id,
                error=error_msg,
                fairness_score=0.0,
                safety_score=0.0,
                inclusivity_score=0.0,
                privacy_measures=[],
                transparency_report={},
                accountability_id=analysis_id
            )
        
        # Análisis de texto
        text_results = await analyze_text_features(clean_prompt)
        redacted_prompt = redact_pii(clean_prompt, text_results["pii"])
        
        # Análisis con OpenAI
        openai_client = get_openai_client()
        openai_response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model=config.get_secret_cached("AZURE-OPENAI-DEPLOYMENT-NAME"),
            messages=[{
                "role": "system",
                "content": """Analiza el prompt y devuelve SOLO un JSON válido con:
                {
                    "improved_prompt": "string",
                    "safety_score": 0.0-1.0,
                    "fairness_score": 0.0-1.0,
                    "inclusivity_score": 0.0-1.0,
                    "issues": [{"type": "string", "description": "string", "severity": "string", "mitigation": "string"}]
                }"""
            }, {
                "role": "user",
                "content": redacted_prompt
            }],
            temperature=0.2
        )
        
        # Procesar respuesta
        analysis_data = json.loads(openai_response.choices[0].message.content)
        required_keys = ["improved_prompt", "safety_score", "fairness_score", "inclusivity_score"]
        if not all(key in analysis_data for key in required_keys):
            raise ValueError("Respuesta de OpenAI inválida")
        
        # Auditoría
        analysis_id = str(uuid.uuid4())
        audit_doc = {
            "id": analysis_id,
            "timestamp": datetime.utcnow().isoformat(),
            "prompt_hash": hashlib.sha256(clean_prompt.encode()).hexdigest(),
            "analysis": analysis_data,
            "metadata": {
                "safety": safety_results,
                "text_analytics": text_results,
                "compliance": ["GDPR", "ISO27001"]
            }
        }
        
        container = get_cosmos_client().get_database_client("PromptAnalysis").get_container_client("Analytics")
        await asyncio.to_thread(container.upsert_item, audit_doc)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            improved_prompt=analysis_data["improved_prompt"],
            fairness_score=analysis_data["fairness_score"],
            safety_score=analysis_data["safety_score"],
            inclusivity_score=analysis_data["inclusivity_score"],
            privacy_measures=["pii_redaction"],
            transparency_report={
                "safety_analysis": safety_results,
                "text_analysis": text_results
            },
            accountability_id=analysis_id
        )
        
    except Exception as e:
        logger.error(f"Error en análisis: {str(e)}", exc_info=True)
        raise HTTPException(500, "Error procesando la solicitud")

@app.get("/audit/{analysis_id}", tags=["Accountability"])
async def get_audit_trail(analysis_id: str):
    """
    Obtiene el registro completo de auditoría para un análisis específico
    
    - **analysis_id**: ID único generado durante el análisis
    """
    try:
        container = get_cosmos_client()\
            .get_database_client("PromptAnalysis")\
            .get_container_client("Analytics")
        
        document = await asyncio.to_thread(
            container.read_item,
            analysis_id,
            partition_key=analysis_id
        )
        
        return {
            "analysis_id": document["id"],
            "timestamp": document["timestamp"],
            "compliance": document["metadata"]["compliance"],
            "safety_summary": document["metadata"]["safety"],
            "text_analysis_summary": document["metadata"]["text_analytics"],
            "prompt_hash": document["prompt_hash"]
        }
    except Exception as e:
        raise HTTPException(404, "Registro de auditoría no encontrado")

@app.get("/health")
async def health_check():
    return {"status": "OK", "version": "4.0"}

# Funciones auxiliares
def redact_pii(text: str, pii_list: List[dict]) -> str:
    redacted = text
    for entity in pii_list:
        redacted = redacted.replace(entity["text"], f"[{entity['category']}]")
    return redacted

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)