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
                {{ (metrics.totalIssuesDetected / metrics.totalPrompts).toFixed(2) }} promedio por prompt
              </span>
            </div>
          </div>
  
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Puntuación de Seguridad</p>
                <h3 class="text-2xl font-bold">{{ metrics.avgSafetyScore.toFixed(1) }}/10</h3>
              </div>
              <div class="p-3 bg-green-100 dark:bg-green-900/30 rounded-full">
                <ShieldIcon class="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
            <div class="mt-2">
              <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  class="bg-green-500 h-2 rounded-full" 
                  :style="`width: ${metrics.avgSafetyScore * 10}%`"
                ></div>
              </div>
            </div>
          </div>
  
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Puntuación de Claridad</p>
                <h3 class="text-2xl font-bold">{{ metrics.avgClarityScore.toFixed(1) }}/10</h3>
              </div>
              <div class="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-full">
                <CheckCircleIcon class="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
            <div class="mt-2">
              <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  class="bg-purple-500 h-2 rounded-full" 
                  :style="`width: ${metrics.avgClarityScore * 10}%`"
                ></div>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Charts Row 1 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <!-- Prompt Volume Chart -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
            <h3 class="text-lg font-semibold mb-4">Volumen de Prompts</h3>
            <PromptVolumeChart :data="historicalData.promptVolume" />
          </div>
  
          <!-- Safety Score Chart -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
            <h3 class="text-lg font-semibold mb-4">Puntuaciones de Seguridad</h3>
            <SafetyScoreChart :data="historicalData.safetyScores" />
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
            <h3 class="text-lg font-semibold mb-4">Categorías de Contenido</h3>
            <ContentCategoryChart :data="historicalData.contentSafetyTrend" />
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
                    {{ ((category.count / metrics.totalPrompts) * 100).toFixed(1) }}%
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
  import { ref, onMounted } from 'vue';
  import { ShieldIcon, CheckCircleIcon, AlertCircleIcon, MessageSquareIcon } from 'lucide-vue-next';
  import { getDashboardMetrics, getHistoricalData } from '@/services/api';
  import type { DashboardMetrics, HistoricalData, TimePeriod } from '@/types';
  import PromptVolumeChart from './charts/PromptVolumeChart.vue';
  import SafetyScoreChart from './charts/SafetyScoreChart.vue';
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
  
  const loadData = async () => {
    isLoading.value = true;
    try {
      // En un entorno real, estas llamadas obtendrían datos de la API
      // Para esta demo, usaremos datos simulados
      metrics.value = await getDashboardMetrics();
      historicalData.value = await getHistoricalData(selectedPeriod.value);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      isLoading.value = false;
    }
  };
  
  onMounted(() => {
    loadData();
  });
  </script>