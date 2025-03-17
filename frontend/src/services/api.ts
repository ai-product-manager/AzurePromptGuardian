import axios from "axios"
import type {
  AnalysisResponse,
  PromptRequest,
  DashboardMetrics,
  HistoricalData,
  AuditTrail,
  IssueMetric,
  CategoryMetric,
  RejectedPrompt,
} from "../types"

const API_URL = "/api"

export const analyzePrompt = async (prompt: string): Promise<AnalysisResponse> => {
  const response = await axios.post<AnalysisResponse>(`${API_URL}/analyze-prompt`, {
    prompt,
  } as PromptRequest)
  return response.data
}

export const getAuditTrail = async (analysisId: string): Promise<AuditTrail> => {
  const response = await axios.get<AuditTrail>(`${API_URL}/audit/${analysisId}`)
  return response.data
}

// Funciones para el dashboard
export const getDashboardMetrics = async (): Promise<DashboardMetrics> => {
  const response = await axios.get<DashboardMetrics>(`${API_URL}/dashboard/metrics`)
  return response.data
}

export const getHistoricalData = async (period = "week"): Promise<HistoricalData> => {
  const response = await axios.get<HistoricalData>(`${API_URL}/dashboard/historical?period=${period}`)
  return response.data
}

export const getTopIssues = async (limit = 5): Promise<IssueMetric[]> => {
  const response = await axios.get<IssueMetric[]>(`${API_URL}/dashboard/top-issues?limit=${limit}`)
  return response.data
}

export const getContentCategories = async (): Promise<CategoryMetric[]> => {
  const response = await axios.get<CategoryMetric[]>(`${API_URL}/dashboard/content-categories`)
  return response.data
}

// Nuevas funciones para las características adicionales
export const getRejectedPrompts = async (limit = 10): Promise<RejectedPrompt[]> => {
  try {
    const response = await axios.get<RejectedPrompt[]>(`${API_URL}/dashboard/rejected-prompts?limit=${limit}`)
    return response.data
  } catch (error) {
    console.error("Error fetching rejected prompts:", error)
    // Devolver un array vacío en caso de error
    return []
  }
}

