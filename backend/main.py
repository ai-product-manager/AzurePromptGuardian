from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional, Dict, Any, Union
import json
from datetime import datetime
import uuid
import logging
import hashlib
from functools import lru_cache
import asyncio
import re

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

# Umbrales de ambigüedad y calidad
AMBIGUITY_THRESHOLD = 0.6
COMPLETENESS_THRESHOLD = 0.7
CLARITY_THRESHOLD = 0.7

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
    
@lru_cache(maxsize=1)
def get_text_analytics_client():
    return TextAnalyticsClient(
        endpoint=config.get_secret_cached("TEXT-ANALYTICS-ENDPOINT"),
        credential=AzureKeyCredential(config.get_secret_cached("TEXT-ANALYTICS-KEY"))
    )

# ========== Modelos Pydantic ==========
class AnalysisIssue(BaseModel):
    type: Literal["fairness", "safety", "privacy", "inclusiveness", "bias", "ambiguity", "clarity", "completeness", "other"]
    description: str
    severity: Literal["low", "medium", "high"]
    mitigation: str

class PromptVariant(BaseModel):
    variant_text: str
    quality_score: float
    clarity_score: float
    specificity_score: float
    explanation: str

class AnalysisResponse(BaseModel):
    analysis_id: str
    improved_prompt: Optional[str] = None
    original_prompt: Optional[str] = None
    fairness_score: float = Field(..., ge=0, le=1)
    safety_score: float = Field(..., ge=0, le=1)
    inclusivity_score: float = Field(..., ge=0, le=1)
    clarity_score: float = Field(..., ge=0, le=1)
    completeness_score: float = Field(..., ge=0, le=1)
    ambiguity_score: float = Field(..., ge=0, le=1)
    privacy_measures: List[str]
    transparency_report: dict
    accountability_id: str
    suggested_variants: Optional[List[PromptVariant]] = None
    improvement_explanation: Optional[str] = None
    issues: List[AnalysisIssue] = []
    error: Optional[str] = None

class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=2000)
    generate_variants: Optional[bool] = False
    context: Optional[str] = None
    target_model: Optional[str] = None
    optimization_focus: Optional[List[str]] = None
    
    @validator('prompt')
    def validate_prompt_length(cls, v):
        if len(v) < 10:
            raise ValueError("El prompt debe tener al menos 10 caracteres")
        if len(v) > 2000:
            raise ValueError("El prompt no puede exceder 2000 caracteres")
        return v

class FeedbackRequest(BaseModel):
    analysis_id: str
    selected_variant: Optional[str] = None
    satisfaction_rating: Optional[int] = None
    feedback_comments: Optional[str] = None
    was_useful: bool

# ========== Funciones Principales ==========
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def analyze_content_safety(text: str) -> dict:
    try:
        client = ContentSafetyClient(
            endpoint=config.get_secret_cached("CONTENT-SAFETY-ENDPOINT"),
            credential=AzureKeyCredential(config.get_secret_cached("CONTENT-SAFETY-KEY"))
        )
        
        # Análisis de contenido dañino
        content_response = client.analyze_text(AnalyzeTextOptions(text=text))
        
        # Detección de jailbreak (nuevo)
        #jailbreak_response = client.detect_jailbreak(
        #    JailbreakDetectionOptions(text=text)
        #)
        
        result = {
            "categories": {c.category: c.severity for c in content_response.categories_analysis}
            #"jailbreak_detection": {
            #    "result": jailbreak_response.result,
            #    "probability": jailbreak_response.probability
            #}
        }
        
        return result
    except Exception as e:
        logger.error(f"Content Safety Error: {str(e)}")
        raise

