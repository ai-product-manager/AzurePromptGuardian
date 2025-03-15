from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal, Optional
import os
from openai import OpenAI
from dotenv import load_dotenv
import json

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="PromptGuardian API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Origen de Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Modelos de datos
class Issue(BaseModel):
    type: str
    description: str
    severity: Literal["low", "medium", "high"]

class AnalysisResponse(BaseModel):
    improvedPrompt: str
    analysis: dict

class PromptRequest(BaseModel):
    prompt: str

@app.post("/analyze-prompt", response_model=AnalysisResponse)
async def analyze_prompt(request: PromptRequest):
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Se requiere un prompt válido")
    
    try:
        # Llamada a la API de OpenAI
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",  # Puedes usar "gpt-3.5-turbo" si prefieres
            messages=[
                {
                    "role": "system",
                    "content": """
                    Actúa como un sistema de preprocesamiento de prompts llamado PromptGuardian.
                    
                    Tu tarea es analizar prompts que los usuarios quieren enviar a sistemas de IA generativa.
                    Debes devolver un JSON con el siguiente formato exacto:
                    {
                      "issues": [
                        {"type": "string", "description": "string", "severity": "low|medium|high"}
                      ],
                      "improvements": ["string"],
                      "safetyScore": number (0-10),
                      "clarityScore": number (0-10),
                      "improvedPrompt": "string"
                    }
                    """
                },
                {
                    "role": "user",
                    "content": f"""
                    Analiza el siguiente prompt:
                    
                    "{request.prompt}"
                    
                    Identifica problemas como:
                    - Errores gramaticales o de ortografía
                    - Ambigüedades o falta de claridad
                    - Posible contenido inapropiado o sesgado
                    - Solicitudes que podrían llevar a respuestas no éticas
                    - Información personal identificable (PII)
                    
                    Proporciona una versión mejorada del prompt que:
                    - Corrija los problemas identificados
                    - Sea más claro y específico
                    - Siga siendo fiel a la intención original del usuario
                    - Sea ético y seguro
                    
                    Asigna puntuaciones de 0 a 10 para seguridad y claridad.
                    Lista las mejoras específicas que has aplicado.
                    """
                }
            ],
            response_format={"type": "json_object"}
        )
        
        # Extraer y procesar la respuesta
        result = response.choices[0].message.content
        result_json = json.loads(response.choices[0].message.content)
        
        return {
            "improvedPrompt": result_json["improvedPrompt"],
            "analysis": {
                "issues": result_json["issues"],
                "improvements": result_json["improvements"],
                "safetyScore": result_json["safetyScore"],
                "clarityScore": result_json["clarityScore"],
            }
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al analizar el prompt: {str(e)}")

@app.get("/")
async def root():
    return {"message": "PromptGuardian API está funcionando"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)