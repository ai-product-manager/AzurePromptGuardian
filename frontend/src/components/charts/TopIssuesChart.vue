<template>
  <div class="h-64">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import type { IssueMetric } from '@/types';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const props = defineProps<{
  data: IssueMetric[]
}>();

const chartData = computed(() => {
  const sortedData = [...props.data].sort((a, b) => b.count - a.count).slice(0, 5);
  
  return {
    labels: sortedData.map(item => item.type),
    datasets: [
      {
        label: 'Ocurrencias',
        data: sortedData.map(item => item.count),
        backgroundColor: sortedData.map(item => {
          switch (item.severity) {
            case 'high': return 'rgba(239, 68, 68, 0.7)';
            case 'medium': return 'rgba(245, 158, 11, 0.7)';
            case 'low': return 'rgba(59, 130, 246, 0.7)';
            default: return 'rgba(107, 114, 128, 0.7)';
          }
        }),
        borderWidth: 0
      }
    ]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y' as const,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: function(context: any) {
          return `Ocurrencias: ${context.raw}`;
        }
      }
    }
  },
  scales: {
    x: {
      beginAtZero: true,
      ticks: {
        precision: 0
      }
    }
  }
};
</script>