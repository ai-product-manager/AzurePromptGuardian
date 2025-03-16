export interface DailyMetric {
    date: string;
    count: number;
    avgSafetyScore?: number;
    avgClarityScore?: number;
  }
  
  export interface CategoryMetric {
    category: string;
    count: number;
  }
  
  export interface IssueMetric {
    type: string;
    count: number;
    severity: 'low' | 'medium' | 'high';
  }
  
  export interface SentimentMetric {
    date: string;
    positive: number;
    neutral: number;
    negative: number;
  }
  
  export interface ContentSafetyMetric {
    date: string;
    hate: number;
    selfHarm: number;
    sexual: number;
    violence: number;
  }
  
  export interface DashboardMetrics {
    totalPrompts: number;
    totalIssuesDetected: number;
    avgSafetyScore: number;
    avgClarityScore: number;
    promptsLastWeek: number;
    promptsLastMonth: number;
    percentChangeWeek: number;
    percentChangeMonth: number;
    topCategories: CategoryMetric[];
  }
  
  export interface HistoricalData {
    promptVolume: DailyMetric[];
    safetyScores: DailyMetric[];
    sentimentTrend: SentimentMetric[];
    contentSafetyTrend: ContentSafetyMetric[];
    topIssues: IssueMetric[];
  }
  
  export type TimePeriod = 'week' | 'month' | 'quarter' | 'year';