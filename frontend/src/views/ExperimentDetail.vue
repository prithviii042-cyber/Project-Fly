<template>
  <div class="page">
    <div v-if="loading" class="center-msg">Loading...</div>
    <template v-else-if="exp">
      <!-- Header -->
      <div class="page-header">
        <div>
          <router-link to="/" class="back-link">← All experiments</router-link>
          <h1>{{ exp.name }}</h1>
          <p v-if="exp.goal" class="goal">Goal: {{ exp.goal }}</p>
        </div>
        <div class="header-actions">
          <select :value="exp.status" @change="changeStatus($event.target.value)" class="status-select">
            <option value="running">Running</option>
            <option value="paused">Paused</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      <!-- Variants -->
      <div class="variants-grid">
        <div
          v-for="(v, i) in exp.variants"
          :key="v.id"
          :class="['variant-card', { winner: isWinner(v) }]"
        >
          <div class="variant-header">
            <span class="variant-label">{{ v.name }}</span>
            <span v-if="isWinner(v)" class="winner-badge">🏆 Leading</span>
          </div>

          <blockquote class="variant-content">{{ v.content }}</blockquote>

          <div class="stats-row">
            <div class="stat">
              <span class="stat-value">{{ v.views }}</span>
              <span class="stat-label">Views</span>
            </div>
            <div class="stat">
              <span class="stat-value">{{ v.conversions }}</span>
              <span class="stat-label">Conversions</span>
            </div>
            <div class="stat highlight">
              <span class="stat-value">{{ convRate(v).toFixed(1) }}%</span>
              <span class="stat-label">Conv. rate</span>
            </div>
          </div>

          <!-- Progress bar -->
          <div class="bar-wrap">
            <div class="bar" :style="{ width: convRate(v) + '%' }" />
          </div>

          <!-- Simulate buttons -->
          <div class="sim-buttons">
            <button class="btn-sim" @click="trackView(v)">+ View</button>
            <button class="btn-sim convert" @click="trackConvert(v)">+ Convert</button>
          </div>
        </div>
      </div>

      <!-- Add variant -->
      <div class="add-variant-row">
        <div v-if="showAddVariant" class="add-variant-form">
          <input v-model="newVariant.name" placeholder="Variant name" />
          <textarea v-model="newVariant.content" rows="2" placeholder="Content / copy" />
          <div class="add-variant-actions">
            <button class="btn-ghost" @click="showAddVariant = false">Cancel</button>
            <button class="btn-primary" @click="addVariant" :disabled="!newVariant.content.trim()">Add</button>
          </div>
        </div>
        <button v-else class="btn-ghost" @click="showAddVariant = true">+ Add variant</button>
      </div>

      <!-- Claude Analysis -->
      <div class="analysis-section">
        <div class="analysis-header">
          <h2>✨ Claude Analysis</h2>
          <button
            class="btn-ai"
            :disabled="analyzing || exp.variants.length < 2"
            @click="analyze"
          >
            {{ analyzing ? 'Analyzing...' : 'Analyze results' }}
          </button>
        </div>

        <div v-if="analysis" class="analysis-body">
          <pre>{{ analysis }}</pre>
        </div>
        <p v-else class="analysis-hint">
          {{ exp.variants.length < 2 ? 'Add at least 2 variants to analyze.' : 'Click "Analyze results" to get Claude\'s recommendation.' }}
        </p>
      </div>
    </template>

    <div v-else class="center-msg">Experiment not found.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/index.js'

const route = useRoute()
const exp = ref(null)
const loading = ref(true)
const analyzing = ref(false)
const analysis = ref('')
const showAddVariant = ref(false)
const newVariant = ref({ name: '', content: '' })

async function load() {
  try {
    exp.value = await api.getExperiment(route.params.id)
  } finally {
    loading.value = false
  }
}

function convRate(v) {
  if (!v.views) return 0
  return v.conversions / v.views * 100
}

function isWinner(v) {
  if (!exp.value?.variants?.length || exp.value.variants.length < 2) return false
  const best = [...exp.value.variants].sort((a, b) => convRate(b) - convRate(a))[0]
  return best.id === v.id && convRate(v) > 0
}

async function trackView(v) {
  await api.trackView(exp.value.id, v.id)
  v.views++
}

async function trackConvert(v) {
  await api.trackConversion(exp.value.id, v.id)
  v.conversions++
  v.views++
}

