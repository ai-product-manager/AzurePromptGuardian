import axios from "axios"
import { v4 as uuidv4 } from 'uuid';
import type {
  AnalysisResponse,
  PromptRequest,
  DashboardMetrics,
  HistoricalData,
  AuditTrail,
  IssueMetric,
  CategoryMetric,
  RejectedPrompt,
  FeedbackRequest,
} from "../types"

const API_URL = "/api"

// Actualicemos la función analyzePrompt en el servicio API para aceptar los parámetros adicionales

export const analyzePrompt = async (
  prompt: string,
  options?: {
    generate_variants?: boolean
    context?: string
    target_model?: string
    optimization_focus?: string[]
  },
): Promise<AnalysisResponse> => {
  try {
    const requestPayload: PromptRequest = {
      prompt,
      generate_variants: options?.generate_variants || false,
      context: options?.context,
      target_model: options?.target_model,
      optimization_focus: options?.optimization_focus
    };

    console.debug("[API] Request payload:", JSON.stringify(requestPayload, null, 2));
    console.log(`[API] Sending POST to: ${API_URL}/analyze-prompt`);

    const startTime = performance.now();
    
    const response = await axios.post<AnalysisResponse>(
      `${API_URL}/analyze-prompt`,
      requestPayload,
      {
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': uuidv4() // Agregar ID único para tracking
        },
        timeout: 30000, // 30 segundos timeout
        validateStatus: (status) => status >= 200 && status < 500 // Considerar 4xx como respuesta válida
      }
    );

    const duration = performance.now() - startTime;
    console.log(`[API] Response received in ${duration.toFixed(2)}ms`);
    console.debug("[API] Full response:", response);

    if (response.status >= 400) {
      console.error(`[API Error] HTTP ${response.status}: ${response.statusText}`);
      console.error("Error details:", response.data);
      throw new Error(`HTTP Error ${response.status}: ${response.data?.error || response.statusText}`);
    }

    return response.data;
  } catch (error) {
    console.error("[API Critical Error] Full error object:", error);
    
    if (axios.isAxiosError(error)) {
      console.error("[API Axios Error Details]:");
      console.error("Request config:", error.config);
      console.error("Response data:", error.response?.data);
      console.error("Response status:", error.response?.status);
      console.error("Response headers:", error.response?.headers);
      
      let errorMessage = "Error desconocido en la comunicación con el servidor";
      
      if (!error.response) {
        errorMessage = "No se pudo conectar al servidor. Verifica tu conexión a internet.";
      } else if (error.response.status === 405) {
        errorMessage = `Método no permitido (405). Verifica: 
          1. Si el endpoint existe (${error.config?.url})
          2. Si el método HTTP es correcto (POST)
          3. Configuración CORS del servidor`;
      }

      throw new Error(`Error del servidor: ${errorMessage}`);
    }

    if (error instanceof Error) {
      throw new Error(`Error en la solicitud: ${error.message}`);
    }

    throw new Error("Error desconocido al procesar la solicitud");
  }
};

export const getAuditTrail = async (analysisId: string): Promise<AuditTrail> => {
  const response = await axios.get<AuditTrail>(`${API_URL}/audit/${analysisId}`)
  return response.data
}

export const submitFeedback = async (feedback: FeedbackRequest): Promise<void> => {
  await axios.post(`${API_URL}/feedback`, feedback)
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

