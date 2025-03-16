import logging

from fastapi import APIRouter, Query, HTTPException
from typing import List
from datetime import datetime, timedelta
from models import *
from database import get_cosmos_container

router = APIRouter(prefix="/dashboard")
container = get_cosmos_container()

def calculate_percent_change(current: int, previous: int) -> float:
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 1)

async def execute_query(query: str, params: list = None):
    try:
        results = list(container.query_items(
            query=query,
            parameters=params or [],
            enable_cross_partition_query=True
        ))
        logging.info(f"Consulta ejecutada: {query}")
        logging.info(f"Parámetros: {params}")
        logging.info(f"Resultados: {results}")
        return results
    except Exception as e:
        logging.exception("Error ejecutando la consulta en CosmosDB")
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics():
    try:
        # 1. Total de prompts
        total_query = "SELECT VALUE COUNT(1) FROM c"
        total_result = await execute_query(total_query)
        total_prompts = total_result[0] if total_result else 0

        # 2. Promedio de safetyScore (consulta separada)
        avg_safety_query = """
        SELECT VALUE AVG(c.openai_analysis.safetyScore)
        FROM c
        """
        safety_data = await execute_query(avg_safety_query)
        avg_safety = safety_data[0] if safety_data else 0

        # 3. Promedio de clarityScore (consulta separada)
        avg_clarity_query = """
        SELECT VALUE AVG(c.openai_analysis.clarityScore)
        FROM c
        """
        clarity_data = await execute_query(avg_clarity_query)
        avg_clarity = clarity_data[0] if clarity_data else 0

        # 4. Conteos temporales (semana y mes)
        now = datetime.utcnow()

        week_query = """
        SELECT VALUE COUNT(1)
        FROM c
        WHERE c.timestamp >= @startDate
        """
        week_params = [{"name": "@startDate", "value": (now - timedelta(days=7)).isoformat()}]
        week_data = await execute_query(week_query, week_params)
        week_count = week_data[0] if week_data else 0

        month_params = [{"name": "@startDate", "value": (now - timedelta(days=30)).isoformat()}]
        month_data = await execute_query(week_query, month_params)
        month_count = month_data[0] if month_data else 0

        # 5. Issues totales
        issues_query = "SELECT VALUE SUM(ARRAY_LENGTH(c.openai_analysis.issues)) FROM c"
        issues_data = await execute_query(issues_query)
        total_issues = issues_data[0] if issues_data else 0

        # 6. Categorías principales
        # Usamos una subconsulta con SELECT VALUE para evitar composiciones de agregados
        category_query = """
        SELECT VALUE g
        FROM (
            SELECT 
                c.azure_metrics.text_analytics.key_phrases[0] AS category,
                COUNT(1) AS count
            FROM c
            WHERE ARRAY_LENGTH(c.azure_metrics.text_analytics.key_phrases) > 0
            GROUP BY c.azure_metrics.text_analytics.key_phrases[0]
        ) g
        """
        cat_data = await execute_query(category_query)
        # Ordenamos y tomamos los 6 principales en Python
        cat_sorted = sorted(cat_data, key=lambda x: x["count"], reverse=True)
        cat_top_6 = cat_sorted[:6]

        # 7. Construir la respuesta final
        return DashboardMetrics(
            totalPrompts=total_prompts,
            totalIssuesDetected=total_issues,
            avgSafetyScore=round(avg_safety, 1),
            avgClarityScore=round(avg_clarity, 1),
            promptsLastWeek=week_count,
            promptsLastMonth=month_count,
            percentChangeWeek=0.0,   # Lógica histórica opcional
            percentChangeMonth=0.0,  # Lógica histórica opcional
            topCategories=[CategoryMetric(**c) for c in cat_top_6],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/historical", response_model=HistoricalData)
async def get_historical_data(period: str = Query("week")):
    days = {"week": 7, "month": 30, "quarter": 90, "year": 365}.get(period, 7)
    start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

    try:
        # 1. Volumen de prompts
        volume_query = """
        SELECT VALUE {
            "date": g.date,
            "count": g.count
        }
        FROM (
            SELECT 
                SUBSTRING(c.timestamp, 0, 10) AS date,
                COUNT(1) AS count
            FROM c
            WHERE c.timestamp >= @startDate
            GROUP BY SUBSTRING(c.timestamp, 0, 10)
        ) g
        """
        volume_data = await execute_query(volume_query, [{"name": "@startDate", "value": start_date}])
        
        # 2. Puntajes de seguridad y claridad
        safety_query = """
        SELECT VALUE {
            "date": g.date,
            "avgSafetyScore": g.avgSafetyScore,
            "avgClarityScore": g.avgClarityScore
        }
        FROM (
            SELECT 
                SUBSTRING(c.timestamp, 0, 10) AS date,
                AVG(c.openai_analysis.safetyScore) AS avgSafetyScore,
                AVG(c.openai_analysis.clarityScore) AS avgClarityScore
            FROM c
            GROUP BY SUBSTRING(c.timestamp, 0, 10)
        ) g
        """
        safety_data = await execute_query(safety_query)

        # 3. Tendencias de sentimiento
        sentiment_query = """
        SELECT VALUE {
            "date": g.date,
            "positive": g.positive,
            "neutral": g.neutral,
            "negative": g.negative
        }
        FROM (
            SELECT
                SUBSTRING(c.timestamp, 0, 10) AS date,
                AVG(c.azure_metrics.text_analytics.sentiment.score.positive) AS positive,
                AVG(c.azure_metrics.text_analytics.sentiment.score.neutral) AS neutral,
                AVG(c.azure_metrics.text_analytics.sentiment.score.negative) AS negative
            FROM c
            GROUP BY SUBSTRING(c.timestamp, 0, 10)
        ) g
        """
        sentiment_data = await execute_query(sentiment_query)

        # 4. Tendencias de seguridad de contenido
        safety_trend_query = """
        SELECT VALUE {
            "date": g.date,
            "hate": g.hate,
            "selfHarm": g.selfHarm,
            "sexual": g.sexual,
            "violence": g.violence
        }
        FROM (
            SELECT
                SUBSTRING(c.timestamp, 0, 10) AS date,
                AVG(c.azure_metrics.content_safety.hate_severity) AS hate,
                AVG(c.azure_metrics.content_safety.self_harm_severity) AS selfHarm,
                AVG(c.azure_metrics.content_safety.sexual_severity) AS sexual,
                AVG(c.azure_metrics.content_safety.violence_severity) AS violence
            FROM c
            GROUP BY SUBSTRING(c.timestamp, 0, 10)
        ) g
        """
        safety_trend_data = await execute_query(safety_trend_query)

        # 5. Issues principales (top issues)
        issues_query = """
        SELECT TOP 10 VALUE g
        FROM (
            SELECT 
                i.type AS type,
                i.severity AS severity,
                COUNT(1) AS count
            FROM c
            JOIN i IN c.openai_analysis.issues
            GROUP BY i.type, i.severity
        ) g
        """
        issues_data = await execute_query(issues_query)

        return HistoricalData(
            promptVolume=[VolumeMetric(**d) for d in volume_data],
            safetyScores=[SafetyMetric(**d) for d in safety_data],
            sentimentTrend=[SentimentMetric(**s) for s in sentiment_data],
            contentSafetyTrend=[ContentSafetyMetric(**c) for c in safety_trend_data],
            topIssues=[IssueMetric(**i) for i in issues_data],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/top-issues", response_model=List[IssueMetric])
async def get_top_issues(limit: int = Query(5, ge=1, le=20)):
    try:
        query = """
        SELECT TOP @limit VALUE g
        FROM (
            SELECT 
                i.type AS type, 
                i.severity AS severity, 
                COUNT(1) AS count
            FROM c
            JOIN i IN c.openai_analysis.issues
            GROUP BY i.type, i.severity
        ) g
        """
        params = [{"name": "@limit", "value": limit}]
        results = await execute_query(query, params)
        results_sorted = sorted(results, key=lambda x: x["count"], reverse=True)
        return [IssueMetric(**item) for item in results_sorted]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content-categories", response_model=List[CategoryMetric])
async def get_content_categories():
    try:
        query = """
        SELECT TOP 6
            c.azure_metrics.text_analytics.key_phrases[0] AS category,
            COUNT(1) AS count
        FROM c
        WHERE ARRAY_LENGTH(c.azure_metrics.text_analytics.key_phrases) > 0
        GROUP BY c.azure_metrics.text_analytics.key_phrases[0]
        """
        results = await execute_query(query)
        results_sorted = sorted(results, key=lambda x: x["count"], reverse=True)
        return [CategoryMetric(**item) for item in results_sorted]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