async function changeStatus(status) {
  await api.updateStatus(exp.value.id, status)
  exp.value.status = status
}

async function addVariant() {
  if (!newVariant.value.content.trim()) return
  const letter = String.fromCharCode(65 + exp.value.variants.length)
  const v = await api.addVariant(exp.value.id, {
    name: newVariant.value.name || `Variant ${letter}`,
    content: newVariant.value.content
  })
  exp.value.variants.push(v)
  newVariant.value = { name: '', content: '' }
  showAddVariant.value = false
}

async function analyze() {
  analyzing.value = true
  analysis.value = ''
  try {
    const res = await api.analyzeExperiment(exp.value.id)
    analysis.value = res.analysis
  } catch (e) {
    analysis.value = `Error: ${e.message}`
  } finally {
    analyzing.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page { max-width: 900px; margin: 0 auto; padding: 32px 20px; }

.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 28px; }
.page-header h1 { font-size: 22px; font-weight: 700; margin: 6px 0 4px; }
.back-link { color: #666; font-size: 13px; text-decoration: none; }
.back-link:hover { color: #aaa; }
.goal { font-size: 13px; color: #666; }

.status-select {
  background: #1a1a1a; border: 1px solid #333; color: #f0f0f0;
  border-radius: 8px; padding: 8px 12px; font-size: 13px; cursor: pointer;
}

.variants-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; margin-bottom: 16px; }

.variant-card {
  background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px; padding: 18px;
  transition: border-color 0.2s;
}
.variant-card.winner { border-color: #3a7bd5; }

.variant-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.variant-label { font-size: 13px; font-weight: 600; color: #7cb9ff; }
.winner-badge { font-size: 11px; color: #4ade80; }

.variant-content {
  font-size: 14px; color: #ccc; border-left: 3px solid #333; padding-left: 12px;
  margin: 0 0 16px; line-height: 1.5; white-space: pre-wrap; word-break: break-word;
}

.stats-row { display: flex; gap: 12px; margin-bottom: 12px; }
.stat { flex: 1; text-align: center; }
.stat-value { display: block; font-size: 22px; font-weight: 700; }
.stat-label { font-size: 11px; color: #666; }
.stat.highlight .stat-value { color: #3a7bd5; }

.bar-wrap { background: #2a2a2a; border-radius: 99px; height: 6px; overflow: hidden; margin-bottom: 14px; }
.bar { height: 100%; background: #3a7bd5; border-radius: 99px; transition: width 0.4s; max-width: 100%; }

.sim-buttons { display: flex; gap: 8px; }
.btn-sim {
  flex: 1; background: #1e1e1e; border: 1px solid #333; color: #aaa;
  border-radius: 6px; padding: 7px; font-size: 12px; cursor: pointer; transition: all 0.2s;
}
.btn-sim:hover { background: #2a2a2a; border-color: #555; }
.btn-sim.convert { color: #4ade80; border-color: #1a3a2a; }
.btn-sim.convert:hover { background: #0d2a1a; }

.add-variant-row { margin-bottom: 28px; }
.add-variant-form {
  background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 16px;
  display: flex; flex-direction: column; gap: 10px;
}
.add-variant-form input, .add-variant-form textarea {
  background: #111; border: 1px solid #333; color: #f0f0f0;
  border-radius: 8px; padding: 10px 12px; font-size: 14px;
  font-family: inherit; outline: none; resize: vertical;
}
.add-variant-form input:focus, .add-variant-form textarea:focus { border-color: #3a7bd5; }
.add-variant-actions { display: flex; justify-content: flex-end; gap: 8px; }

.analysis-section {
  background: #111827; border: 1px solid #1e3a5f; border-radius: 12px; padding: 20px;
}
.analysis-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.analysis-header h2 { font-size: 15px; font-weight: 600; }

.btn-ai {
  background: #1e3a5f; color: #7cb9ff; border: 1px solid #2d5a8e;
  border-radius: 8px; padding: 8px 16px; font-size: 13px; cursor: pointer;
}
.btn-ai:hover:not(:disabled) { background: #2d5a8e; }
.btn-ai:disabled { opacity: 0.4; cursor: not-allowed; }

.analysis-body pre {
  white-space: pre-wrap; font-family: inherit; font-size: 14px;
  color: #ccc; line-height: 1.6;
}
.analysis-hint { font-size: 13px; color: #555; }

.center-msg { text-align: center; padding: 60px; color: #555; }
</style>
