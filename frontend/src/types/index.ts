export type Severity = 'low' | 'medium' | 'high';

export interface Issue {
  type: string;
  description: string;
  severity: Severity;
}

export interface Analysis {
  issues: Issue[];
  improvements: string[];
  safetyScore: number;
  clarityScore: number;
}

export interface AnalysisResponse {
  improvedPrompt: string;
  analysis: Analysis;
}

export interface PromptRequest {
  prompt: string;
}