import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import CreateExperiment from '../views/CreateExperiment.vue'
import ExperimentDetail from '../views/ExperimentDetail.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Dashboard },
    { path: '/new', component: CreateExperiment },
    { path: '/experiments/:id', component: ExperimentDetail }
  ]
})
