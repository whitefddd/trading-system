import { createRouter, createWebHistory } from 'vue-router'
import SignalList from '../components/SignalList.vue'

const routes = [
  {
    path: '/',
    redirect: '/signals'
  },
  {
    path: '/signals',
    name: 'Signals',
    component: SignalList
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 