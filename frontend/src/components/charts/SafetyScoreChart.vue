<template>
    <div class="h-64">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </template>
  
  <script setup lang="ts">
  import { computed } from 'vue';
  import { Line } from 'vue-chartjs';
  import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
  import { format, parseISO } from 'date-fns';
  import { es } from 'date-fns/locale';
  import type { DailyMetric } from '@/types';
  
  ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);
  
  const props = defineProps<{
    data: DailyMetric[]
  }>();
  
  const chartData = computed(() => {
    return {
      labels: props.data.map(item => format(parseISO(item.date), 'dd MMM', { locale: es })),
      datasets: [
        {
          label: 'Seguridad',
          data: props.data.map(item => item.avgSafetyScore),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.5)',
          tension: 0.3,
          fill: false
        },
        {
          label: 'Claridad',
          data: props.data.map(item => item.avgClarityScore),
          borderColor: '#8b5cf6',
          backgroundColor: 'rgba(139, 92, 246, 0.5)',
          tension: 0.3,
          fill: false
        }
      ]
    };
  });
  
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const
      },
      tooltip: {
        mode: 'index',
        intersect: false
      }
    },
    scales: {
      y: {
        min: 0,
        max: 10,
        ticks: {
          stepSize: 2
        }
      }
    }
  };
  </script>