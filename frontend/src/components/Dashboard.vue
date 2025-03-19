<template>
  <div>
    <!-- Period Selector -->
    <div class="mb-6 flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Dashboard de Analytics</h2>
      <div class="flex items-center space-x-2">
        <span class="text-sm text-gray-500 dark:text-gray-400">Periodo:</span>
        <select 
          v-model="selectedPeriod" 
          @change="loadData"
          class="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md text-sm px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="week">Última semana</option>
          <option value="month">Último mes</option>
          <option value="quarter">Último trimestre</option>
          <option value="year">Último año</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
    </div>

    <div v-else>
      <!-- Key Metrics -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Total de Prompts</p>
              <h3 class="text-2xl font-bold">{{ metrics.totalPrompts }}</h3>
            </div>
            <div class="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full">
              <MessageSquareIcon class="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          <div class="mt-2 flex items-center">
            <span 
              :class="metrics.percentChangeWeek >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'"
              class="text-sm font-medium"
            >
              {{ metrics.percentChangeWeek >= 0 ? '+' : '' }}{{ metrics.percentChangeWeek }}%
            </span>
            <span class="text-xs text-gray-500 dark:text-gray-400 ml-1">vs semana anterior</span>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Problemas Detectados</p>
              <h3 class="text-2xl font-bold">{{ metrics.totalIssuesDetected }}</h3>
            </div>
            <div class="p-3 bg-red-100 dark:bg-red-900/30 rounded-full">
              <AlertCircleIcon class="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
          </div>
          <div class="mt-2">
            <span class="text-xs text-gray-500 dark:text-gray-400">
              {{ metrics.totalIssuesDetected !== undefined && metrics.totalPrompts !== undefined ? 
    (metrics.totalIssuesDetected / Math.max(metrics.totalPrompts, 1)).toFixed(2) : '0.00' }} promedio por prompt
            </span>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Puntuación de Seguridad</p>
              <h3 class="text-2xl font-bold">{{ metrics.avgSafetyScore !== undefined ? metrics.avgSafetyScore.toFixed(1) : '0.0' }}/10</h3>
            </div>
            <div class="p-3 bg-green-100 dark:bg-green-900/30 rounded-full">
              <ShieldIcon class="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
          <div class="mt-2">
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                class="bg-green-500 h-2 rounded-full" 
                :style="`width: ${(metrics.avgSafetyScore / 10) * 100}%`"
              ></div>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Prompts Rechazados</p>
              <h3 class="text-2xl font-bold">{{ rejectedPrompts.length }}</h3>
            </div>
            <div class="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-full">
              <AlertTriangleIcon class="h-6 w-6 text-orange-600 dark:text-orange-400" />
            </div>
          </div>
          <div class="mt-2">
            <span class="text-xs text-gray-500 dark:text-gray-400">
              {{ rejectedPrompts.length !== undefined && metrics.totalPrompts !== undefined ? 
    ((rejectedPrompts.length / Math.max(metrics.totalPrompts + rejectedPrompts.length, 1)) * 100).toFixed(1) : '0.0' }}% de tasa de rechazo
            </span>
          </div>
        </div>
      </div>

      <!-- Responsible AI Metrics -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold">Equidad</h3>
            <div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-full">
              <ScaleIcon class="h-5 w-5 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          <div class="text-3xl font-bold mb-2">{{ metrics.avgFairnessScore !== undefined ? (metrics.avgFairnessScore * 10).toFixed(1) : '0.0' }}/10</div>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
            <div 
              class="bg-blue-500 h-2 rounded-full" 
              :style="`width: ${metrics.avgFairnessScore * 100}%`"
            ></div>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Evaluación de sesgos y discriminación en los prompts
          </p>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold">Inclusividad</h3>
            <div class="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-full">
              <UsersIcon class="h-5 w-5 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
          <div class="text-3xl font-bold mb-2">{{ metrics.avgInclusivityScore !== undefined ? (metrics.avgInclusivityScore * 10).toFixed(1) : '0.0' }}/10</div>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
            <div 
              class="bg-purple-500 h-2 rounded-full" 
              :style="`width: ${metrics.avgInclusivityScore * 100}%`"
            ></div>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Medición de lenguaje inclusivo y representación
          </p>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold">Privacidad</h3>
            <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-full">
              <LockIcon class="h-5 w-5 text-green-600 dark:text-green-400" />
            </div>
          </div>
          <div class="text-3xl font-bold mb-2">{{ piiDetectionRate !== undefined ? piiDetectionRate.toFixed(1) : '0.0' }}%</div>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
            <div 
              class="bg-green-500 h-2 rounded-full" 
              :style="`width: ${piiDetectionRate}%`"
            ></div>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Tasa de detección y redacción de información personal
          </p>
        </div>
      </div>

      <!-- Charts Row 1 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <!-- Prompt Volume Chart -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <h3 class="text-lg font-semibold mb-4">Volumen de Prompts</h3>
          <PromptVolumeChart :data="historicalData.promptVolume" />
        </div>

        <!-- Scores Chart -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <h3 class="text-lg font-semibold mb-4">Tendencia de Puntuaciones</h3>
          <ScoresTrendChart :data="historicalData.scoresTrend" />
        </div>
      </div>

      <!-- Charts Row 2 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <!-- Top Issues Chart -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <h3 class="text-lg font-semibold mb-4">Problemas Más Comunes</h3>
          <TopIssuesChart :data="historicalData.topIssues" />
        </div>

        <!-- Sentiment Trend Chart -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <h3 class="text-lg font-semibold mb-4">Tendencia de Sentimiento</h3>
          <SentimentTrendChart :data="historicalData.sentimentTrend" />
        </div>

        <!-- Content Safety Chart -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <h3 class="text-lg font-semibold mb-4">Categorías de Seguridad</h3>
          <ContentCategoryChart :data="historicalData.contentSafetyTrend" />
        </div>
      </div>

      <!-- Rejected Prompts Table -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4 mb-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">Prompts Rechazados</h3>
          <span class="text-sm text-gray-500 dark:text-gray-400">Últimos {{ rejectedPrompts.length }} rechazos</span>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  ID
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Timestamp
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Razón
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Severidad
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(prompt, i) in rejectedPrompts" :key="i">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900 dark:text-gray-100">
                  {{ prompt.id ? prompt.id.substring(0, 8) + '...' : 'ID-' + i }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ prompt.timestamp ? formatDate(prompt.timestamp) : 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ prompt.safety_analysis ? getHighestSeverityCategory(prompt.safety_analysis) : 'Desconocido' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    class="px-2 py-1 text-xs rounded-full"
                    :class="prompt.safety_analysis ? getSeverityClass(getHighestSeverity(prompt.safety_analysis)) : ''"
                  >
                    {{ prompt.safety_analysis ? getHighestSeverity(prompt.safety_analysis) : 'N/A' }}
                  </span>
                </td>
              </tr>
              <tr v-if="rejectedPrompts.length === 0">
                <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                  No hay prompts rechazados en este periodo
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Top Categories Table -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
        <h3 class="text-lg font-semibold mb-4">Categorías Principales</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Categoría
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Cantidad
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Porcentaje
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Distribución
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(category, i) in metrics.topCategories" :key="i">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                  {{ category.category }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ category.count }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ category.count !== undefined && metrics.totalPrompts !== undefined ? 
    ((category.count / metrics.totalPrompts) * 100).toFixed(1) : '0.0' }}%
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      class="bg-blue-500 h-2 rounded-full" 
                      :style="`width: ${(category.count / metrics.totalPrompts) * 100}%`"
                    ></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { 
  ShieldIcon, 
  AlertCircleIcon, 
  MessageSquareIcon,
  ScaleIcon,
  UsersIcon,
  LockIcon,
  AlertTriangleIcon
} from 'lucide-vue-next';
import { getDashboardMetrics, getHistoricalData, getRejectedPrompts } from '@/services/api';
import type { DashboardMetrics, HistoricalData, TimePeriod, RejectedPrompt, ContentSafety } from '@/types';
import PromptVolumeChart from './charts/PromptVolumeChart.vue';
import ScoresTrendChart from './charts/ScoresTrendChart.vue';
import TopIssuesChart from './charts/TopIssuesChart.vue';
import SentimentTrendChart from './charts/SentimentTrendChart.vue';
import ContentCategoryChart from './charts/ContentCategoryChart.vue';

