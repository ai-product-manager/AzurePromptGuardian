export type Severity = 'low' | 'medium' | 'high';

export interface Issue {
  type: string;
  description: string;
  severity: Severity;
}

export interface OpenAIAnalysis {
  issues: Issue[];
  improvements: string[];
  safetyScore: number;
  clarityScore: number;
}

export interface PII {
  text: string;
  category: string;
}

export interface SentimentScore {
  positive: number;
  neutral: number;
  negative: number;
}

export interface Sentiment {
  score: SentimentScore;
  label: string;
}

export interface AzureSafety {
  hate_severity: number;
  self_harm_severity: number;
  sexual_severity: number;
  violence_severity: number;
}

export interface TextAnalytics {
  detected_pii: PII[];
  sentiment: Sentiment;
  key_phrases: string[];
}

export interface AnalysisResponse {
  improvedPrompt: string;
  openaiAnalysis: OpenAIAnalysis;
  azureSafety: AzureSafety;
  textAnalytics: TextAnalytics;
}

export interface PromptRequest {
  prompt: string;
}