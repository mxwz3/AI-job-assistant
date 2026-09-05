<script setup>
import { ref, watch, nextTick, computed, onMounted } from 'vue'
import { marked } from 'marked'
import { sendChatMessage } from '../api/chat.js'

const props = defineProps({
  context: {
    type: Object,
    default: () => ({}),
  },
})

const messages = ref([
  {
    role: 'assistant',
    content: '你好！我是你的 AI 求职顾问。可以帮你优化简历、准备面试、分析岗位匹配度。',
  },
])
const input = ref('')
const loading = ref(false)
const error = ref('')
const messagesRef = ref(null)

const MIN_WIDTH = 320
const MAX_WIDTH = 600
const DEFAULT_WIDTH = 360
const STORAGE_KEY = 'ai-assistant-width'
const COLLAPSE_KEY = 'ai-assistant-collapsed'

const panelWidth = ref(DEFAULT_WIDTH)
const collapsed = ref(false)
const isResizing = ref(false)

onMounted(() => {
  const savedWidth = parseInt(localStorage.getItem(STORAGE_KEY), 10)
  if (!isNaN(savedWidth) && savedWidth >= MIN_WIDTH && savedWidth <= MAX_WIDTH) {
    panelWidth.value = savedWidth
  }
  const savedCollapsed = localStorage.getItem(COLLAPSE_KEY)
  collapsed.value = savedCollapsed === 'true'
  // 移动端默认收起为悬浮按钮，避免全屏面板遮挡内容
  if (window.matchMedia('(max-width: 767px)').matches) {
    collapsed.value = true
  }
})

function startResize(event) {
  isResizing.value = true
  const startX = event.clientX
  const startWidth = panelWidth.value

  function onMouseMove(e) {
    const delta = startX - e.clientX
    let newWidth = startWidth + delta
    newWidth = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, newWidth))
    panelWidth.value = newWidth
  }

  function onMouseUp() {
    isResizing.value = false
    localStorage.setItem(STORAGE_KEY, String(panelWidth.value))
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

function toggleCollapse() {
  collapsed.value = !collapsed.value
  localStorage.setItem(COLLAPSE_KEY, String(collapsed.value))
}

const hasResume = computed(() => !!props.context?.resume?.trim())
const hasJd = computed(() => !!props.context?.jd?.trim())
const hasMatch = computed(() => !!props.context?.matchAnalysis)
const hasOptimization = computed(() =>
  (props.context?.optimizationSuggestions?.length || 0) > 0
)
const hasOptimizedResume = computed(() => !!props.context?.optimizedResume)

const quickQuestions = computed(() => {
  if (!hasResume.value) {
    return ['简历应该包含哪些内容？', '如何写出更好的项目经历？']
  }
  if (!hasJd.value) {
    return [
      '我的简历最大的优势是什么？',
      '我的简历有哪些问题？',
      '如何改进我的技能描述？',
    ]
  }
  if (!hasMatch.value) {
    return [
      '这个岗位最看重什么？',
      '我还需要补充哪些技能？',
      '我的简历和这个岗位匹配吗？',
    ]
  }
  const list = [
    '我的简历最需要改哪三处？',
    `为什么只有${props.context.matchAnalysis.matchScore}%匹配？`,
    '帮我修改这个项目经历',
    '这个岗位面试可能问什么？',
  ]
  if (hasOptimization.value) {
    list.push('这些优化建议会不会有夸大的问题？')
  }
  if (hasOptimizedResume.value) {
    list.push('刚才修改了什么？')
    list.push('这段修改是不是太夸张了？')
  }
  if (props.context?.optimizedMatchScore != null) {
    list.push(`为什么优化后匹配度是${props.context.optimizedMatchScore}%？`)
  }
  if (props.context?.currentSection === 'section-optimized-resume') {
    list.push('帮我再优化一下这个自我评价')
  }
  return list
})

function renderMarkdown(text) {
  return marked.parse(text || '', { breaks: true })
}

function resumeInfoToText(info) {
  if (!info) return ''
  const parts = []
  if (info.name) parts.push(`姓名：${info.name}`)
  if (info.school || info.major) {
    parts.push(`教育背景：${[info.school, info.major].filter(Boolean).join(' ')}`)
  }
  if (info.skills?.length) parts.push(`技能：${info.skills.join('、')}`)
  if (info.projects?.length) {
    parts.push('项目经历：')
    info.projects.forEach((p) => parts.push(`- ${p}`))
  }
  if (info.selfEvaluation) parts.push(`自我评价：${info.selfEvaluation}`)
  return parts.join('\n')
}

watch(messages, () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}, { deep: true })

