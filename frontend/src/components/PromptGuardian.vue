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
                @click="activeTab = 'safety'" 
                :class="[
                  'py-2 px-4 text-sm font-medium border-b-2 focus:outline-none transition-colors',
                  activeTab === 'safety' 
                    ? 'border-primary-500 text-primary-500' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                Seguridad
              </button>
              <button 
                @click="activeTab = 'text'" 
                :class="[
                  'py-2 px-4 text-sm font-medium border-b-2 focus:outline-none transition-colors',
                  activeTab === 'text' 
                    ? 'border-primary-500 text-primary-500' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                Análisis de Texto
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
                <div class="grid grid-cols-3 gap-4">
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
                  </div>
                </div>
                
                <!-- Audit Info -->
                <div class="bg-gray-100 dark:bg-gray-900 p-4 rounded-md">
                  <h3 class="text-sm font-medium mb-2">Información de Auditoría</h3>
                  <div class="grid grid-cols-2 gap-2 text-xs">
                    <div class="text-gray-500 dark:text-gray-400">ID de Análisis:</div>
                    <div class="font-mono">{{ analysisResult.analysis_id }}</div>
                    <div class="text-gray-500 dark:text-gray-400">ID de Responsabilidad:</div>
                    <div class="font-mono">{{ analysisResult.accountability_id }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Safety Analysis Tab -->
          <div v-if="activeTab === 'safety' && !analysisResult.error" class="mt-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
              <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 class="text-lg font-semibold flex items-center gap-2">
                  <ShieldIcon class="h-5 w-5 text-purple-500" />
                  Análisis de Seguridad
                </h2>
                <p class="text-sm text-gray-500 dark:text-gray-400">Evaluación de seguridad de contenido</p>
              </div>
              
              <div class="p-4 space-y-6">
                <!-- Content Safety -->
                <div>
                  <h3 class="text-sm font-medium mb-3">Análisis de Seguridad de Contenido</h3>
                  <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
                    <div 
                      class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center"
                      :class="getSeverityClass(analysisResult.transparency_report.safety_analysis.Hate)"
                    >
                      <div class="text-xl font-bold">{{ analysisResult.transparency_report.safety_analysis.Hate || 0 }}</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">Odio</div>
                    </div>
                    <div 
                      class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center"
                      :class="getSeverityClass(analysisResult.transparency_report.safety_analysis.SelfHarm)"
                    >
                      <div class="text-xl font-bold">{{ analysisResult.transparency_report.safety_analysis.SelfHarm || 0 }}</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">Autolesión</div>
                    </div>
                    <div 
                      class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center"
                      :class="getSeverityClass(analysisResult.transparency_report.safety_analysis.Sexual)"
                    >
                      <div class="text-xl font-bold">{{ analysisResult.transparency_report.safety_analysis.Sexual || 0 }}</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">Sexual</div>
                    </div>
                    <div 
                      class="bg-gray-100 dark:bg-gray-900 p-3 rounded-md text-center"
                      :class="getSeverityClass(analysisResult.transparency_report.safety_analysis.Violence)"
                    >
                      <div class="text-xl font-bold">{{ analysisResult.transparency_report.safety_analysis.Violence || 0 }}</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">Violencia</div>
                    </div>
                  </div>
                </div>
                
                <!-- Safety Thresholds -->
                <div>
                  <h3 class="text-sm font-medium mb-3">Umbrales de Seguridad</h3>
                  <div class="bg-gray-100 dark:bg-gray-900 p-4 rounded-md">
                    <div class="grid grid-cols-2 gap-2 text-sm">
                      <div>Odio:</div>
                      <div>4</div>
                      <div>Autolesión:</div>
                      <div>2</div>
                      <div>Sexual:</div>
                      <div>3</div>
                      <div>Violencia:</div>
                      <div>3</div>
                    </div>
                    <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                      Los valores por encima de estos umbrales se consideran potencialmente problemáticos.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Text Analysis Tab -->
          <div v-if="activeTab === 'text' && !analysisResult.error" class="mt-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
              <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 class="text-lg font-semibold flex items-center gap-2">
                  <FileTextIcon class="h-5 w-5 text-orange-500" />
                  Análisis de Texto
                </h2>
                <p class="text-sm text-gray-500 dark:text-gray-400">Análisis de sentimiento, PII y frases clave</p>
              </div>
              
              <div class="p-4 space-y-6">
                <!-- Sentiment Analysis -->
                <div>
                  <h3 class="text-sm font-medium mb-3">Análisis de Sentimiento</h3>
                  <div class="bg-gray-100 dark:bg-gray-900 p-4 rounded-md">
                    <div class="flex justify-between items-center mb-2">
                      <span class="text-sm font-medium">Sentimiento: 
                        <span 
                          :class="{
                            'text-green-600 dark:text-green-400': analysisResult.transparency_report.text_analysis.sentiment.label === 'positive',
                            'text-yellow-600 dark:text-yellow-400': analysisResult.transparency_report.text_analysis.sentiment.label === 'neutral',
                            'text-red-600 dark:text-red-400': analysisResult.transparency_report.text_analysis.sentiment.label === 'negative'
                          }"
                        >
                          {{ getSentimentLabel(analysisResult.transparency_report.text_analysis.sentiment.label) }}
                        </span>
                      </span>
                    </div>
                    <div class="space-y-2">
                      <div class="flex items-center">
                        <span class="text-xs w-20">Positivo:</span>
                        <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            class="bg-green-500 h-2 rounded-full" 
                            :style="`width: ${analysisResult.transparency_report.text_analysis.sentiment.scores.positive * 100}%`"
                          ></div>
                        </div>
                        <span class="text-xs ml-2 w-10">{{ Math.round(analysisResult.transparency_report.text_analysis.sentiment.scores.positive * 100) }}%</span>
                      </div>
                      <div class="flex items-center">
                        <span class="text-xs w-20">Neutral:</span>
                        <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            class="bg-yellow-500 h-2 rounded-full" 
                            :style="`width: ${analysisResult.transparency_report.text_analysis.sentiment.scores.neutral * 100}%`"
                          ></div>
                        </div>
                        <span class="text-xs ml-2 w-10">{{ Math.round(analysisResult.transparency_report.text_analysis.sentiment.scores.neutral * 100) }}%</span>
                      </div>
                      <div class="flex items-center">
                        <span class="text-xs w-20">Negativo:</span>
                        <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            class="bg-red-500 h-2 rounded-full" 
                            :style="`width: ${analysisResult.transparency_report.text_analysis.sentiment.scores.negative * 100}%`"
                          ></div>
                        </div>
                        <span class="text-xs ml-2 w-10">{{ Math.round(analysisResult.transparency_report.text_analysis.sentiment.scores.negative * 100) }}%</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- PII Detection -->
                <div v-if="analysisResult.transparency_report.text_analysis.pii && analysisResult.transparency_report.text_analysis.pii.length > 0">
                  <h3 class="text-sm font-medium mb-3">Información Personal Identificable (PII)</h3>
                  <div class="bg-gray-100 dark:bg-gray-900 p-4 rounded-md">
                    <ul class="space-y-2">
                      <li 
                        v-for="(pii, i) in analysisResult.transparency_report.text_analysis.pii" 
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
                <div v-if="analysisResult.transparency_report.text_analysis.key_phrases && analysisResult.transparency_report.text_analysis.key_phrases.length > 0">
                  <h3 class="text-sm font-medium mb-3">Frases Clave</h3>
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
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { 
  ShieldIcon, 
  CheckCircleIcon, 
  BarChart2Icon, 
  FileTextIcon, 
  UserIcon,
  AlertTriangleIcon,
  ClipboardIcon,
  XIcon
} from 'lucide-vue-next';
import type { AnalysisResponse, AuditTrail } from '@/types';
import { analyzePrompt as analyzePromptApi, getAuditTrail } from '@/services/api';

