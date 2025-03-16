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
          label: 'Prompts',
          data: props.data.map(item => item.count),
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.5)',
          tension: 0.3,
          fill: true
        }
      ]
    };
  });
  
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        mode: 'index',
        intersect: false
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0
        }
      }
    }
  };
  </script>