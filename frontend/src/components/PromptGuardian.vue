<template>
    <div class="container mx-auto py-8 max-w-4xl px-4">
      <div class="flex flex-col items-center text-center mb-8">
        <div class="flex items-center gap-2 mb-2">
          <ShieldIcon class="h-8 w-8 text-primary-500" />
          <h1 class="text-3xl font-bold">PromptGuardian</h1>
        </div>
        <p class="text-gray-600 dark:text-gray-400 max-w-2xl">
          Un sistema inteligente para mejorar y validar la seguridad, claridad y eficacia de los prompts enviados a sistemas de IA generativos.
        </p>
      </div>
  
      <div class="grid gap-8 md:grid-cols-2">
        <!-- Prompt Original Card -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
          <div class="p-4 border-b border-gray-200 dark:border-gray-700">
            <h2 class="text-lg font-semibold">Prompt Original</h2>
            <p class="text-sm text-gray-500 dark:text-gray-400">Ingrese el prompt que desea analizar y mejorar</p>
          </div>
          <div class="p-4">
            <textarea
              v-model="userPrompt"
              placeholder="Escriba su prompt aquí..."
              class="w-full min-h-[200px] p-3 border border-gray-300 dark:border-gray-600 rounded-md bg-transparent focus:outline-none focus:ring-2 focus:ring-primary-500"
            ></textarea>
          </div>
          <div class="p-4 border-t border-gray-200 dark:border-gray-700">
            <button 
              @click="analyzePrompt" 
              :disabled="isLoading || !userPrompt.trim()" 
              class="w-full py-2 px-4 bg-primary-500 text-white rounded-md hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <div v-if="isLoading" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analizando...
              </div>
              <span v-else>Analizar y Mejorar Prompt</span>
            </button>
          </div>
        </div>
  
        <!-- Results Card -->
        <div class="flex flex-col gap-4">
          <div v-if="processedPrompt">
            <!-- Tabs -->
            <div class="border-b border-gray-200 dark:border-gray-700">
              <div class="flex">
                <button 
                  @click="activeTab = 'improved'" 
                  :class="[
                    'py-2 px-4 text-sm font-medium border-b-2 focus:outline-none transition-colors',
                    activeTab === 'improved' 
                      ? 'border-primary-500 text-primary-500' 
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  Prompt Mejorado
                </button>
                <button 
                  @click="activeTab = 'analysis'" 
                  :class="[
                    'py-2 px-4 text-sm font-medium border-b-2 focus:outline-none transition-colors',
                    activeTab === 'analysis' 
                      ? 'border-primary-500 text-primary-500' 
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  Análisis
                </button>
              </div>
            </div>
  
            <!-- Improved Prompt Tab -->
            <div v-if="activeTab === 'improved'" class="mt-4">
              <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
                <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                  <h2 class="text-lg font-semibold flex items-center gap-2">
                    <CheckCircleIcon class="h-5 w-5 text-green-500" />
                    Prompt Optimizado
                  </h2>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Versión mejorada lista para usar</p>
                </div>
                <div class="p-4">
                  <div class="bg-gray-100 dark:bg-gray-900 p-4 rounded-md min-h-[200px] whitespace-pre-wrap">
                    {{ processedPrompt }}
                  </div>
                </div>
                <div class="p-4 border-t border-gray-200 dark:border-gray-700">
                  <button 
                    @click="copyToClipboard" 
                    class="w-full py-2 px-4 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
                  >
                    {{ copied ? 'Copiado!' : 'Copiar Prompt Mejorado' }}
                  </button>
                </div>
              </div>
            </div>
  
            <!-- Analysis Tab -->
            <div v-if="activeTab === 'analysis' && analysis" class="mt-4">
              <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
                <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                  <h2 class="text-lg font-semibold flex items-center gap-2">
                    <InfoIcon class="h-5 w-5 text-blue-500" />
                    Análisis Detallado
                  </h2>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Evaluación de seguridad y claridad</p>
                </div>
                <div class="p-4 space-y-4">
                  <!-- Scores -->
                  <div class="flex gap-4">
                    <div class="flex-1 bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center">
                      <div class="text-2xl font-bold">{{ analysis.safetyScore }}/10</div>
                      <div class="text-sm text-gray-500 dark:text-gray-400">Seguridad</div>
                    </div>
                    <div class="flex-1 bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center">
                      <div class="text-2xl font-bold">{{ analysis.clarityScore }}/10</div>
                      <div class="text-sm text-gray-500 dark:text-gray-400">Claridad</div>
                    </div>
                  </div>
                  
                  <!-- Issues -->
                  <div v-if="analysis.issues.length > 0" class="space-y-2">
                    <h3 class="text-sm font-medium">Problemas Detectados</h3>
                    <div 
                      v-for="(issue, i) in analysis.issues" 
                      :key="i" 
                      :class="[
                        'p-4 border rounded-md flex items-start gap-3',
                        issue.severity === 'high' ? 'border-red-300 bg-red-50 dark:bg-red-900/20 dark:border-red-800' :
                        issue.severity === 'medium' ? 'border-yellow-300 bg-yellow-50 dark:bg-yellow-900/20 dark:border-yellow-800' :
                        'border-gray-300 bg-gray-50 dark:bg-gray-900/50 dark:border-gray-700'
                      ]"
                    >
                      <AlertCircleIcon class="h-5 w-5 shrink-0 mt-0.5" :class="[
                        issue.severity === 'high' ? 'text-red-500' :
                        issue.severity === 'medium' ? 'text-yellow-500' :
                        'text-gray-500'
                      ]" />
                      <div>
                        <div class="flex items-center gap-2">
                          <span class="font-medium">{{ issue.type }}</span>
                          <span 
                            :class="[
                              'text-xs px-2 py-0.5 rounded-full',
                              issue.severity === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300' :
                              issue.severity === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300' :
                              'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                            ]"
                          >
                            {{ issue.severity }}
                          </span>
                        </div>
                        <p class="text-sm mt-1">{{ issue.description }}</p>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Improvements -->
                  <div v-if="analysis.improvements.length > 0" class="space-y-2">
                    <h3 class="text-sm font-medium">Mejoras Aplicadas</h3>
                    <ul class="space-y-1">
                      <li 
                        v-for="(improvement, i) in analysis.improvements" 
                        :key="i" 
                        class="text-sm flex items-start gap-2"
                      >
                        <CheckCircleIcon class="h-4 w-4 text-green-500 mt-0.5 shrink-0" />
                        <span>{{ improvement }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
  
          <!-- Empty State -->
          <div 
            v-else 
            class="h-full flex flex-col justify-center items-center p-8 text-center text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm"
          >
            <ShieldIcon class="h-12 w-12 mb-4 opacity-50" />
            <h3 class="text-lg font-medium mb-2">Esperando Prompt</h3>
            <p class="max-w-md">
              Ingrese un prompt en el panel izquierdo y haga clic en "Analizar y Mejorar Prompt" para recibir sugerencias y correcciones.
            </p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
  import axios from 'axios';
  import { ShieldIcon, CheckCircleIcon, InfoIcon, AlertCircleIcon } from 'lucide-vue-next';
  import type { Analysis, AnalysisResponse } from '@/types';
  
  const userPrompt = ref<string>('');
  const processedPrompt = ref<string>('');
  const isLoading = ref<boolean>(false);
  const activeTab = ref<'improved' | 'analysis'>('improved');
  const analysis = ref<Analysis | null>(null);
  const copied = ref<boolean>(false);
  
  const analyzePrompt = async (): Promise<void> => {
    if (!userPrompt.value.trim()) return;
    
    isLoading.value = true;
    
    try {
      const response = await axios.post<AnalysisResponse>('/api/analyze-prompt', {
        prompt: userPrompt.value
      });
      
      processedPrompt.value = response.data.improvedPrompt;
      analysis.value = response.data.analysis;
      activeTab.value = 'improved';
    } catch (error) {
      console.error("Error analyzing prompt:", error);
      alert("Ocurrió un error al analizar el prompt. Por favor, intente de nuevo.");
    } finally {
      isLoading.value = false;
    }
  };
  
  const copyToClipboard = (): void => {
    navigator.clipboard.writeText(processedPrompt.value);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  };
  </script>