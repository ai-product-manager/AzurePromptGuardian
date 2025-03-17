// Tipos básicos
export type Severity = "low" | "medium" | "high"

export interface PII {
  text: string
  category: string
}

export interface SentimentScore {
  positive: number
  neutral: number
  negative: number
}

export interface Sentiment {
  label: string
  score: SentimentScore
}

export interface TextAnalytics {
  detected_pii: PII[]
  sentiment: Sentiment
  key_phrases: string[]
}

// Asegúrate de que la interfaz ContentSafety tenga los nombres de propiedades correctos:

export interface ContentSafety {
  hate_severity: number
  self_harm_severity: number
  sexual_severity: number
  violence_severity: number
}

export interface AnalysisIssue {
  type: "fairness" | "safety" | "privacy" | "inclusiveness" | "bias" | "other"
  description: string
  severity: Severity
  mitigation: string
}

export interface OpenAIAnalysis {
  safetyScore: number
  clarityScore: number
  issues: AnalysisIssue[]
  improvements: string[]
}

// Tipos para la respuesta de análisis
export interface AnalysisResponse {
  analysis_id: string
  improved_prompt: string | null
  fairness_score: number
  safety_score: number
  inclusivity_score: number
  privacy_measures: string[]
  transparency_report: {
    safety_analysis: ContentSafety
    text_analysis: TextAnalytics
  }
  accountability_id: string
  error?: string
}

// Tipos para el dashboard
export interface VolumeMetric {
  date: string
  count: number
}

export interface SafetyMetric {
  date: string
  avgSafetyScore: number
  avgClarityScore: number
}

export interface CategoryMetric {
  category: string
  count: number
}

export interface IssueMetric {
  type: string
  count: number
  severity: Severity
}

export interface SentimentMetric {
  date: string
  positive: number
  neutral: number
  negative: number
}

export interface ContentSafetyMetric {
  date: string
  hate: number
  selfHarm: number
  sexual: number
  violence: number
}

export interface DashboardMetrics {
  totalPrompts: number
  totalIssuesDetected: number
  avgSafetyScore: number
  avgClarityScore: number
  avgFairnessScore: number
  avgInclusivityScore: number
  promptsLastWeek: number
  promptsLastMonth: number
  percentChangeWeek: number
  percentChangeMonth: number
  topCategories: CategoryMetric[]
}

export interface HistoricalData {
  promptVolume: VolumeMetric[]
  safetyScores: SafetyMetric[]
  sentimentTrend: SentimentMetric[]
  contentSafetyTrend: ContentSafetyMetric[]
  topIssues: IssueMetric[]
}

export interface AuditTrail {
  analysis_id: string
  timestamp: string
  compliance: string[]
  safety_summary: ContentSafety
  text_analysis_summary: TextAnalytics
  prompt_hash: string
}

export interface RejectedPrompt {
  id: string
  timestamp: string
  prompt_hash: string
  safety_analysis: ContentSafety
  status: "rejected"
}

export type TimePeriod = "week" | "month" | "quarter" | "year"

export interface PromptRequest {
  prompt: string
}