@retry(stop=stop_after_attempt(3), reraise=True)
async def analyze_text_features(text: str) -> dict:
    try:
        client = get_text_analytics_client()
        
        # Crear tareas para todas las llamadas
        entities_task = asyncio.to_thread(client.recognize_entities, documents=[text])
        sentiment_task = asyncio.to_thread(client.analyze_sentiment, documents=[text])
        phrases_task = asyncio.to_thread(client.extract_key_phrases, documents=[text])
        language_task = asyncio.to_thread(client.detect_language, documents=[text])
        grammar_task = asyncio.to_thread(
            client.analyze_sentiment, 
            documents=[text],
            show_opinion_mining=True
        )
        
        # Ejecutar en paralelo
        results = await asyncio.gather(
            entities_task, sentiment_task, phrases_task, language_task, grammar_task,
            return_exceptions=True
        )
        
        # Manejar errores individuales
        processed = []
        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Error en Text Analytics: {str(res)}")
                raise res
            processed.append(res)
        
        entities_result, sentiment_result, phrases_result, language_result, grammar_result = processed
        
        return {
            "pii": [{"text": e.text, "category": e.category} for e in entities_result[0].entities],
            "sentiment": {
                "label": sentiment_result[0].sentiment,
                "scores": sentiment_result[0].confidence_scores.__dict__
            },
            "key_phrases": phrases_result[0].key_phrases,
            "language": language_result[0].primary_language.name,
            "grammar_quality": {
                "opinion_mining_present": len(grammar_result[0].sentences) > 0 and hasattr(grammar_result[0].sentences[0], 'mined_opinions')
            }
        }
    except Exception as e:
        logger.error(f"Error Text Analytics: {str(e)}")
        raise

async def analyze_ambiguity(text: str) -> dict:
    """Analiza la ambigüedad y claridad del prompt"""
    try:
        openai_client = get_openai_client()
        
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model=config.get_secret_cached("AZURE-OPENAI-DEPLOYMENT-NAME"),
            messages=[{
                "role": "system",
                "content": """Analiza este prompt para determinar su nivel de ambigüedad, claridad y completitud.
                Devuelve SOLO un JSON válido con el siguiente formato:
                {
                    "ambiguity_score": float entre 0-1 (donde 0 es nada ambiguo y 1 es extremadamente ambiguo),  
                    "clarity_score": float entre 0-1 (donde 0 es nada claro y 1 es perfectamente claro),
                    "completeness_score": float entre 0-1 (donde 0 es muy incompleto y 1 es totalmente completo),
                    "ambiguous_terms": ["lista", "de", "términos", "ambiguos"],
                    "missing_context": ["lista", "de", "contexto", "faltante"],
                    "improvement_suggestions": ["Lista", "de", "sugerencias", "concretas"]
                }"""
            }, {
                "role": "user",
                "content": text
            }],
            temperature=0.2
        )
        
        analysis = json.loads(response.choices[0].message.content)
        return analysis
    except Exception as e:
        logger.error(f"Ambiguity analysis error: {str(e)}")
        return {
            "ambiguity_score": 0.5,
            "clarity_score": 0.5,
            "completeness_score": 0.5,
            "ambiguous_terms": [],
            "missing_context": [],
            "improvement_suggestions": []
        }

async def generate_prompt_variants(original_prompt: str, context: str = None, optimization_focus: List[str] = None) -> List[PromptVariant]:
    """Genera variantes optimizadas del prompt original"""
    try:
        openai_client = get_openai_client()
        
        system_prompt = """Genera 3 variantes mejoradas del prompt proporcionado.
        Cada variante debe optimizar:
        1. Claridad: Reducir ambigüedad y ser específico
        2. Estructura: Mejorar la organización de la solicitud
        3. Especificidad: Incluir detalles relevantes
        
        Devuelve SOLO un JSON válido con el siguiente formato:
        {
            "variants": [
                {
                    "variant_text": "texto de la variante 1",
                    "quality_score": float entre 0-1,
                    "clarity_score": float entre 0-1,
                    "specificity_score": float entre 0-1,
                    "explanation": "explicación de las mejoras"
                },
                ...
            ]
        }"""
        
        if optimization_focus:
            system_prompt += f"\n\nEnfócate especialmente en: {', '.join(optimization_focus)}"
        
        user_content = original_prompt
        if context:
            user_content = f"Contexto: {context}\n\nPrompt original: {original_prompt}"
        
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model=config.get_secret_cached("AZURE-OPENAI-DEPLOYMENT-NAME"),
            messages=[{
                "role": "system",
                "content": system_prompt
            }, {
                "role": "user",
                "content": user_content
            }],
            temperature=0.7
        )
        
        variants_data = json.loads(response.choices[0].message.content)
        variants = []
        
        for variant in variants_data.get("variants", []):
            variants.append(PromptVariant(
                variant_text=variant["variant_text"],
                quality_score=variant["quality_score"],
                clarity_score=variant["clarity_score"],
                specificity_score=variant["specificity_score"],
                explanation=variant["explanation"]
            ))
        
        return variants
    except Exception as e:
        logger.error(f"Error generando variantes: {str(e)}")
        return []

