<template>
  <div class="page">
    <div class="page-header">
      <router-link to="/" class="back-link">← Back</router-link>
      <h1>New Experiment</h1>
    </div>

    <div class="form-card">
      <!-- Experiment details -->
      <section>
        <h2>Details</h2>
        <label>Name *
          <input v-model="form.name" placeholder="e.g. Homepage headline test" />
        </label>
        <label>Goal
          <input v-model="form.goal" placeholder="e.g. Increase sign-up clicks" />
        </label>
        <label>Description
          <textarea v-model="form.description" rows="2" placeholder="What are you testing and why?" />
        </label>
      </section>

      <!-- AI variant generator -->
      <section class="ai-section">
        <h2>✨ Generate variants with Claude</h2>
        <p class="hint">Describe what you want to test and Claude will write two variants for you.</p>
        <label>What are you testing?
          <input v-model="aiPrompt" placeholder="e.g. CTA button text for a SaaS sign-up page" />
        </label>
        <button class="btn-ai" :disabled="aiLoading || !aiPrompt.trim()" @click="generateVariants">
          {{ aiLoading ? 'Generating...' : '✨ Generate variants' }}
        </button>
        <p v-if="aiError" class="error">{{ aiError }}</p>
      </section>

      <!-- Variants -->
      <section>
        <div class="variants-header">
          <h2>Variants</h2>
          <button class="btn-ghost" @click="addVariant">+ Add variant</button>
        </div>

        <div v-for="(v, i) in form.variants" :key="i" class="variant-block">
          <div class="variant-title">
            <span>Variant {{ String.fromCharCode(65 + i) }}</span>
            <button class="delete-btn" @click="removeVariant(i)" v-if="form.variants.length > 1">✕</button>
          </div>
          <label>Name
            <input v-model="v.name" :placeholder="`Variant ${String.fromCharCode(65 + i)}`" />
          </label>
          <label>Content
            <textarea v-model="v.content" rows="3" placeholder="The actual copy, headline, or description to test" />
          </label>
        </div>
      </section>

      <div class="form-footer">
        <router-link to="/" class="btn-ghost">Cancel</router-link>
        <button class="btn-primary" :disabled="saving || !form.name.trim()" @click="save">
          {{ saving ? 'Creating...' : 'Create experiment' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/index.js'

const router = useRouter()

const form = ref({
  name: '',
  goal: '',
  description: '',
  variants: [
    { name: 'Variant A', content: '' },
    { name: 'Variant B', content: '' }
  ]
})

const aiPrompt = ref('')
const aiLoading = ref(false)
const aiError = ref('')
const saving = ref(false)

function addVariant() {
  const letter = String.fromCharCode(65 + form.value.variants.length)
  form.value.variants.push({ name: `Variant ${letter}`, content: '' })
}

function removeVariant(i) {
  form.value.variants.splice(i, 1)
}

async function generateVariants() {
  aiError.value = ''
  aiLoading.value = true
  try {
    const res = await api.generateVariants({
      description: aiPrompt.value,
      goal: form.value.goal,
      context: form.value.description
    })
    form.value.variants = res.variants
    if (!form.value.name) form.value.name = aiPrompt.value
  } catch (e) {
    aiError.value = e.message
  } finally {
    aiLoading.value = false
  }
}

async function save() {
  saving.value = true
  try {
    const exp = await api.createExperiment({
      name: form.value.name,
      goal: form.value.goal,
      description: form.value.description,
      variants: form.value.variants.filter(v => v.content.trim())
    })
    router.push(`/experiments/${exp.id}`)
  } catch (e) {
    alert(e.message)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page { max-width: 680px; margin: 0 auto; padding: 32px 20px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 22px; font-weight: 700; margin-top: 8px; }
.back-link { color: #666; font-size: 13px; text-decoration: none; }
.back-link:hover { color: #aaa; }

.form-card { display: flex; flex-direction: column; gap: 28px; }

section h2 { font-size: 14px; font-weight: 600; color: #aaa; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 14px; }

label {
  display: flex; flex-direction: column; gap: 6px;
  font-size: 13px; color: #bbb; margin-bottom: 12px;
}

input, textarea {
  background: #1a1a1a; border: 1px solid #333; border-radius: 8px;
  color: #f0f0f0; padding: 10px 12px; font-size: 14px; font-family: inherit;
  outline: none; transition: border-color 0.2s; resize: vertical;
}
input:focus, textarea:focus { border-color: #3a7bd5; }

.ai-section { background: #111827; border: 1px solid #1e3a5f; border-radius: 12px; padding: 18px; }
.hint { font-size: 12px; color: #7cb9ff; margin-bottom: 14px; }

.btn-ai {
  background: #1e3a5f; color: #7cb9ff; border: 1px solid #2d5a8e;
  border-radius: 8px; padding: 9px 16px; font-size: 13px; cursor: pointer;
  transition: background 0.2s;
}
.btn-ai:hover:not(:disabled) { background: #2d5a8e; }
.btn-ai:disabled { opacity: 0.4; cursor: not-allowed; }

.variants-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.variants-header h2 { margin-bottom: 0; }

.variant-block {
  background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px;
  padding: 16px; margin-bottom: 12px;
}
.variant-title {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 13px; font-weight: 600; color: #7cb9ff; margin-bottom: 12px;
}
.delete-btn {
  background: none; border: none; color: #555; cursor: pointer;
  font-size: 12px; padding: 2px 6px; border-radius: 4px;
}
.delete-btn:hover { color: #f87171; background: #2a2a2a; }

.form-footer { display: flex; justify-content: flex-end; gap: 10px; padding-top: 4px; }

.error { color: #f87171; font-size: 12px; margin-top: 8px; }
</style>
