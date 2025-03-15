<template>
    <div class="container mx-auto py-8 max-w-4xl px-4">
      <div class="flex flex-col items-center text-center mb-8">
        <div class="flex items-center gap-2 mb-2">
          <ShieldIcon class="h-8 w-8 text-primary-500" />
          <h1 class="text-3xl font-bold">PromptGuardian Pro</h1>
        </div>
        <p class="text-gray-600 dark:text-gray-400 max-w-2xl">
          Sistema avanzado para mejorar y validar la seguridad, claridad y eficacia de los prompts con análisis de Azure AI y OpenAI.
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
          <div v-if="analysisResult">
            <!-- Tabs -->
            <div class="border-b border-gray-200 dark:border-gray-700">
              <div class="flex flex-wrap">
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
                  @click="activeTab = 'openai'" 
                  :class="[
                    'py-2 px-4 text-sm font-medium border-b-2 focus:outline-none transition-colors',
                    activeTab === 'openai' 
                      ? 'border-primary-500 text-primary-500' 
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  Análisis OpenAI
                </button>
                <button 
                  @click="activeTab = 'azure'" 
                  :class="[
                    'py-2 px-4 text-sm font-medium border-b-2 focus:outline-none transition-colors',
                    activeTab === 'azure' 
                      ? 'border-primary-500 text-primary-500' 
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  Análisis Azure
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
                    {{ analysisResult.improvedPrompt }}
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
  
            <!-- OpenAI Analysis Tab -->
            <div v-if="activeTab === 'openai' && analysisResult.openaiAnalysis" class="mt-4">
              <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
                <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                  <h2 class="text-lg font-semibold flex items-center gap-2">
                    <InfoIcon class="h-5 w-5 text-blue-500" />
                    Análisis OpenAI
                  </h2>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Evaluación de seguridad y claridad</p>
                </div>
                <div class="p-4 space-y-4">
                  <!-- Scores -->
                  <div class="flex gap-4">
                    <div class="flex-1 bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center">
                      <div class="text-2xl font-bold">{{ analysisResult.openaiAnalysis.safetyScore }}/10</div>
                      <div class="text-sm text-gray-500 dark:text-gray-400">Seguridad</div>
                    </div>
                    <div class="flex-1 bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center">
                      <div class="text-2xl font-bold">{{ analysisResult.openaiAnalysis.clarityScore }}/10</div>
                      <div class="text-sm text-gray-500 dark:text-gray-400">Claridad</div>
                    </div>
                  </div>
                  
                  <!-- Issues -->
                  <div v-if="analysisResult.openaiAnalysis.issues.length > 0" class="space-y-2">
                    <h3 class="text-sm font-medium">Problemas Detectados</h3>
                    <div 
                      v-for="(issue, i) in analysisResult.openaiAnalysis.issues" 
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
                  <div v-if="analysisResult.openaiAnalysis.improvements.length > 0" class="space-y-2">
                    <h3 class="text-sm font-medium">Mejoras Aplicadas</h3>
                    <ul class="space-y-1">
                      <li 
                        v-for="(improvement, i) in analysisResult.openaiAnalysis.improvements" 
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
  
            <!-- Azure Analysis Tab -->
            <div v-if="activeTab === 'azure' && analysisResult.azureSafety && analysisResult.textAnalytics" class="mt-4">
              <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
                <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                  <h2 class="text-lg font-semibold flex items-center gap-2">
                    <ShieldIcon class="h-5 w-5 text-purple-500" />
                    Análisis Azure AI
                  </h2>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Evaluación de seguridad y análisis de texto</p>
                </div>
                
                <div class="p-4 space-y-6">
                  <!-- Content Safety -->
                  <div>
                    <h3 class="text-sm font-medium mb-3">Análisis de Seguridad de Contenido</h3>
                    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
                      <div 
                        class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center"
                        :class="getSeverityClass(analysisResult.azureSafety.hate_severity)"
                      >
                        <div class="text-xl font-bold">{{ analysisResult.azureSafety.hate_severity }}</div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">Odio</div>
                      </div>
                      <div 
                        class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center"
                        :class="getSeverityClass(analysisResult.azureSafety.self_harm_severity)"
                      >
                        <div class="text-xl font-bold">{{ analysisResult.azureSafety.self_harm_severity }}</div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">Autolesión</div>
                      </div>
                      <div 
                        class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center"
                        :class="getSeverityClass(analysisResult.azureSafety.sexual_severity)"
                      >
                        <div class="text-xl font-bold">{{ analysisResult.azureSafety.sexual_severity }}</div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">Sexual</div>
                      </div>
                      <div 
                        class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center"
                        :class="getSeverityClass(analysisResult.azureSafety.violence_severity)"
                      >
                        <div class="text-xl font-bold">{{ analysisResult.azureSafety.violence_severity }}</div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">Violencia</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Sentiment Analysis -->
                  <div>
                    <h3 class="text-sm font-medium mb-3">Análisis de Sentimiento</h3>
                    <div class="bg-gray-100 dark:bg-gray-900 p-4 rounded-md">
                      <div class="flex justify-between items-center mb-2">
                        <span class="text-sm font-medium">Sentimiento: 
                          <span 
                            :class="{
                              'text-green-600 dark:text-green-400': analysisResult.textAnalytics.sentiment.label === 'positive',
                              'text-yellow-600 dark:text-yellow-400': analysisResult.textAnalytics.sentiment.label === 'neutral',
                              'text-red-600 dark:text-red-400': analysisResult.textAnalytics.sentiment.label === 'negative'
                            }"
                          >
                            {{ getSentimentLabel(analysisResult.textAnalytics.sentiment.label) }}
                          </span>
                        </span>
                      </div>
                      <div class="space-y-2">
                        <div class="flex items-center">
                          <span class="text-xs w-20">Positivo:</span>
                          <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              class="bg-green-500 h-2 rounded-full" 
                              :style="`width: ${analysisResult.textAnalytics.sentiment.score.positive * 100}%`"
                            ></div>
                          </div>
                          <span class="text-xs ml-2 w-10">{{ Math.round(analysisResult.textAnalytics.sentiment.score.positive * 100) }}%</span>
                        </div>
                        <div class="flex items-center">
                          <span class="text-xs w-20">Neutral:</span>
                          <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              class="bg-yellow-500 h-2 rounded-full" 
                              :style="`width: ${analysisResult.textAnalytics.sentiment.score.neutral * 100}%`"
                            ></div>
                          </div>
                          <span class="text-xs ml-2 w-10">{{ Math.round(analysisResult.textAnalytics.sentiment.score.neutral * 100) }}%</span>
                        </div>
                        <div class="flex items-center">
                          <span class="text-xs w-20">Negativo:</span>
                          <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              class="bg-red-500 h-2 rounded-full" 
                              :style="`width: ${analysisResult.textAnalytics.sentiment.score.negative * 100}%`"
                            ></div>
                          </div>
                          <span class="text-xs ml-2 w-10">{{ Math.round(analysisResult.textAnalytics.sentiment.score.negative * 100) }}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- PII Detection -->
                  <div v-if="analysisResult.textAnalytics.detected_pii && analysisResult.textAnalytics.detected_pii.length > 0">
                    <h3 class="text-sm font-medium mb-3">Información Personal Identificable (PII)</h3>
                    <div class="bg-gray-100 dark:bg-gray-900 p-4 rounded-md">
                      <ul class="space-y-2">
                        <li 
                          v-for="(pii, i) in analysisResult.textAnalytics.detected_pii" 
                          :key="i"
                          class="flex items-center gap-2 text-sm"
                        >
                          <UserIcon class="h-4 w-4 text-orange-500" />
                          <span class="font-medium">{{ pii.text }}</span>
                          <span class="text-xs px-2 py-0.5 bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300 rounded-full">
                            {{ pii.category }}
                          </span>
                        </li>
                      </ul>
                    </div>
                  </div>
                  
                  <!-- Key Phrases -->
                  <div v-if="analysisResult.textAnalytics.key_phrases && analysisResult.textAnalytics.key_phrases.length > 0">
                    <h3 class="text-sm font-medium mb-3">Frases Clave</h3>
                    <div class="flex flex-wrap gap-2">
                      <span 
                        v-for="(phrase, i) in analysisResult.textAnalytics.key_phrases" 
                        :key="i"
                        class="px-3 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded-full text-xs"
                      >
                        {{ phrase }}
                      </span>
                    </div>
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
  import { ShieldIcon, CheckCircleIcon, InfoIcon, AlertCircleIcon, UserIcon } from 'lucide-vue-next';
  import type { AnalysisResponse } from '@/types';
  
  const userPrompt = ref<string>('');
  const analysisResult = ref<AnalysisResponse | null>(null);
  const isLoading = ref<boolean>(false);
  const activeTab = ref<'improved' | 'openai' | 'azure'>('improved');
  const copied = ref<boolean>(false);
  
  const analyzePrompt = async (): Promise<void> => {
    if (!userPrompt.value.trim()) return;
    
    isLoading.value = true;
    
    try {
      const response = await axios.post<AnalysisResponse>('/api/analyze-prompt', {
        prompt: userPrompt.value
      });
      
      analysisResult.value = response.data;
      activeTab.value = 'improved';
    } catch (error) {
      console.error("Error analyzing prompt:", error);
      alert("Ocurrió un error al analizar el prompt. Por favor, intente de nuevo.");
    } finally {
      isLoading.value = false;
    }
  };
  
  const copyToClipboard = (): void => {
    if (!analysisResult.value) return;
    
    navigator.clipboard.writeText(analysisResult.value.improvedPrompt);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  };
  
  const getSeverityClass = (severity: number | null): string => {
    if (severity === null || severity === undefined) return '';
    
    if (severity >= 4) return 'border-2 border-red-500';
    if (severity >= 2) return 'border-2 border-yellow-500';
    return '';
  };
  
  const getSentimentLabel = (sentiment: string): string => {
    switch (sentiment) {
      case 'positive': return 'Positivo';
      case 'negative': return 'Negativo';
      case 'neutral': return 'Neutral';
      default: return sentiment;
    }
  };
  </script>