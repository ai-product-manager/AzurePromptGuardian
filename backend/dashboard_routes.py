from fastapi import APIRouter, Query, HTTPException
from typing import List
from datetime import datetime, timedelta
from backend.models import *
from backend.database import get_analytics_container, get_rejected_container
import logging
from collections import defaultdict

router = APIRouter(prefix="/dashboard")
logger = logging.getLogger(__name__)

async def execute_query(query: str, params: list = None, container_name: str = "analytics"):
    try:
        container = get_analytics_container() if container_name == "analytics" else get_rejected_container()
        return list(container.query_items(
            query=query,
            parameters=params or [],
            enable_cross_partition_query=True
        ))
    except Exception as e:
        logger.error(f"Cosmos DB Error: {str(e)}")
        raise HTTPException(500, "Database operation failed")

@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics():
    try:
        total_query = "SELECT VALUE COUNT(1) FROM c"
        total_prompts = (await execute_query(total_query))[0] or 0

        async def get_avg(field: str):
            result = (await execute_query(f"SELECT VALUE AVG(c.analysis.{field}) FROM c"))[0]
            return round(float(result or 0), 2)

        avg_safety = await get_avg("safety_score")
        avg_fairness = await get_avg("fairness_score")
        avg_inclusivity = await get_avg("inclusivity_score")

        async def get_count(days: int):
            return (await execute_query(
                "SELECT VALUE COUNT(1) FROM c WHERE c.timestamp >= @startDate",
                [{"name": "@startDate", "value": (datetime.utcnow() - timedelta(days=days)).isoformat()}]
            ))[0] or 0

        week_count = await get_count(7)
        month_count = await get_count(30)

        total_issues = (await execute_query("SELECT VALUE SUM(ARRAY_LENGTH(c.analysis.issues)) FROM c"))[0] or 0

        category_counts = defaultdict(int)
        for item in await execute_query("SELECT c.metadata.text_analytics.key_phrases FROM c"):
            if item.get("key_phrases"):
                category_counts[item["key_phrases"][0]] += 1

        return DashboardMetrics(
            totalPrompts=total_prompts,
            totalIssuesDetected=total_issues,
            avgSafetyScore=avg_safety,
            avgFairnessScore=avg_fairness,
            avgInclusivityScore=avg_inclusivity,
            promptsLastWeek=week_count,
            promptsLastMonth=month_count,
            percentChangeWeek=0.0,
            percentChangeMonth=0.0,
            topCategories=[CategoryMetric(category=k, count=v) for k, v in 
                          sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:6]]
        )
    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        raise HTTPException(500, "Error generating metrics")

def safe_aggregate(data: List[dict], fields: List[str]) -> List[dict]:
    grouped = defaultdict(lambda: {f: [] for f in fields})
    for item in data:
        date = item.get("date", "")
        for field in fields:
            value = item.get(field, 0.0)
            if isinstance(value, (int, float)):
                grouped[date][field].append(float(value))
    return [
        {
            "date": date,
            **{field: round(sum(values)/len(values), 2) if values else 0.0 for field, values in fields_data.items()}
        }
        for date, fields_data in grouped.items()
    ]

@router.get("/historical", response_model=HistoricalData)
async def get_historical_data(period: str = Query("week")):
    try:
        days = {"week": 7, "month": 30, "quarter": 90, "year": 365}.get(period, 7)
        all_data = await execute_query("SELECT * FROM c")
        
        date_set = set()
        base_data = []
        sentiment_data = []
        safety_data = []
        issue_counts = defaultdict(int)

        for doc in all_data:
            try:
                date = doc["timestamp"][:10]
                date_set.add(date)
                
                analysis = doc.get("analysis", {})
                metadata = doc.get("metadata", {})
                text_analytics = metadata.get("text_analytics", {})
                safety = metadata.get("safety", {})

                base_data.append({
                    "date": date,
                    "safety": analysis.get("safety_score", 0.0),
                    "fairness": analysis.get("fairness_score", 0.0),
                    "inclusivity": analysis.get("inclusivity_score", 0.0)
                })

                sentiment = text_analytics.get("sentiment", {}).get("scores", {})
                sentiment_data.append({
                    "date": date,
                    "positive": sentiment.get("positive", 0.0),
                    "neutral": sentiment.get("neutral", 0.0),
                    "negative": sentiment.get("negative", 0.0)
                })

                safety_data.append({
                    "date": date,
                    "hate": safety.get("Hate", 0.0),
                    "selfHarm": safety.get("SelfHarm", 0.0),
                    "sexual": safety.get("Sexual", 0.0),
                    "violence": safety.get("Violence", 0.0)
                })

                for issue in analysis.get("issues", []):
                    key = (issue.get("type", "unknown"), issue.get("severity", "medium"))
                    issue_counts[key] += 1
            except KeyError as e:
                logger.warning(f"Documento incompleto: {str(e)}")

        processed_volume = [
            {"date": date, "count": sum(1 for d in base_data if d["date"] == date)}
            for date in sorted(date_set)
        ]

        return HistoricalData(
            promptVolume=processed_volume,
            scoresTrend=safe_aggregate(base_data, ["safety", "fairness", "inclusivity"]),
            sentimentTrend=safe_aggregate(sentiment_data, ["positive", "neutral", "negative"]),
            contentSafetyTrend=safe_aggregate(safety_data, ["hate", "selfHarm", "sexual", "violence"]),
            topIssues=[
                IssueMetric(type=k[0], severity=k[1], count=v)
                for k, v in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
        )
    except Exception as e:
        logger.error(f"Historical data error: {str(e)}")
        raise HTTPException(500, "Error generating historical data")

@router.get("/rejected-prompts", response_model=List[dict])
async def get_rejected_prompts(limit: int = Query(10)):
    try:
        results = await execute_query(
            "SELECT TOP @limit * FROM c WHERE c.status = 'rejected'",
            [{"name": "@limit", "value": limit}],
            "rejected"
        )
        return [{
            "id": item["id"],
            "timestamp": item["timestamp"],
            "reason": "Violación de políticas de seguridad",
            "safety_analysis": item.get("safety_analysis", {})
        } for item in results]
    except Exception as e:
        logger.error(f"Rejected prompts error: {str(e)}")
        raise HTTPException(500, "Error retrieving rejected prompts")