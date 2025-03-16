<template>
    <div class="h-64">
      <Doughnut :data="chartData" :options="chartOptions" />
    </div>
  </template>
  
  <script setup lang="ts">
  import { computed } from 'vue';
  import { Doughnut } from 'vue-chartjs';
  import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
  import type { ContentSafetyMetric } from '@/types';
  
  ChartJS.register(ArcElement, Tooltip, Legend);
  
  const props = defineProps<{
    data: ContentSafetyMetric[]
  }>();
  
  const chartData = computed(() => {
    // Calcular promedios para cada categoría
    const totalDays = props.data.length;
    const avgHate = props.data.reduce((sum, item) => sum + item.hate, 0) / totalDays;
    const avgSelfHarm = props.data.reduce((sum, item) => sum + item.selfHarm, 0) / totalDays;
    const avgSexual = props.data.reduce((sum, item) => sum + item.sexual, 0) / totalDays;
    const avgViolence = props.data.reduce((sum, item) => sum + item.violence, 0) / totalDays;
    
    return {
      labels: ['Odio', 'Autolesión', 'Sexual', 'Violencia'],
      datasets: [
        {
          data: [avgHate, avgSelfHarm, avgSexual, avgViolence],
          backgroundColor: [
            'rgba(239, 68, 68, 0.7)',
            'rgba(245, 158, 11, 0.7)',
            'rgba(139, 92, 246, 0.7)',
            'rgba(59, 130, 246, 0.7)'
          ],
          borderColor: [
            'rgb(239, 68, 68)',
            'rgb(245, 158, 11)',
            'rgb(139, 92, 246)',
            'rgb(59, 130, 246)'
          ],
          borderWidth: 1
        }
      ]
    };
  });
  
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `Severidad: ${context.raw.toFixed(2)}`;
          }
        }
      }
    }
  };
  </script>