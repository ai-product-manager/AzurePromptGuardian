<template>
  <div class="container mx-auto py-8 max-w-4xl px-4">
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
          
          <!-- Configuración Avanzada (Colapsable) -->
          <div class="mt-4">
            <button 
              @click="showAdvancedConfig = !showAdvancedConfig" 
              class="flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 dark:hover:text-primary-400 focus:outline-none"
            >
              <ChevronRightIcon 
                :class="[
                  'h-4 w-4 mr-1 transition-transform', 
                  showAdvancedConfig ? 'transform rotate-90' : ''
                ]" 
              />
              Configuración Avanzada
            </button>
            
            <div v-if="showAdvancedConfig" class="mt-3 p-4 bg-gray-50 dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-700 space-y-4">
              <!-- Generar Variantes -->
              <div class="flex items-center">
                <input 
                  type="checkbox" 
                  id="generate-variants" 
                  v-model="generateVariants"
                  class="h-4 w-4 text-primary-500 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label for="generate-variants" class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Generar variantes optimizadas
                </label>
              </div>
              
              <!-- Modelo Objetivo -->
              <div>
                <label for="target-model" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Modelo Objetivo
                </label>
                <select 
                  id="target-model" 
                  v-model="targetModel"
                  class="w-full p-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="claude-3">Claude 3</option>
                  <option value="llama-3">Llama 3</option>
                  <option value="gemini-pro">Gemini Pro</option>
                  <option value="mistral-large">Mistral Large</option>
                </select>
              </div>
              
              <!-- Enfoque de Optimización -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Enfoque de Optimización
                </label>
                <div class="grid grid-cols-2 gap-2">
                  <div class="flex items-center">
                    <input 
                      type="checkbox" 
                      id="focus-clarity" 
                      value="clarity" 
                      v-model="optimizationFocus"
                      class="h-4 w-4 text-primary-500 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label for="focus-clarity" class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                      Claridad
                    </label>
                  </div>
                  <div class="flex items-center">
                    <input 
                      type="checkbox" 
                      id="focus-specificity" 
                      value="specificity" 
                      v-model="optimizationFocus"
                      class="h-4 w-4 text-primary-500 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label for="focus-specificity" class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                      Especificidad
                    </label>
                  </div>
                  <div class="flex items-center">
                    <input 
                      type="checkbox" 
                      id="focus-conciseness" 
                      value="conciseness" 
                      v-model="optimizationFocus"
                      class="h-4 w-4 text-primary-500 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label for="focus-conciseness" class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                      Concisión
                    </label>
                  </div>
                  <div class="flex items-center">
                    <input 
                      type="checkbox" 
                      id="focus-safety" 
                      value="safety" 
                      v-model="optimizationFocus"
                      class="h-4 w-4 text-primary-500 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label for="focus-safety" class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                      Seguridad
                    </label>
                  </div>
                </div>
              </div>
              
              <!-- Contexto Adicional -->
              <div>
                <label for="additional-context" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Contexto Adicional
                </label>
                <textarea
                  id="additional-context"
                  v-model="additionalContext"
                  placeholder="Proporcione contexto adicional para entender mejor el prompt..."
                  rows="3"
                  class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-transparent focus:outline-none focus:ring-2 focus:ring-primary-500"
                ></textarea>
              </div>
            </div>
          </div>
        </div>
        <div class="p-4 border-t border-gray-200 dark:border-gray-700">
          <button 
            @click="analyzePrompt" 
            :disabled="isLoading || !userPrompt.trim() || userPrompt.length < 10" 
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
          <!-- Error Message -->
          <div v-if="analysisResult.error" class="bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-800 text-red-800 dark:text-red-300 p-4 rounded-md mb-4">
            <div class="flex items-start">
              <AlertTriangleIcon class="h-5 w-5 mr-2 mt-0.5" />
              <div>
                <h3 class="font-medium">Prompt Rechazado</h3>
                <p>{{ analysisResult.error }}</p>
                <p class="mt-2 text-sm">El prompt ha sido rechazado por motivos de seguridad. Por favor, revise el contenido y asegúrese de que cumple con las políticas de uso.</p>
              </div>
            </div>
          </div>

          <!-- Tabs -->
          <div v-if="!analysisResult.error" class="border-b border-gray-200 dark:border-gray-700">
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
                @click="activeTab = 'scores'" 
                :class="[
                  'py-2 px-4 text-sm font-medium border-b-2 focus:outline-none transition-colors',
                  activeTab === 'scores' 
                    ? 'border-primary-500 text-primary-500' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                Puntuaciones
              </button>
              <button 
                @click="activeTab = 'issues'" 
                :class="[
                  'py-2 px-4 text-sm font-medium border-b-2 focus:outline-none transition-colors',
                  activeTab === 'issues' 
                    ? 'border-primary-500 text-primary-500' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                Problemas
              </button>
              <button 
                @click="activeTab = 'variants'" 
                :class="[
                  'py-2 px-4 text-sm font-medium border-b-2 focus:outline-none transition-colors',
                  activeTab === 'variants' 
                    ? 'border-primary-500 text-primary-500' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                Variantes
              </button>
              <button 
                @click="activeTab = 'audit'" 
                :class="[
                  'py-2 px-4 text-sm font-medium border-b-2 focus:outline-none transition-colors',
                  activeTab === 'audit' 
                    ? 'border-primary-500 text-primary-500' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                Auditoría
              </button>
            </div>
          </div>

          <!-- Improved Prompt Tab -->
          <div v-if="activeTab === 'improved' && !analysisResult.error" class="mt-4">
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
                  {{ analysisResult.improved_prompt }}
                </div>
                
                <!-- Explicación de mejoras -->
                <div v-if="analysisResult.improvement_explanation" class="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-md">
                  <h3 class="text-sm font-medium text-blue-800 dark:text-blue-300 mb-2">Explicación de mejoras:</h3>
                  <p class="text-sm text-blue-700 dark:text-blue-200">{{ analysisResult.improvement_explanation }}</p>
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

          <!-- Scores Tab -->
          <div v-if="activeTab === 'scores' && !analysisResult.error" class="mt-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
              <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 class="text-lg font-semibold flex items-center gap-2">
                  <BarChart2Icon class="h-5 w-5 text-blue-500" />
                  Puntuaciones de Calidad
                </h2>
                <p class="text-sm text-gray-500 dark:text-gray-400">Evaluación de equidad, seguridad e inclusividad</p>
              </div>
              <div class="p-4 space-y-6">
                <!-- Scores -->
                <div class="grid grid-cols-2 gap-4 sm:grid-cols-3">
                  <div class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center">
                    <div class="text-2xl font-bold">{{ Math.round(analysisResult.safety_score * 100) }}%</div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">Seguridad</div>
                    <div class="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        class="bg-green-500 h-2 rounded-full" 
                        :style="`width: ${analysisResult.safety_score * 100}%`"
                      ></div>
                    </div>
                  </div>
                  <div class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center">
                    <div class="text-2xl font-bold">{{ Math.round(analysisResult.fairness_score * 100) }}%</div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">Equidad</div>
                    <div class="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        class="bg-blue-500 h-2 rounded-full" 
                        :style="`width: ${analysisResult.fairness_score * 100}%`"
                      ></div>
                    </div>
                  </div>
                  <div class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center">
                    <div class="text-2xl font-bold">{{ Math.round(analysisResult.inclusivity_score * 100) }}%</div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">Inclusividad</div>
                    <div class="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        class="bg-purple-500 h-2 rounded-full" 
                        :style="`width: ${analysisResult.inclusivity_score * 100}%`"
                      ></div>
                    </div>
                  </div>
                </div>
                
                <!-- Ambiguity Scores -->
                <div class="grid grid-cols-3 gap-4">
                  <div class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center">
                    <div class="text-2xl font-bold">{{ Math.round((1 - analysisResult.ambiguity_score) * 100) }}%</div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">Claridad</div>
                    <div class="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        class="bg-yellow-500 h-2 rounded-full" 
                        :style="`width: ${(1 - analysisResult.ambiguity_score) * 100}%`"
                      ></div>
                    </div>
                  </div>
                  <div class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center">
                    <div class="text-2xl font-bold">{{ Math.round(analysisResult.completeness_score * 100) }}%</div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">Completitud</div>
                    <div class="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        class="bg-orange-500 h-2 rounded-full" 
                        :style="`width: ${analysisResult.completeness_score * 100}%`"
                      ></div>
                    </div>
                  </div>
                  <div class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center">
                    <div class="text-2xl font-bold">{{ Math.round(analysisResult.clarity_score * 100) }}%</div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">Precisión</div>
                    <div class="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        class="bg-teal-500 h-2 rounded-full" 
                        :style="`width: ${analysisResult.clarity_score * 100}%`"
                      ></div>
                    </div>
                  </div>
                </div>
                
                <!-- Privacy Measures -->
                <div class="space-y-2">
                  <h3 class="text-sm font-medium">Medidas de Privacidad Aplicadas</h3>
                  <div class="flex flex-wrap gap-2">
                    <span 
                      v-for="(measure, i) in analysisResult.privacy_measures" 
                      :key="i"
                      class="px-3 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded-full text-xs"
                    >
                      {{ formatPrivacyMeasure(measure) }}
                    </span>
                    <span v-if="!analysisResult.privacy_measures || analysisResult.privacy_measures.length === 0" 
                      class="px-3 py-1 bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300 rounded-full text-xs">
                      No se requirieron medidas de privacidad
                    </span>
                  </div>
                </div>
                
                <!-- Safety Analysis -->
                <div class="bg-gray-100 dark:bg-gray-900 p-4 rounded-md">
                  <h3 class="text-sm font-medium mb-2">Análisis de Seguridad</h3>
                  <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
                    <div v-for="(value, category) in analysisResult.transparency_report.safety_analysis.categories" :key="category"
                      class="flex flex-col items-center">
                      <div class="text-sm font-medium">{{ formatCategory(category) }}</div>
                      <div :class="getSeverityTextClass(value)" class="text-lg font-bold">
                        {{ value }}
                      </div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">
                        {{ getSeverityLabel(value) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Issues Tab -->
          <div v-if="activeTab === 'issues' && !analysisResult.error" class="mt-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
              <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 class="text-lg font-semibold flex items-center gap-2">
                  <AlertCircleIcon class="h-5 w-5 text-orange-500" />
                  Problemas Detectados
                </h2>
                <p class="text-sm text-gray-500 dark:text-gray-400">Problemas identificados en el prompt original</p>
              </div>
              
              <div class="p-4 space-y-4">
                <div v-if="analysisResult.issues && analysisResult.issues.length > 0">
                  <div v-for="(issue, index) in analysisResult.issues" :key="index" 
                    class="mb-4 p-4 rounded-md"
                    :class="{
                      'bg-red-50 dark:bg-red-900/20': issue.severity === 'high',
                      'bg-yellow-50 dark:bg-yellow-900/20': issue.severity === 'medium',
                      'bg-blue-50 dark:bg-blue-900/20': issue.severity === 'low'
                    }">
                    <div class="flex items-start">
                      <div :class="{
                        'text-red-500 dark:text-red-400': issue.severity === 'high',
                        'text-yellow-500 dark:text-yellow-400': issue.severity === 'medium',
                        'text-blue-500 dark:text-blue-400': issue.severity === 'low'
                      }" class="mr-3 mt-0.5">
                        <AlertTriangleIcon v-if="issue.severity === 'high'" class="h-5 w-5" />
                        <AlertCircleIcon v-else-if="issue.severity === 'medium'" class="h-5 w-5" />
                        <InfoIcon v-else class="h-5 w-5" />
                      </div>
                      <div class="flex-1">
                        <div class="flex items-center mb-1">
                          <h3 :class="{
                            'text-red-800 dark:text-red-300': issue.severity === 'high',
                            'text-yellow-800 dark:text-yellow-300': issue.severity === 'medium',
                            'text-blue-800 dark:text-blue-300': issue.severity === 'low'
                          }" class="text-sm font-medium">
                            {{ formatIssueType(issue.type) }}
                          </h3>
                          <span :class="{
                            'bg-red-200 text-red-800 dark:bg-red-800 dark:text-red-200': issue.severity === 'high',
                            'bg-yellow-200 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200': issue.severity === 'medium',
                            'bg-blue-200 text-blue-800 dark:bg-blue-800 dark:text-blue-200': issue.severity === 'low'
                          }" class="ml-2 px-2 py-0.5 rounded-full text-xs">
                            {{ formatSeverity(issue.severity) }}
                          </span>
                        </div>
                        <p :class="{
                          'text-red-700 dark:text-red-300': issue.severity === 'high',
                          'text-yellow-700 dark:text-yellow-300': issue.severity === 'medium',
                          'text-blue-700 dark:text-blue-300': issue.severity === 'low'
                        }" class="text-sm mb-2">
                          {{ issue.description }}
                        </p>
                        <div :class="{
                          'bg-red-100 dark:bg-red-900/40 border-red-200 dark:border-red-800': issue.severity === 'high',
                          'bg-yellow-100 dark:bg-yellow-900/40 border-yellow-200 dark:border-yellow-800': issue.severity === 'medium',
                          'bg-blue-100 dark:bg-blue-900/40 border-blue-200 dark:border-blue-800': issue.severity === 'low'
                        }" class="text-sm p-2 rounded border">
                          <span class="font-medium">Solución: </span>{{ issue.mitigation }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div v-else class="text-center py-8">
                  <CheckCircleIcon class="h-12 w-12 text-green-500 mx-auto mb-3" />
                  <p class="text-lg font-medium text-gray-900 dark:text-gray-100">¡No se detectaron problemas!</p>
                  <p class="text-gray-500 dark:text-gray-400">El prompt parece estar bien formulado.</p>
                </div>
                
                <!-- Ambiguity Analysis -->
                <div v-if="analysisResult.transparency_report.ambiguity_analysis" class="mt-6">
                  <h3 class="text-sm font-medium mb-3">Análisis de Ambigüedad</h3>
                  
                  <!-- Ambiguous Terms -->
                  <div v-if="analysisResult.transparency_report.ambiguity_analysis.ambiguous_terms && analysisResult.transparency_report.ambiguity_analysis.ambiguous_terms.length > 0" class="mb-4">
                    <h4 class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">Términos Ambiguos:</h4>
                    <div class="flex flex-wrap gap-2">
                      <span 
                        v-for="(term, i) in analysisResult.transparency_report.ambiguity_analysis.ambiguous_terms" 
                        :key="i"
                        class="px-3 py-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 rounded-full text-xs"
                      >
                        {{ term }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- Missing Context -->
                  <div v-if="analysisResult.transparency_report.ambiguity_analysis.missing_context && analysisResult.transparency_report.ambiguity_analysis.missing_context.length > 0" class="mb-4">
                    <h4 class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">Contexto Faltante:</h4>
                    <ul class="list-disc pl-5 text-sm text-gray-700 dark:text-gray-300 space-y-1">
                      <li v-for="(context, i) in analysisResult.transparency_report.ambiguity_analysis.missing_context" :key="i">
                        {{ context }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Variants Tab -->
          <div v-if="activeTab === 'variants' && !analysisResult.error" class="mt-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
              <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 class="text-lg font-semibold flex items-center gap-2">
                  <CopyIcon class="h-5 w-5 text-indigo-500" />
                  Variantes Sugeridas
                </h2>
                <p class="text-sm text-gray-500 dark:text-gray-400">Alternativas optimizadas para su prompt</p>
              </div>
              
              <div class="p-4 space-y-6">
                <div v-if="analysisResult.suggested_variants && analysisResult.suggested_variants.length > 0">
                  <div v-for="(variant, index) in analysisResult.suggested_variants" :key="index" 
                    class="mb-6 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                    <div class="mb-3">
                      <div class="flex justify-between items-center mb-2">
                        <h3 class="text-sm font-medium">Variante {{ index + 1 }}</h3>
                        <button 
                          @click="copyVariant(variant.variant_text)" 
                          class="text-xs px-2 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                        >
                          Copiar
                        </button>
                      </div>
                      <div class="p-3 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700 text-sm">
                        {{ variant.variant_text }}
                      </div>
                    </div>
                    
                    <div class="grid grid-cols-3 gap-2 mb-3">
                      <div class="text-center">
                        <div class="text-xs text-gray-500 dark:text-gray-400">Calidad</div>
                        <div class="text-sm font-medium">{{ Math.round(variant.quality_score * 100) }}%</div>
                        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mt-1">
                          <div 
                            class="bg-indigo-500 h-1.5 rounded-full" 
                            :style="`width: ${variant.quality_score * 100}%`"
                          ></div>
                        </div>
                      </div>
                      <div class="text-center">
                        <div class="text-xs text-gray-500 dark:text-gray-400">Claridad</div>
                        <div class="text-sm font-medium">{{ Math.round(variant.clarity_score * 100) }}%</div>
                        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mt-1">
                          <div 
                            class="bg-blue-500 h-1.5 rounded-full" 
                            :style="`width: ${variant.clarity_score * 100}%`"
                          ></div>
                        </div>
                      </div>
                      <div class="text-center">
                        <div class="text-xs text-gray-500 dark:text-gray-400">Especificidad</div>
                        <div class="text-sm font-medium">{{ Math.round(variant.specificity_score * 100) }}%</div>
                        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mt-1">
                          <div 
                            class="bg-green-500 h-1.5 rounded-full" 
                            :style="`width: ${variant.specificity_score * 100}%`"
                          ></div>
                        </div>
                      </div>
                    </div>
                    
                    <div class="text-xs text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 p-2 rounded">
                      <span class="font-medium">Explicación: </span>{{ variant.explanation }}
                    </div>
                  </div>
                </div>
                
                <div v-else class="text-center py-8">
                  <FileX class="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <p class="text-lg font-medium text-gray-900 dark:text-gray-100">No hay variantes disponibles</p>
                  <p class="text-gray-500 dark:text-gray-400">No se generaron variantes para este prompt.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Audit Tab -->
          <div v-if="activeTab === 'audit' && !analysisResult.error" class="mt-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
              <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 class="text-lg font-semibold flex items-center gap-2">
                  <ClipboardIcon class="h-5 w-5 text-indigo-500" />
                  Auditoría y Responsabilidad
                </h2>
                <p class="text-sm text-gray-500 dark:text-gray-400">Información de auditoría y cumplimiento</p>
              </div>
              
              <div class="p-4 space-y-6">
                <!-- Audit Info -->
                <div>
                  <h3 class="text-sm font-medium mb-3">Información de Auditoría</h3>
                  <div class="bg-gray-100 dark:bg-gray-900 p-4 rounded-md">
                    <div class="grid grid-cols-2 gap-3 text-sm">
                      <div class="text-gray-500 dark:text-gray-400">ID de Análisis:</div>
                      <div class="font-mono">{{ analysisResult.analysis_id }}</div>
                      <div class="text-gray-500 dark:text-gray-400">ID de Responsabilidad:</div>
                      <div class="font-mono">{{ analysisResult.accountability_id }}</div>
                      <div class="text-gray-500 dark:text-gray-400">Hash del Prompt:</div>
                      <div class="font-mono text-xs truncate">{{ auditTrail?.prompt_hash || 'Cargando...' }}</div>
                      <div class="text-gray-500 dark:text-gray-400">Timestamp:</div>
                      <div>{{ auditTrail?.timestamp ? formatDate(auditTrail.timestamp) : 'Cargando...' }}</div>
                    </div>
                  </div>
                </div>
                
                <!-- Compliance -->
                <div v-if="auditTrail?.compliance">
                  <h3 class="text-sm font-medium mb-3">Cumplimiento</h3>
                  <div class="flex flex-wrap gap-2">
                    <span 
                      v-for="(standard, i) in auditTrail.compliance" 
                      :key="i"
                      class="px-3 py-1 bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 rounded-full text-xs"
                    >
                      {{ standard }}
                    </span>
                  </div>
                </div>
                
                <!-- Text Analytics -->
                <div v-if="analysisResult.transparency_report.text_analysis">
                  <h3 class="text-sm font-medium mb-3">Análisis de Texto</h3>
                  
                  <!-- Language and Sentiment -->
                  <div class="grid grid-cols-2 gap-4 mb-4">
                    <div class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md">
                      <div class="text-xs text-gray-500 dark:text-gray-400">Idioma</div>
                      <div class="text-sm font-medium">{{ analysisResult.transparency_report.text_analysis.language || 'No detectado' }}</div>
                    </div>
                    <div class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md">
                      <div class="text-xs text-gray-500 dark:text-gray-400">Sentimiento</div>
                      <div class="text-sm font-medium" :class="{
                        'text-green-600 dark:text-green-400': analysisResult.transparency_report.text_analysis.sentiment === 'positive',
                        'text-yellow-600 dark:text-yellow-400': analysisResult.transparency_report.text_analysis.sentiment === 'neutral',
                        'text-red-600 dark:text-red-400': analysisResult.transparency_report.text_analysis.sentiment === 'negative'
                      }">
                        {{ getSentimentLabel(analysisResult.transparency_report.text_analysis.sentiment) }}
                      </div>
                    </div>
                  </div>
                  
                  <!-- Key Phrases -->
                  <div v-if="analysisResult.transparency_report.text_analysis.key_phrases && analysisResult.transparency_report.text_analysis.key_phrases.length > 0" class="mb-4">
                    <h4 class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">Frases Clave:</h4>
                    <div class="flex flex-wrap gap-2">
                      <span 
                        v-for="(phrase, i) in analysisResult.transparency_report.text_analysis.key_phrases" 
                        :key="i"
                        class="px-3 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded-full text-xs"
                      >
                        {{ phrase }}
                      </span>
                    </div>
                  </div>
                </div>
                
                <!-- Responsible AI -->
                <div>
                  <h3 class="text-sm font-medium mb-3">IA Responsable</h3>
                  <div class="bg-gray-100 dark:bg-gray-900 p-4 rounded-md">
                    <p class="text-sm">Este análisis cumple con los principios de IA Responsable:</p>
                    <ul class="mt-2 space-y-1 text-sm">
                      <li class="flex items-start gap-2">
                        <CheckCircleIcon class="h-4 w-4 text-green-500 mt-0.5" />
                        <span>Equidad: Evaluación de sesgos y discriminación</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <CheckCircleIcon class="h-4 w-4 text-green-500 mt-0.5" />
                        <span>Seguridad: Detección de contenido dañino</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <CheckCircleIcon class="h-4 w-4 text-green-500 mt-0.5" />
                        <span>Privacidad: Identificación y redacción de PII</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <CheckCircleIcon class="h-4 w-4 text-green-500 mt-0.5" />
                        <span>Transparencia: Reporte detallado de análisis</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <CheckCircleIcon class="h-4 w-4 text-green-500 mt-0.5" />
                        <span>Responsabilidad: Registro de auditoría completo</span>
                      </li>
                    </ul>
                  </div>
                </div>
                
                <!-- View Full Audit -->
                <div class="flex justify-center">
                  <button 
                    @click="viewFullAudit" 
                    class="py-2 px-4 bg-indigo-500 text-white rounded-md hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors"
                  >
                    Ver Registro de Auditoría Completo
                  </button>
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

    <!-- Audit Modal -->
    <div v-if="showAuditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-auto">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h2 class="text-lg font-semibold">Registro de Auditoría Completo</h2>
          <button @click="showAuditModal = false" class="text-gray-500 hover:text-gray-700">
            <XIcon class="h-5 w-5" />
          </button>
        </div>
        <div class="p-4">
          <pre class="bg-gray-100 dark:bg-gray-900 p-4 rounded-md overflow-auto text-xs font-mono">{{ JSON.stringify(auditTrail, null, 2) }}</pre>
        </div>
        <div class="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
          <button 
            @click="showAuditModal = false" 
            class="py-2 px-4 bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>

    <!-- Feedback Modal -->
    <div v-if="showFeedbackModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h2 class="text-lg font-semibold">¿Fue útil este análisis?</h2>
          <button @click="showFeedbackModal = false" class="text-gray-500 hover:text-gray-700">
            <XIcon class="h-5 w-5" />
          </button>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Calificación</label>
            <div class="flex space-x-2">
              <button 
                v-for="rating in 5" 
                :key="rating"
                @click="feedbackRating = rating"
                :class="[
                  'p-2 rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500',
                  feedbackRating >= rating ? 'text-yellow-500' : 'text-gray-300 dark:text-gray-600'
                ]"
              >
                <StarIcon class="h-6 w-6" />
              </button>
            </div>
          </div>
          
          <div class="mb-4">
            <label for="feedback-comments" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Comentarios (opcional)</label>
            <textarea
              id="feedback-comments"
              v-model="feedbackComments"
              rows="3"
              class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-transparent focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="¿Qué te pareció el análisis?"
            ></textarea>
          </div>
          
          <div class="flex justify-end space-x-3">
            <button 
              @click="submitFeedback(false)" 
              class="py-2 px-4 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
            >
              No fue útil
            </button>
            <button 
              @click="submitFeedback(true)" 
              class="py-2 px-4 bg-primary-500 text-white rounded-md hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
            >
              Fue útil
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Agregemos la variable showAdvancedConfig y el nuevo icono en las importaciones

import { ref, watch } from 'vue';
import { 
  ShieldIcon, 
  CheckCircleIcon, 
  BarChart2Icon, 
  FileTextIcon, 
  UserIcon,
  AlertTriangleIcon,
  ClipboardIcon,
  XIcon,
  AlertCircleIcon,
  InfoIcon,
  CopyIcon,
  FileX,
  StarIcon,
  ChevronRightIcon
} from 'lucide-vue-next';
import type { AnalysisResponse, AuditTrail } from '@/types';
import { analyzePrompt as analyzePromptApi, getAuditTrail, submitFeedback as submitFeedbackApi } from '@/services/api';

const userPrompt = ref<string>('');
const analysisResult = ref<AnalysisResponse | null>(null);
const auditTrail = ref<AuditTrail | null>(null);
const isLoading = ref<boolean>(false);
const activeTab = ref<'improved' | 'scores' | 'issues' | 'variants' | 'audit'>('improved');
const copied = ref<boolean>(false);
const showAuditModal = ref<boolean>(false);
const showFeedbackModal = ref<boolean>(false);
const feedbackRating = ref<number>(0);
const feedbackComments = ref<string>('');
const variantCopied = ref<string | null>(null);

// Primero, agreguemos las nuevas variables de estado para los parámetros de configuración
// Busca la sección donde se definen las variables ref y agrega estas nuevas:

const generateVariants = ref<boolean>(true);
const additionalContext = ref<string>('');
const targetModel = ref<string>('gpt-4');
const optimizationFocus = ref<string[]>([]);
// Y agreguemos la variable de estado para controlar la visibilidad de la configuración avanzada
// Busca la sección donde se definen las variables ref y agrega:

const showAdvancedConfig = ref<boolean>(false);

// Ahora, modifiquemos la función analyzePrompt para incluir estos parámetros
// Busca la función analyzePrompt y actualízala para incluir los nuevos parámetros:

const analyzePrompt = async (): Promise<void> => {
  if (!userPrompt.value.trim() || userPrompt.value.length < 10) return;

  isLoading.value = true;
  auditTrail.value = null;

  try {
    const result = await analyzePromptApi(userPrompt.value, {
      generate_variants: generateVariants.value,
      context: additionalContext.value || undefined,
      target_model: targetModel.value || undefined,
      optimization_focus: optimizationFocus.value.length > 0 ? optimizationFocus.value : undefined
    });
    analysisResult.value = result;
    activeTab.value = 'improved';
    
    // Si no hay error, cargar el registro de auditoría
    if (!result.error && result.analysis_id) {
      loadAuditTrail(result.analysis_id);
      
      // Mostrar modal de feedback después de un tiempo
      setTimeout(() => {
        showFeedbackModal.value = true;
      }, 10000); // 10 segundos
    }
  } catch (error) {
    console.error("Error analyzing prompt:", error);
    alert("Ocurrió un error al analizar el prompt. Por favor, intente de nuevo.", error);
  } finally {
    isLoading.value = false;
  }
};

const loadAuditTrail = async (analysisId: string): Promise<void> => {
  try {
    auditTrail.value = await getAuditTrail(analysisId);
  } catch (error) {
    console.error("Error loading audit trail:", error);
  }
};

const copyToClipboard = (): void => {
  if (!analysisResult.value || !analysisResult.value.improved_prompt) return;

  navigator.clipboard.writeText(analysisResult.value.improved_prompt);
  copied.value = true;
  setTimeout(() => {
    copied.value = false;
  }, 2000);
};

const copyVariant = (text: string): void => {
  navigator.clipboard.writeText(text);
  variantCopied.value = text;
  setTimeout(() => {
    variantCopied.value = null;
  }, 2000);
};

const getSeverityTextClass = (severity: number): string => {
  if (severity >= 4) return 'text-red-600 dark:text-red-400';
  if (severity >= 2) return 'text-yellow-600 dark:text-yellow-400';
  return 'text-green-600 dark:text-green-400';
};

const getSeverityLabel = (severity: number): string => {
  if (severity >= 4) return 'Alto';
  if (severity >= 2) return 'Medio';
  if (severity > 0) return 'Bajo';
  return 'Ninguno';
};

const getSentimentLabel = (sentiment: string): string => {
  switch (sentiment) {
    case 'positive': return 'Positivo';
    case 'negative': return 'Negativo';
    case 'neutral': return 'Neutral';
    default: return sentiment || 'No detectado';
  }
};

const formatPrivacyMeasure = (measure: string): string => {
  switch (measure) {
    case 'pii_redaction': return 'Redacción de PII';
    default: return measure.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }
};

const formatIssueType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'fairness': 'Problema de Equidad',
    'safety': 'Problema de Seguridad',
    'privacy': 'Problema de Privacidad',
    'inclusiveness': 'Problema de Inclusividad',
    'bias': 'Sesgo Detectado',
    'ambiguity': 'Ambigüedad',
    'clarity': 'Falta de Claridad',
    'completeness': 'Información Incompleta',
    'other': 'Otro Problema'
  };
  
  return typeMap[type] || type.replace(/\b\w/g, l => l.toUpperCase());
};

