<template>
    <div class="flex h-screen bg-gray-100 dark:bg-gray-900">
      <!-- Sidebar -->
      <Sidebar :collapsed="sidebarCollapsed" />
      
      <!-- Main Content -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Top Navigation -->
        <header class="bg-white dark:bg-gray-800 shadow-sm z-10">
          <div class="px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
            <button 
              @click="toggleSidebar" 
              class="p-2 rounded-md text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 focus:outline-none"
            >
              <MenuIcon v-if="sidebarCollapsed" class="h-6 w-6" />
              <XIcon v-else class="h-6 w-6" />
            </button>
            
            <div class="flex items-center">
              <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
                {{ currentPageTitle }}
              </h1>
            </div>
            
            <div class="flex items-center space-x-4">
              <button 
                @click="toggleDarkMode" 
                class="p-2 rounded-md text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 focus:outline-none"
              >
                <SunIcon v-if="isDarkMode" class="h-5 w-5" />
                <MoonIcon v-else class="h-5 w-5" />
              </button>
            </div>
          </div>
        </header>
        
        <!-- Page Content -->
        <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <slot></slot>
        </main>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, computed, onMounted, watch } from 'vue';
  import { useRoute } from 'vue-router';
  import { MenuIcon, XIcon, SunIcon, MoonIcon } from 'lucide-vue-next';
  import Sidebar from './Sidebar.vue';
  
  const route = useRoute();
  const sidebarCollapsed = ref(window.innerWidth < 768);
  const isDarkMode = ref(false);
  
  const currentPageTitle = computed(() => {
    return route.meta.title as string || 'Azure Prompt Guardian';
  });
  
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value;
  };
  
  const toggleDarkMode = () => {
    isDarkMode.value = !isDarkMode.value;
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', isDarkMode.value ? 'dark' : 'light');
  };
  
  // Check for saved dark mode preference
  onMounted(() => {
    const savedMode = localStorage.getItem('darkMode');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    isDarkMode.value = savedMode === 'dark' || (savedMode === null && prefersDark);
    
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark');
    }
    
    // Handle window resize for responsive sidebar
    const handleResize = () => {
      if (window.innerWidth < 768) {
        sidebarCollapsed.value = true;
      }
    };
    
    window.addEventListener('resize', handleResize);
    
    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  });
  </script>