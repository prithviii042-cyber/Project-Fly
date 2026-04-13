<template>
  <div class="chat-container">
    <header class="chat-header">
      <h1>Project Fly</h1>
      <span class="model-badge">{{ model }}</span>
    </header>

    <div class="messages" ref="messagesEl">
      <div v-if="messages.length === 0" class="empty-state">
        Send a message to start chatting with the agent.
      </div>
      <div
        v-for="(msg, i) in messages"
        :key="i"
        :class="['message', msg.role]"
      >
        <div class="bubble">{{ msg.content }}</div>
      </div>
      <div v-if="loading" class="message assistant">
        <div class="bubble loading">
          <span class="dot" /><span class="dot" /><span class="dot" />
        </div>
      </div>
    </div>

    <form class="input-bar" @submit.prevent="send">
      <textarea
        v-model="input"
        placeholder="Message the agent..."
        rows="1"
        @keydown.enter.exact.prevent="send"
        @input="autoResize"
        ref="inputEl"
      />
      <button type="submit" :disabled="loading || !input.trim()">
        Send
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const messages = ref([])
const input = ref('')
const loading = ref(false)
const model = ref('claude-sonnet-4-6')
const messagesEl = ref(null)
const inputEl = ref(null)

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const res = await fetch('/api/agent/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.error || `HTTP ${res.status}`)
    }

    const data = await res.json()
    model.value = data.model
    messages.value.push({ role: 'assistant', content: data.response })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: `Error: ${e.message}` })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

function autoResize(e) {
  e.target.style.height = 'auto'
  e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px'
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #2a2a2a;
}

.chat-header h1 {
  font-size: 18px;
  font-weight: 600;
}

.model-badge {
  font-size: 11px;
  background: #1e3a5f;
  color: #7cb9ff;
  padding: 2px 8px;
  border-radius: 99px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-state {
  text-align: center;
  color: #555;
  margin: auto;
  font-size: 14px;
}

.message {
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.user .bubble {
  background: #1e3a5f;
  color: #e8f4ff;
  border-bottom-right-radius: 4px;
}

.assistant .bubble {
  background: #1e1e1e;
  color: #e0e0e0;
  border-bottom-left-radius: 4px;
}

.loading {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 14px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #555;
  animation: pulse 1.2s infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

.input-bar {
  display: flex;
  gap: 8px;
  padding: 16px 20px;
  border-top: 1px solid #2a2a2a;
  align-items: flex-end;
}

textarea {
  flex: 1;
  background: #1e1e1e;
  border: 1px solid #333;
  border-radius: 8px;
  color: #f0f0f0;
  padding: 10px 14px;
  font-size: 14px;
  resize: none;
  outline: none;
  font-family: inherit;
  line-height: 1.5;
  transition: border-color 0.2s;
}

textarea:focus {
  border-color: #3a7bd5;
}

button {
  background: #3a7bd5;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  font-size: 14px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
  white-space: nowrap;
}

button:hover:not(:disabled) {
  background: #2d63b0;
}

button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
