<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>A/B Tests</h1>
        <p class="subtitle">{{ experiments.length }} experiment{{ experiments.length !== 1 ? 's' : '' }}</p>
      </div>
      <router-link to="/new" class="btn-primary">+ New Experiment</router-link>
    </div>

    <div v-if="loading" class="center-msg">Loading...</div>
    <div v-else-if="experiments.length === 0" class="empty-state">
      <div class="empty-icon">⚗️</div>
      <p>No experiments yet.</p>
      <router-link to="/new" class="btn-primary">Create your first test</router-link>
    </div>

    <div v-else class="cards">
      <div
        v-for="exp in experiments"
        :key="exp.id"
        class="card"
        @click="$router.push(`/experiments/${exp.id}`)"
      >
        <div class="card-top">
          <span :class="['status-badge', exp.status]">{{ exp.status }}</span>
          <button class="delete-btn" @click.stop="deleteExp(exp.id)">✕</button>
        </div>
        <h2>{{ exp.name }}</h2>
        <p class="goal">{{ exp.goal || 'No goal set' }}</p>

        <div class="card-stats">
          <div v-for="v in exp.variants" :key="v.id" class="variant-row">
            <span class="variant-name">{{ v.name }}</span>
            <div class="bar-wrap">
              <div class="bar" :style="{ width: convRate(v) + '%' }" />
            </div>
            <span class="rate">{{ convRate(v).toFixed(1) }}%</span>
          </div>
          <p v-if="exp.variants.length === 0" class="no-variants">No variants yet</p>
        </div>

        <div class="card-footer">
          <span>{{ exp.variants.length }} variant{{ exp.variants.length !== 1 ? 's' : '' }}</span>
          <span>{{ totalViews(exp) }} views</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api/index.js'

const experiments = ref([])
const loading = ref(true)

async function load() {
  try {
    experiments.value = await api.listExperiments()
  } finally {
    loading.value = false
  }
}

async function deleteExp(id) {
  if (!confirm('Delete this experiment?')) return
  await api.deleteExperiment(id)
  experiments.value = experiments.value.filter(e => e.id !== id)
}

function convRate(v) {
  if (!v.views) return 0
  return v.conversions / v.views * 100
}

function totalViews(exp) {
  return exp.variants.reduce((s, v) => s + v.views, 0)
}

onMounted(load)
</script>

<style scoped>
.page { max-width: 960px; margin: 0 auto; padding: 32px 20px; }

.page-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 28px;
}
.page-header h1 { font-size: 24px; font-weight: 700; }
.subtitle { color: #666; font-size: 13px; margin-top: 2px; }

.empty-state {
  text-align: center; padding: 80px 20px; color: #555;
}
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-state p { margin-bottom: 16px; }

.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }

.card {
  background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px;
  padding: 18px; cursor: pointer; transition: border-color 0.2s;
}
.card:hover { border-color: #3a7bd5; }

.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.card h2 { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.goal { font-size: 12px; color: #666; margin-bottom: 14px; }

.status-badge {
  font-size: 11px; padding: 2px 8px; border-radius: 99px; font-weight: 500;
}
.status-badge.running { background: #0d3320; color: #4ade80; }
.status-badge.paused  { background: #2a2000; color: #facc15; }
.status-badge.completed { background: #1e1e1e; color: #aaa; }

.delete-btn {
  background: none; border: none; color: #555; cursor: pointer;
  font-size: 12px; padding: 2px 6px; border-radius: 4px;
}
.delete-btn:hover { background: #2a2a2a; color: #f87171; }

.card-stats { margin-bottom: 14px; }
.variant-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.variant-name { font-size: 12px; color: #aaa; width: 70px; flex-shrink: 0; }
.bar-wrap { flex: 1; background: #2a2a2a; border-radius: 99px; height: 6px; overflow: hidden; }
.bar { height: 100%; background: #3a7bd5; border-radius: 99px; transition: width 0.4s; }
.rate { font-size: 12px; color: #aaa; width: 36px; text-align: right; }
.no-variants { font-size: 12px; color: #555; }

.card-footer {
  display: flex; justify-content: space-between;
  font-size: 11px; color: #555; border-top: 1px solid #2a2a2a; padding-top: 10px;
}
</style>
