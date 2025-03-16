import axios from 'axios'
import type { AnalysisResponse, PromptRequest, DashboardMetrics, HistoricalData } from '../types'

const API_URL = '/api'

export const analyzePrompt = async (prompt: string): Promise<AnalysisResponse> => {
  const response = await axios.post<AnalysisResponse>(`${API_URL}/analyze-prompt`, {
    prompt
  } as PromptRequest)
  return response.data
}

export const getDashboardMetrics = async (): Promise<DashboardMetrics> => {
  const response = await axios.get<DashboardMetrics>(`${API_URL}/dashboard/metrics`)
  return response.data
}

export const getHistoricalData = async (period: string = 'week'): Promise<HistoricalData> => {
  const response = await axios.get<HistoricalData>(`${API_URL}/dashboard/historical?period=${period}`)
  return response.data
}

export const getTopIssues = async (limit: number = 5): Promise<{ type: string; count: number }[]> => {
  const response = await axios.get<{ type: string; count: number }[]>(`${API_URL}/dashboard/top-issues?limit=${limit}`)
  return response.data
}

export const getContentCategories = async (): Promise<{ category: string; count: number }[]> => {
  const response = await axios.get<{ category: string; count: number }[]>(`${API_URL}/dashboard/content-categories`)
  return response.data
}