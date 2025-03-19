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

export interface ContentSafety {
  hate_severity: number
  self_harm_severity: number
  sexual_severity: number
  violence_severity: number
}

export interface AnalysisIssue {
  type:
    | "fairness"
    | "safety"
    | "privacy"
    | "inclusiveness"
    | "bias"
    | "ambiguity"
    | "clarity"
    | "completeness"
    | "other"
  description: string
  severity: Severity
  mitigation: string
}

export interface PromptVariant {
  variant_text: string
  quality_score: number
  clarity_score: number
  specificity_score: number
  explanation: string
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
  original_prompt?: string
  improved_prompt: string | null
  fairness_score: number
  safety_score: number
  inclusivity_score: number
  clarity_score: number
  completeness_score: number
  ambiguity_score: number
  privacy_measures: string[]
  transparency_report: {
    safety_analysis: {
      categories: Record<string, number>
    }
    text_analysis: {
      sentiment: string
      key_phrases: string[]
      language: string
    }
    ambiguity_analysis: {
      ambiguous_terms: string[]
      missing_context: string[]
    }
  }
  accountability_id: string
  suggested_variants?: PromptVariant[]
  improvement_explanation?: string
  issues: AnalysisIssue[]
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

export interface FeedbackRequest {
  analysis_id: string
  selected_variant?: string
  satisfaction_rating?: number
  feedback_comments?: string
  was_useful: boolean
}

export type TimePeriod = "week" | "month" | "quarter" | "year"

export interface PromptRequest {
  prompt: string
  generate_variants?: boolean
  context?: string
  target_model?: string
  optimization_focus?: string[]
}