const formatSeverity = (severity: string): string => {
  const severityMap: Record<string, string> = {
    'high': 'Alto',
    'medium': 'Medio',
    'low': 'Bajo'
  };
  
  return severityMap[severity] || severity;
};

const formatCategory = (category: string): string => {
  const categoryMap: Record<string, string> = {
    'Hate': 'Odio',
    'SelfHarm': 'Autolesión',
    'Sexual': 'Sexual',
    'Violence': 'Violencia'
  };
  
  return categoryMap[category] || category;
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

const viewFullAudit = (): void => {
  showAuditModal.value = true;
};

const submitFeedback = async (wasUseful: boolean): Promise<void> => {
  if (!analysisResult.value) return;
  
  try {
    await submitFeedbackApi({
      analysis_id: analysisResult.value.analysis_id,
      satisfaction_rating: feedbackRating.value || undefined,
      feedback_comments: feedbackComments.value || undefined,
      was_useful: wasUseful
    });
    
    showFeedbackModal.value = false;
    alert("¡Gracias por tu feedback!");
  } catch (error) {
    console.error("Error submitting feedback:", error);
    alert("Ocurrió un error al enviar el feedback. Por favor, intente de nuevo.");
  }
};

// Limpiar el resultado cuando cambia el prompt
watch(userPrompt, () => {
  if (analysisResult.value) {
    analysisResult.value = null;
    auditTrail.value = null;
  }
});
</script>

