<template>
    <aside 
      :class="[
        'bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ease-in-out z-20',
        collapsed ? 'w-16' : 'w-80'
      ]"
    >
      <!-- Logo -->
      <div class="flex items-center justify-center h-16 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center">
          <ShieldIcon class="h-8 w-8 text-primary-500" />
          <span 
            v-if="!collapsed" 
            class="ml-2 text-xl font-semibold text-gray-900 dark:text-gray-100"
          >
            Azure Prompt Guardian
          </span>
        </div>
      </div>
      
      <!-- Navigation -->
      <nav class="mt-6">
        <div class="px-4 space-y-2">
          <router-link 
            to="/analyze" 
            :class="[
              'flex items-center py-3 px-4 rounded-md transition-colors',
              route.path === '/analyze' 
                ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400' 
                : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
            ]"
          >
            <MessageSquareIcon class="h-5 w-5" />
            <span v-if="!collapsed" class="ml-3">Análisis de Prompts</span>
          </router-link>
          
          <router-link 
            to="/dashboard" 
            :class="[
              'flex items-center py-3 px-4 rounded-md transition-colors',
              route.path === '/dashboard' 
                ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400' 
                : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
            ]"
          >
            <BarChartIcon class="h-5 w-5" />
            <span v-if="!collapsed" class="ml-3">Dashboard</span>
          </router-link>
        </div>
      </nav>
      
      <!-- Footer -->
      <div class="absolute bottom-0 w-full p-4 border-t border-gray-200 dark:border-gray-700 bg-inherit">
        <div class="flex items-center justify-center">
          <span v-if="!collapsed" class="text-xs text-gray-500 dark:text-gray-400">
            v2.0 - Powered by Azure AI
          </span>
          <span v-else class="text-xs text-gray-500 dark:text-gray-400">v2.0</span>
        </div>
      </div>
    </aside>
  </template>
  
  <script setup lang="ts">
  import { useRoute } from 'vue-router';
  import { ShieldIcon, MessageSquareIcon, BarChartIcon } from 'lucide-vue-next';
  
  const route = useRoute();
  
  defineProps({
    collapsed: {
      type: Boolean,
      default: false
    }
  });
  </script>