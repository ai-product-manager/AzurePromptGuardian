from pydantic import BaseModel, Field
from typing import List

class CategoryMetric(BaseModel):
    category: str
    count: int

class DashboardMetrics(BaseModel):
    totalPrompts: int
    totalIssuesDetected: int
    avgSafetyScore: float
    avgFairnessScore: float
    avgInclusivityScore: float
    promptsLastWeek: int
    promptsLastMonth: int
    percentChangeWeek: float
    percentChangeMonth: float
    topCategories: List[CategoryMetric]

class VolumeMetric(BaseModel):
    date: str
    count: int

class ScoresMetric(BaseModel):
    date: str
    avg_safety_score: float = Field(..., alias="safety")
    avg_fairness_score: float = Field(..., alias="fairness")
    avg_inclusivity_score: float = Field(..., alias="inclusivity")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {float: lambda v: round(v, 2)}

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
    scoresTrend: List[ScoresMetric]
    sentimentTrend: List[SentimentMetric]
    contentSafetyTrend: List[ContentSafetyMetric]
    topIssues: List[IssueMetric]
