from pydantic import BaseModel
from typing import List, Optional

class CategoryMetric(BaseModel):
    category: str
    count: int

class DashboardMetrics(BaseModel):
    totalPrompts: int
    totalIssuesDetected: int
    avgSafetyScore: float
    avgClarityScore: float
    promptsLastWeek: int
    promptsLastMonth: int
    percentChangeWeek: float
    percentChangeMonth: float
    topCategories: List[CategoryMetric]

class DailyMetric(BaseModel):
    date: str
    count: int
    avgSafetyScore: Optional[float] = None
    avgClarityScore: Optional[float] = None
    
# Modelo para el volumen de prompts (fecha y count)
class VolumeMetric(BaseModel):
    date: str
    count: int

# Modelo para las puntuaciones de seguridad y claridad
class SafetyMetric(BaseModel):
    date: str
    avgSafetyScore: Optional[float] = None
    avgClarityScore: Optional[float] = None

class SentimentMetric(BaseModel):
    date: str
    positive: float
    neutral: float
    negative: float

class ContentSafetyMetric(BaseModel):
    date: str
    hate: float
    selfHarm: float
    sexual: float
    violence: float

class IssueMetric(BaseModel):
    type: str
    count: int
    severity: str

class HistoricalData(BaseModel):
    promptVolume: List[VolumeMetric]
    safetyScores: List[SafetyMetric]
    sentimentTrend: List[SentimentMetric]
    contentSafetyTrend: List[ContentSafetyMetric]
    topIssues: List[IssueMetric]
