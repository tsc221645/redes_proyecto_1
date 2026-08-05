<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import { api, type ChatMessage } from './api'

const sessionId = ref('')
const messages = ref<ChatMessage[]>([])
const draft = ref('')
const busy = ref(false)
const connected = ref(false)
const error = ref('')
const server = ref<'local' | 'remote'>('local')
const conversation = ref<HTMLElement | null>(null)

const canSend = computed(() => draft.value.trim().length > 0 && !busy.value && Boolean(sessionId.value))

function formatResponse(content: string): string {
  return DOMPurify.sanitize(marked.parse(content, { async: false }) as string)
}

async function startSession() {
  error.value = ''
  try {
    const session = await api.createSession()
    sessionId.value = session.session_id
    messages.value = []
  } catch (reason) {
    error.value = reason instanceof Error ? reason.message : 'No se pudo crear la sesión.'
  }
}

async function sendMessage() {
  if (!canSend.value) return
  const content = draft.value.trim()
  draft.value = ''
  messages.value.push({ role: 'user', content })
  busy.value = true
  error.value = ''
  await scrollToBottom()
  try {
    const result = await api.sendMessage(sessionId.value, content)
    messages.value.push({ role: 'assistant', content: result.response })
  } catch (reason) {
    error.value = reason instanceof Error ? reason.message : 'No se pudo obtener una respuesta.'
  } finally {
    busy.value = false
    await scrollToBottom()
  }
}

async function clearConversation() {
  if (!sessionId.value) return
  await api.deleteSession(sessionId.value)
  await startSession()
}

async function scrollToBottom() {
  await nextTick()
  if (conversation.value) conversation.value.scrollTop = conversation.value.scrollHeight
}

onMounted(async () => {
  try {
    await api.health()
    connected.value = true
    await startSession()
  } catch (reason) {
    connected.value = false
    error.value = reason instanceof Error ? reason.message : 'Backend no disponible.'
  }
})
</script>

<template>
  <main class="app-shell">
    <aside class="sidebar">
      <div class="brand"><img class="brand-logo" src="/executive-insights-logo.png" alt="Executive Insights" /><div><strong>Executive Insights</strong><small>Business intelligence</small></div></div>
      <button class="new-chat" @click="startSession">＋ Nueva conversación</button>
      <div class="sidebar-section"><span class="eyebrow">SERVIDOR</span><select v-model="server"><option value="local">Local · SQL Anywhere</option><option value="remote">Remoto · próximamente</option></select></div>
      <div class="connection"><span :class="['status-dot', { online: connected }]" />{{ connected ? 'Backend conectado' : 'Backend desconectado' }}</div>
      <button class="clear-button" @click="clearConversation">Limpiar conversación</button>
    </aside>

    <section class="workspace">
      <header class="topbar"><div><span class="eyebrow">ANÁLISIS OPERATIVO</span><h1>¿Qué necesitas saber?</h1></div><div class="user-badge">AL<span>Directivo</span></div></header>
      <div ref="conversation" class="conversation">
        <div v-if="messages.length === 0" class="welcome"><div class="welcome-icon">✦</div><h2>Decisiones más claras,<br /><em>basadas en datos.</em></h2><p>Pregunta sobre ventas, productos, clientes, marcas o márgenes.</p><div class="suggestions"><button @click="draft = '¿Cuáles fueron las ventas mensuales de 2025?'">Ventas mensuales</button><button @click="draft = '¿Qué clientes compran más productos?'">Clientes principales</button><button @click="draft = '¿Qué productos tienen mejor margen?'">Mejores márgenes</button></div></div>
        <article v-for="(message, index) in messages" :key="index" :class="['message-row', message.role]"><div class="avatar">{{ message.role === 'user' ? 'AL' : '✦' }}</div><div class="message-content"><span class="message-label">{{ message.role === 'user' ? 'TÚ' : 'EXECUTIVE INSIGHTS' }}</span><div v-if="message.role === 'assistant'" class="markdown-body" v-html="formatResponse(message.content)" /><p v-else>{{ message.content }}</p></div></article>
        <div v-if="busy" class="message-row assistant"><div class="avatar">✦</div><div class="message-content"><span class="message-label">EXECUTIVE INSIGHTS</span><p class="thinking">Analizando datos<span>.</span><span>.</span><span>.</span></p></div></div>
      </div>
      <div v-if="error" class="error-banner">{{ error }}</div>
      <form class="composer" @submit.prevent="sendMessage"><textarea v-model="draft" :disabled="busy" placeholder="Pregunta sobre la operación de tu empresa..." @keydown.enter.exact.prevent="sendMessage" /><button type="submit" :disabled="!canSend">Enviar <span>↗</span></button><small>Los resultados se basan en datos empresariales disponibles.</small></form>
    </section>
  </main>
</template>