// 收到外部问题时自动展开并复用现有发送流程
watch(
  () => props.pendingQuestion,
  (q) => {
    const text = q?.text?.trim()
    if (!text) return
    collapsed.value = false
    handleSend(text)
  }
)

async function handleSend(text = null) {
  const question = (text || input.value).trim()
  if (!question || loading.value) return

  messages.value.push({ role: 'user', content: question })
  input.value = ''
  error.value = ''
  loading.value = true

  try {
    const history = messages.value.slice(0, -1).map((m) => ({
      role: m.role,
      content: m.content,
    }))

    const data = await sendChatMessage({
      message: question,
      resume: props.context.resume || '',
      originalResume: props.context.originalResume
        ? resumeInfoToText(props.context.originalResume)
        : '',
      optimizedResume: props.context.optimizedResume
        ? resumeInfoToText(props.context.optimizedResume)
        : '',
      jd: props.context.jd || '',
      matchResult: props.context.matchAnalysis || null,
      optimizedMatchResult: props.context.optimizedMatchAnalysis || null,
      originalMatchScore: props.context.originalMatchScore ?? null,
      optimizedMatchScore: props.context.optimizedMatchScore ?? null,
      history,
    })

    messages.value.push({ role: 'assistant', content: data.answer })
  } catch (err) {
    error.value = err.message || 'AI 回复失败，请重试'
    messages.value.push({
      role: 'assistant',
      content: '抱歉，刚才出了点问题，请稍后再试。',
    })
  } finally {
    loading.value = false
  }
}

function sendQuick(question) {
  handleSend(question)
}

function handleKeyDown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}

function adjustHeight(event) {
  const el = event.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}
</script>

<template>
  <aside
    class="chat-assistant"
    :class="{ collapsed, resizing: isResizing }"
    :style="collapsed ? { width: '48px' } : { width: panelWidth + 'px' }"
  >
    <div v-if="!collapsed" class="resize-handle" @mousedown="startResize"></div>

    <div v-if="collapsed" class="collapsed-bar" @click="toggleCollapse">
      <div class="collapsed-label">AI</div>
    </div>

    <template v-else>
      <header class="chat-header">
        <div class="header-left">
          <h2>AI 助手</h2>
          <div class="context-status">
            <span v-if="!hasResume" class="status-dot empty">未上传简历</span>
            <span v-else-if="!hasJd" class="status-dot partial">已上传简历</span>
            <span v-else-if="!hasMatch" class="status-dot partial">已输入 JD</span>
            <span v-else class="status-dot ready">分析完成</span>
          </div>
        </div>
        <button class="collapse-btn" title="收起" @click="toggleCollapse">
          ››
        </button>
      </header>

      <div class="quick-actions">
      <button
        v-for="q in quickQuestions"
        :key="q"
        class="quick-btn"
        @click="sendQuick(q)"
        :disabled="loading"
      >
        {{ q }}
      </button>
    </div>

    <div ref="messagesRef" class="messages">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.role]"
      >
        <div
          v-if="msg.role === 'assistant'"
          class="bubble markdown-body"
          v-html="renderMarkdown(msg.content)"
        ></div>
        <div v-else class="bubble">{{ msg.content }}</div>
      </div>
      <div v-if="loading" class="message assistant">
        <div class="bubble loading">AI 思考中...</div>
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div class="input-area">
      <textarea
        v-model="input"
        placeholder="有问题随时问我...（Shift+Enter换行）"
        @keydown="handleKeyDown"
        @input="adjustHeight"
        :disabled="loading"
        rows="1"
      ></textarea>
      <button
        class="send-btn"
        @click="handleSend()"
        :disabled="!input.trim() || loading"
      >
        发送
      </button>
    </div>
    </template>
  </aside>
</template>

