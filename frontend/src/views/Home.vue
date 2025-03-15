<template>
    <div>
      <PromptInput @prompt-submitted="handlePromptSubmitted" />
      <PromptOutput :optimizedPrompt="optimizedPrompt" />
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  import PromptInput from '@/components/PromptInput.vue';
  import PromptOutput from '@/components/PromptOutput.vue';
  
  export default defineComponent({
    components: {
      PromptInput,
      PromptOutput
    },
    data() {
      return {
        optimizedPrompt: ''
      };
    },
    methods: {
      handlePromptSubmitted(optimizedPrompt: string) {
        this.optimizedPrompt = optimizedPrompt;
      }
    }
  });
  </script>
  
  <style scoped>
  div {
    max-width: 600px;
    margin: auto;
  }
  </style>
  