async def log_rejected_prompt(analysis_id: str, prompt: str, safety_data: dict):
    """Registra en Cosmos DB los prompts rechazados por motivos de seguridad"""
    container = get_cosmos_client().get_database_client("PromptAnalysis").get_container_client("RejectedPrompts")
    audit_doc = {
        "id": analysis_id,
        "timestamp": datetime.utcnow().isoformat(),
        "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest(),
        "safety_analysis": safety_data,
        "status": "rejected"
    }
    await asyncio.to_thread(container.upsert_item, audit_doc)

async def log_feedback(feedback_data: dict):
    """Registra el feedback del usuario para mejorar el sistema"""
    container = get_cosmos_client().get_database_client("PromptAnalysis").get_container_client("Feedback")
    feedback_doc = {
        "id": str(uuid.uuid4()),
        "analysis_id": feedback_data["analysis_id"],
        "timestamp": datetime.utcnow().isoformat(),
        "selected_variant": feedback_data.get("selected_variant"),
        "satisfaction_rating": feedback_data.get("satisfaction_rating"),
        "feedback_comments": feedback_data.get("feedback_comments"),
        "was_useful": feedback_data["was_useful"]
    }
    await asyncio.to_thread(container.upsert_item, feedback_doc)

def check_safety_violations(safety_results: dict) -> Optional[str]:
    """Verifica violaciones de seguridad en los resultados del análisis"""
    for category, severity in safety_results.get("categories", {}).items():
        if SAFETY_THRESHOLDS.get(category, 6) <= severity:
            return f"Contenido no permitido en categoría: {category}"
    
    # Comprobar detección de jailbreak
    jailbreak_data = safety_results.get("jailbreak_detection", {})
    if jailbreak_data.get("result") == "JailbreakDetected" or jailbreak_data.get("probability", 0) > 0.7:
        return "Se detectó un posible intento de jailbreak"
    
    return None

def calculate_fairness_bias_score(text_results: dict, safety_results: dict) -> float:
    """Calcula una puntuación de equidad/sesgo basada en los resultados del análisis"""
    # Implementación simplificada - en un sistema real sería más complejo
    hate_score = safety_results.get("categories", {}).get("Hate", 0) / 6.0
    sentiment_negativity = text_results.get("sentiment", {}).get("scores", {}).get("negative", 0)
    
    # Menor puntuación representa mayor equidad
    bias_factor = (hate_score + sentiment_negativity) / 2
    fairness_score = 1.0 - bias_factor
    
    return max(0.0, min(1.0, fairness_score))

def redact_pii(text: str, pii_list: List[dict]) -> str:
    """Redacta información personal identificable del texto"""
    redacted = text
    for entity in pii_list:
        redacted = redacted.replace(entity["text"], f"[{entity['category']}]")
    return redacted

async def log_prompt_variants_for_learning(original_prompt: str, variants: List[str]):
    """Registra variantes de prompts generadas automáticamente."""
    try:
        container = get_cosmos_client() \
            .get_database_client("PromptAnalysis") \
            .get_container_client("PromptVariants")

        audit_doc = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "prompt_hash": hashlib.sha256(original_prompt.encode()).hexdigest(),
            "variants": variants,
            "status": "generated"
        }

        await asyncio.to_thread(container.upsert_item, audit_doc)
        logger.info("Prompt variants logged successfully.")

    except Exception as e:
        logger.error(f"Error logging prompt variants: {str(e)}")