const isLoading = ref<boolean>(true);
const selectedPeriod = ref<TimePeriod>('week');
const metrics = ref<DashboardMetrics>({
  totalPrompts: 0,
  totalIssuesDetected: 0,
  avgSafetyScore: 0,
  avgClarityScore: 0,
  avgFairnessScore: 0,  // Añade esta línea
  avgInclusivityScore: 0,  // Añade esta línea
  promptsLastWeek: 0,
  promptsLastMonth: 0,
  percentChangeWeek: 0,
  percentChangeMonth: 0,
  topCategories: []
});

const historicalData = ref<HistoricalData>({
  promptVolume: [],
  safetyScores: [],
  sentimentTrend: [],
  contentSafetyTrend: [],
  topIssues: []
});

const rejectedPrompts = ref<RejectedPrompt[]>([]);

// Valor simulado para la tasa de detección de PII
const piiDetectionRate = computed(() => {
  return 95.5; // En un entorno real, esto se calcularía a partir de datos reales
});

const loadData = async () => {
  isLoading.value = true;
  try {
    metrics.value = await getDashboardMetrics();
    historicalData.value = await getHistoricalData(selectedPeriod.value);
    rejectedPrompts.value = await getRejectedPrompts(10);
  } catch (error) {
    console.error('Error loading dashboard data:', error);
  } finally {
    isLoading.value = false;
  }
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

const getHighestSeverityCategory = (safety: ContentSafety): string => {
  const categories = [
    { name: 'Odio', value: safety.hate_severity },
    { name: 'Autolesión', value: safety.self_harm_severity },
    { name: 'Sexual', value: safety.sexual_severity },
    { name: 'Violencia', value: safety.violence_severity }
  ];
  
  categories.sort((a, b) => b.value - a.value);
  return categories[0].name;
};

const getHighestSeverity = (safety: ContentSafety): number => {
  return Math.max(
    safety.hate_severity || 0,
    safety.self_harm_severity || 0,
    safety.sexual_severity || 0,
    safety.violence_severity || 0
  );
};

const getSeverityClass = (severity: number): string => {
  if (severity >= 4) return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
  if (severity >= 2) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
  return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
};

onMounted(() => {
  loadData();
});
</script>