<style scoped>
.chat-assistant {
  background: #fff;
  border-left: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  height: 100vh;
  flex-shrink: 0;
  position: relative;
  transition: width 0.2s ease;
  overflow: hidden;
}

.chat-assistant.resizing {
  transition: none;
  user-select: none;
}

.chat-assistant.collapsed {
  width: 48px;
  cursor: pointer;
}

.resize-handle {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  cursor: col-resize;
  background: transparent;
  z-index: 10;
}

.resize-handle:hover,
.chat-assistant.resizing .resize-handle {
  background: rgba(59, 130, 246, 0.25);
}

.collapsed-bar {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  writing-mode: vertical-rl;
  text-orientation: mixed;
}

.collapsed-label {
  font-size: 14px;
  font-weight: 700;
  color: #2563eb;
  letter-spacing: 2px;
  padding: 16px 0;
}

.chat-header {
  padding: 16px 20px 16px 22px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.chat-header h2 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
}

.context-status {
  font-size: 12px;
}

.collapse-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: #6b7280;
  font-size: 18px;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapse-btn:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.status-dot {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
}

.status-dot::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-dot.empty::before {
  background: #ef4444;
}

.status-dot.partial::before {
  background: #f59e0b;
}

.status-dot.ready::before {
  background: #10b981;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.quick-btn {
  padding: 6px 12px;
  font-size: 13px;
  color: #2563eb;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 16px;
  cursor: pointer;
}

.quick-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 90%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.message.user .bubble {
  background: #3b82f6;
  color: #fff;
  border-bottom-right-radius: 4px;
  white-space: pre-wrap;
}

.message.assistant .bubble {
  background: #f3f4f6;
  color: #1f2937;
  border-bottom-left-radius: 4px;
}

.bubble.loading {
  color: #6b7280;
}

.error {
  padding: 0 16px 8px;
  color: #ef4444;
  font-size: 13px;
}

.input-area {
  display: flex;
  gap: 8px;
  padding: 12px 16px 16px;
  border-top: 1px solid #e5e7eb;
  align-items: flex-end;
}

.input-area textarea {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  min-height: 40px;
  max-height: 120px;
  font-family: inherit;
}

.input-area textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

.send-btn {
  padding: 10px 18px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  height: 40px;
}

.send-btn:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

.markdown-body :deep(p) {
  margin: 0 0 8px;
}

.markdown-body :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0 0 8px;
  padding-left: 18px;
}

.markdown-body :deep(li) {
  margin-bottom: 4px;
}

.markdown-body :deep(strong) {
  color: #111827;
}

.markdown-body :deep(code) {
  background: #e5e7eb;
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 13px;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin: 12px 0 8px;
  font-size: 15px;
  color: #111827;
}

/* 移动端：收起时为右下角悬浮按钮，展开时为全屏浮层（覆盖内联拖拽宽度） */
@media (max-width: 767px) {
  /* 收起态：右下角胶囊悬浮按钮，不遮挡内容、不阻止页面滑动 */
  .chat-assistant.collapsed {
    position: fixed;
    top: auto;
    right: 16px;
    bottom: 20px;
    left: auto;
    width: auto !important;
    height: auto;
    z-index: 90;
    border-radius: 999px;
    border: none;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35);
    background: #2563eb;
    cursor: pointer;
  }

  .chat-assistant.collapsed .collapsed-bar {
    writing-mode: horizontal-tb;
    padding: 12px 18px;
    background: transparent;
  }

  .chat-assistant.collapsed .collapsed-label {
    color: #fff;
    font-size: 14px;
    letter-spacing: 0;
    padding: 0;
    white-space: nowrap;
  }

  .chat-assistant.collapsed .collapsed-label::before {
    content: '🤖 ';
  }

  /* 展开态：全屏浮层 */
  .chat-assistant {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    width: 100% !important;
    height: 100vh;
    height: 100dvh;
    z-index: 100;
    border-left: none;
    box-shadow: -2px 0 16px rgba(0, 0, 0, 0.15);
  }

  .resize-handle {
    display: none;
  }

  .chat-header {
    padding: 12px 14px;
  }

  .quick-actions {
    padding: 10px 12px;
  }

  .messages {
    padding: 12px;
  }

  .bubble {
    max-width: 95%;
  }

  .input-area {
    padding: 10px 12px 14px;
  }
}
</style>