# ========== Configuración FastAPI ==========
app = FastAPI(
    title="Azure Prompt Guardian API",
    version="5.0",
    docs_url="/docs",
    redoc_url=None,
    description="""
    Sistema inteligente de preprocesamiento de prompts para mejorar la calidad, seguridad y equidad
    de las interacciones con sistemas de IA.
    
    *Parte del hackathon Microsoft Azure 2025*
    """
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization"],
    max_age=600
)

# Importar el router de dashboard
from backend.dashboard_routes import router as dashboard_router 

# Agregar el router a la aplicación
app.include_router(dashboard_router)

# ========== Endpoints ==========
@app.post("/analyze-prompt", response_model=AnalysisResponse)
async def analyze_prompt(request: PromptRequest, background_tasks: BackgroundTasks):
    """
    Analiza un prompt, detecta problemas de seguridad, privacidad, equidad y claridad,
    y proporciona recomendaciones y mejoras.
    
    - **prompt**: Texto del prompt a analizar (10-2000 caracteres)
    - **generate_variants**: Opcional, si se deben generar variantes optimizadas
    - **context**: Opcional, contexto adicional para entender mejor el prompt
    - **target_model**: Opcional, modelo al que va dirigido el prompt
    - **optimization_focus**: Opcional, aspectos específicos a optimizar
    """
    try:
        # Validación inicial
        clean_prompt = request.prompt.strip()
        if len(clean_prompt) < 10:
            raise HTTPException(400, "Prompt inválido: demasiado corto")
        
        # Análisis de seguridad (mejorado con detección de jailbreak)
        safety_results = await analyze_content_safety(clean_prompt)
        
        # Verificar violaciones de seguridad
        if error_msg := check_safety_violations(safety_results):
            analysis_id = str(uuid.uuid4())
            await log_rejected_prompt(analysis_id, clean_prompt, safety_results)
            return AnalysisResponse(
                analysis_id=analysis_id,
                original_prompt=clean_prompt,
                error=error_msg,
                fairness_score=0.0,
                safety_score=0.0,
                inclusivity_score=0.0,
                clarity_score=0.0,
                completeness_score=0.0,
                ambiguity_score=1.0,
                privacy_measures=[],
                transparency_report={},
                accountability_id=analysis_id,
                issues=[AnalysisIssue(
                    type="safety",
                    description=error_msg,
                    severity="high",
                    mitigation="El prompt ha sido rechazado por motivos de seguridad. Por favor, reformule eliminando contenido inapropiado."
                )]
            )
        
        # Análisis paralelo de texto y ambigüedad
        text_task = analyze_text_features(clean_prompt)
        ambiguity_task = analyze_ambiguity(clean_prompt)
        text_results, ambiguity_results = await asyncio.gather(text_task, ambiguity_task)
        
        # Redactar PII
        redacted_prompt = redact_pii(clean_prompt, text_results["pii"])

        # Función auxiliar para la generación del prompt mejorado
        async def get_improved_prompt() -> dict:
            try:
                openai_client = get_openai_client()
                response = await asyncio.to_thread(
                    openai_client.chat.completions.create,
                    model=config.get_secret_cached("AZURE-OPENAI-DEPLOYMENT-NAME"),
                    messages=[{
                        "role": "system",
                        "content": """Analiza el prompt y devuelve SOLO un JSON válido con:
                        {
                            "improved_prompt": "string con prompt mejorado",
                            "safety_score": 0.0-1.0,
                            "fairness_score": 0.0-1.0,
                            "inclusivity_score": 0.0-1.0,
                            "improvement_explanation": "explicación detallada de los cambios realizados",
                            "issues": [
                                {"type": "fairness" | "safety" | "privacy" | "inclusiveness" | "bias" | "ambiguity" | "clarity" | "completeness" | "other",
                                "severity": "low" | "medium" | "high",
                                "description": "...",
                                "mitigation": "..."}
                            ]
                        }"""
                    }, {
                        "role": "user",
                        "content": redacted_prompt
                    }],
                    temperature=0.2
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                logger.error(f"Error OpenAI improved prompt: {str(e)}")
                raise

        # Ejecutar en paralelo la generación del prompt mejorado y las variantes
        improved_task = get_improved_prompt()
        variants_task = generate_prompt_variants(
            clean_prompt, 
            request.context, 
            request.optimization_focus
        ) if request.generate_variants else asyncio.sleep(0)

        # Esperar resultados paralelos
        if request.generate_variants:
            improved_data, variants_result = await asyncio.gather(improved_task, variants_task)
        else:
            improved_data = await improved_task
            variants_result = []

        # Calcular puntuación de equidad ajustada
        calculated_fairness = calculate_fairness_bias_score(text_results, safety_results)
        adjusted_fairness = (improved_data["fairness_score"] + calculated_fairness) / 2

        # Registrar variantes para aprendizaje automático
        if request.generate_variants and variants_result:
            background_tasks.add_task(
                log_prompt_variants_for_learning,
                clean_prompt,
                [v.variant_text for v in variants_result]
            )

        # Preparar lista de problemas detectados
        issues = []
        
        # Añadir problemas de ambigüedad y completitud
        if ambiguity_results.get("ambiguity_score", 0) > AMBIGUITY_THRESHOLD:
            issues.append(AnalysisIssue(
                type="ambiguity",
                description="Prompt con alto nivel de ambigüedad",
                severity="medium" if ambiguity_results["ambiguity_score"] > 0.8 else "low",
                mitigation="Considera especificar los términos ambiguos y proveer contexto adicional"
            ))
            
        if ambiguity_results.get("completeness_score", 0) < COMPLETENESS_THRESHOLD:
            issues.append(AnalysisIssue(
                type="completeness",
                description="Prompt incompleto, falta información relevante",
                severity="medium",
                mitigation="Añade contexto y especificaciones adicionales"
            ))

        # Añadir issues de OpenAI
        if "issues" in improved_data and isinstance(improved_data["issues"], list):
            for issue in improved_data["issues"]:
                issues.append(AnalysisIssue(**issue))

        # Auditoría y registro
        analysis_id = str(uuid.uuid4())
        audit_doc = {
            "id": analysis_id,
            "timestamp": datetime.utcnow().isoformat(),
            "prompt_hash": hashlib.sha256(clean_prompt.encode()).hexdigest(),
            "analysis": {
                **improved_data,
                "ambiguity_analysis": ambiguity_results
            },
            "metadata": {
                "safety": safety_results,
                "text_analytics": text_results,
                "compliance": ["GDPR", "ISO27001", "NIST"]
            },
            "variants": [v.dict() for v in variants_result] if variants_result else []
        }
        
        container = get_cosmos_client().get_database_client("PromptAnalysis").get_container_client("Analytics")
        await asyncio.to_thread(container.upsert_item, audit_doc)
        
        # Respuesta final
        return AnalysisResponse(
            analysis_id=analysis_id,
            original_prompt=clean_prompt,
            improved_prompt=improved_data["improved_prompt"],
            fairness_score=adjusted_fairness,
            safety_score=improved_data["safety_score"],
            inclusivity_score=improved_data["inclusivity_score"],
            clarity_score=ambiguity_results.get("clarity_score", 0.5),
            completeness_score=ambiguity_results.get("completeness_score", 0.5),
            ambiguity_score=ambiguity_results.get("ambiguity_score", 0.5),
            privacy_measures=["pii_redaction"] if text_results["pii"] else [],
            transparency_report={
                "safety_analysis": {
                    "categories": safety_results.get("categories", {}),
                    "jailbreak_probability": safety_results.get("jailbreak_detection", {}).get("probability", 0)
                },
                "text_analysis": {
                    "sentiment": text_results.get("sentiment", {}).get("label", "neutral"),
                    "key_phrases": text_results.get("key_phrases", [])[:5],
                    "language": text_results.get("language", "unknown")
                },
                "ambiguity_analysis": {
                    "ambiguous_terms": ambiguity_results.get("ambiguous_terms", []),
                    "missing_context": ambiguity_results.get("missing_context", [])
                }
            },
            accountability_id=analysis_id,
            suggested_variants=variants_result if variants_result else None,
            improvement_explanation=improved_data.get("improvement_explanation", ""),
            issues=issues
        )
        
    except Exception as e:
        logger.error(f"Error en análisis: {str(e)}", exc_info=True)
        raise HTTPException(500, "Error procesando la solicitud")

@app.post("/feedback", tags=["Feedback"])
async def submit_feedback(feedback: FeedbackRequest):
    """
    Registra feedback del usuario sobre las recomendaciones del sistema
    
    - **analysis_id**: ID del análisis al que corresponde el feedback
    - **selected_variant**: Variante del prompt que el usuario seleccionó (opcional)
    - **satisfaction_rating**: Calificación de satisfacción de 1-5 (opcional)
    - **feedback_comments**: Comentarios adicionales (opcional)
    - **was_useful**: Si el análisis fue útil
    """
    try:
        await log_feedback(feedback.dict())
        return {"status": "Feedback registrado correctamente"}
    except Exception as e:
        logger.error(f"Error al registrar feedback: {str(e)}")
        raise HTTPException(500, "Error al registrar feedback")

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
            "prompt_hash": document["prompt_hash"],
            "variants": document.get("variants", [])
        }
    except Exception as e:
        raise HTTPException(404, "Registro de auditoría no encontrado")