const userPrompt = ref<string>('');
const analysisResult = ref<AnalysisResponse | null>(null);
const auditTrail = ref<AuditTrail | null>(null);
const isLoading = ref<boolean>(false);
const activeTab = ref<'improved' | 'scores' | 'safety' | 'text' | 'audit'>('improved');
const copied = ref<boolean>(false);
const showAuditModal = ref<boolean>(false);

const analyzePrompt = async (): Promise<void> => {
  if (!userPrompt.value.trim() || userPrompt.value.length < 10) return;
  
  isLoading.value = true;
  auditTrail.value = null;
  
  try {
    const result = await analyzePromptApi(userPrompt.value);
    analysisResult.value = result;
    activeTab.value = 'improved';
    
    // Si no hay error, cargar el registro de auditoría
    if (!result.error && result.analysis_id) {
      loadAuditTrail(result.analysis_id);
    }
  } catch (error) {
    console.error("Error analyzing prompt:", error);
    alert("Ocurrió un error al analizar el prompt. Por favor, intente de nuevo.");
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

const getSeverityClass = (severity: number | null | undefined): string => {
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

const formatPrivacyMeasure = (measure: string): string => {
  switch (measure) {
    case 'pii_redaction': return 'Redacción de PII';
    default: return measure.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

const viewFullAudit = (): void => {
  showAuditModal.value = true;
};

// Limpiar el resultado cuando cambia el prompt
watch(userPrompt, () => {
  if (analysisResult.value) {
    analysisResult.value = null;
    auditTrail.value = null;
  }
});
</script>

