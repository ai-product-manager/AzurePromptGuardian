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
  import type { SentimentMetric } from '@/types';
  
  ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);
  
  const props = defineProps<{
    data: SentimentMetric[]
  }>();
  
  const chartData = computed(() => {
    return {
      labels: props.data.map(item => format(parseISO(item.date), 'dd MMM', { locale: es })),
      datasets: [
        {
          label: 'Positivo',
          data: props.data.map(item => item.positive),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.5)',
          tension: 0.3,
          fill: false
        },
        {
          label: 'Neutral',
          data: props.data.map(item => item.neutral),
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.5)',
          tension: 0.3,
          fill: false
        },
        {
          label: 'Negativo',
          data: props.data.map(item => item.negative),
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.5)',
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
        max: 1,
        ticks: {
          callback: function(value: any) {
            return (value * 100) + '%';
          }
        }
      }
    }
  };
  </script>