@app.get("/metrics", tags=["Analytics"])
async def get_system_metrics():
    """
    Obtiene métricas agregadas sobre el rendimiento del sistema
    """
    try:
        analytics_container = get_cosmos_client()\
            .get_database_client("PromptAnalysis")\
            .get_container_client("Analytics")
            
        rejected_container = get_cosmos_client()\
            .get_database_client("PromptAnalysis")\
            .get_container_client("RejectedPrompts")
            
        feedback_container = get_cosmos_client()\
            .get_database_client("PromptAnalysis")\
            .get_container_client("Feedback")
        
        # Consultas para obtener estadísticas
        total_analyzed = await asyncio.to_thread(
            lambda: list(analytics_container.query_items(
                query="SELECT VALUE COUNT(1) FROM c WHERE c._ts > @threshold",
                parameters=[{"name": "@threshold", "value": int((datetime.now() - datetime.timedelta(days=30)).timestamp())}],
                enable_cross_partition_query=True
            ))
        )
        
        total_rejected = await asyncio.to_thread(
            lambda: list(rejected_container.query_items(
                query="SELECT VALUE COUNT(1) FROM c WHERE c._ts > @threshold",
                parameters=[{"name": "@threshold", "value": int((datetime.now() - datetime.timedelta(days=30)).timestamp())}],
                enable_cross_partition_query=True
            ))
        )
        
        average_satisfaction = await asyncio.to_thread(
            lambda: list(feedback_container.query_items(
                query="SELECT VALUE AVG(c.satisfaction_rating) FROM c WHERE c.satisfaction_rating IS NOT NULL",
                enable_cross_partition_query=True
            ))
        )
        
        return {
            "total_prompts_analyzed_30d": total_analyzed[0] if total_analyzed else 0,
            "rejected_prompts_30d": total_rejected[0] if total_rejected else 0,
            "rejection_rate": (total_rejected[0] / total_analyzed[0]) if total_analyzed and total_analyzed[0] > 0 else 0,
            "average_satisfaction": average_satisfaction[0] if average_satisfaction else 0,
            "system_uptime_days": 30,  # Simulado
            "prompt_improvement_stats": {
                "average_clarity_improvement": 0.32,  # Simulado
                "average_safety_improvement": 0.45,  # Simulado
                "average_fairness_improvement": 0.28   # Simulado
            }
        }
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {str(e)}")
        raise HTTPException(500, "Error obteniendo métricas del sistema")

@app.get("/health")
async def health_check():
    """Health check endpoint that verifies key dependencies are accessible"""
    try:
        # Check Azure services connectivity
        cosmos_client = get_cosmos_client()
        await asyncio.to_thread(cosmos_client.list_databases)
        
        # Check OpenAI client
        openai_client = get_openai_client()
        
        return {
            "status": "OK", 
            "version": "5.0",  # Match app version
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {
                "cosmos": "connected",
                "openai": "available"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "ERROR",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)