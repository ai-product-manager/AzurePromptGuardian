import { createRouter, createWebHistory } from 'vue-router'
import PromptGuardian from '../components/PromptGuardian.vue'
import Dashboard from '../components/Dashboard.vue'

const routes = [
  {
    path: '/',
    redirect: '/analyze'
  },
  {
    path: '/analyze',
    name: 'Analyze',
    component: PromptGuardian,
    meta: { title: 'Análisis de Prompts' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: 'Dashboard de Analytics' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title} | Azure Prompt Guardian`
  next()
})

export default router