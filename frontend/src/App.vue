<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { matchResumeJd } from './api/match.js'
import { analyzeJd } from './api/analyze.js'
import Sidebar from './components/Sidebar.vue'
import ChatAssistant from './components/ChatAssistant.vue'
import JdInput from './components/JdInput.vue'
import ResumeUpload from './components/ResumeUpload.vue'
import ResumeInfo from './components/ResumeInfo.vue'
import ResumeAnalysis from './components/ResumeAnalysis.vue'
import AnalysisResult from './components/AnalysisResult.vue'
import MatchResult from './components/MatchResult.vue'
import OptimizationPanel from './components/OptimizationPanel.vue'
import OptimizedResume from './components/OptimizedResume.vue'

const jdText = ref('')
const resumeData = ref(null)
const jdAnalysis = ref(null)
const matchResult = ref(null)
const jdLoading = ref(false)
const matchLoading = ref(false)
const error = ref('')
const jdError = ref('')
const activeSection = ref('section-resume')
const appliedChanges = ref([])
const originalResume = ref(null)
const optimizedResume = ref(null)
const originalMatchScore = ref(null)
const optimizedMatchScore = ref(null)
const optimizedMatchResult = ref(null)
const isRematching = ref(false)
// 转发给右侧 AI 助手的问题（对象形式保证重复点击同一项也能触发 watch）
const assistantPrompt = ref(null)

function handleSendToAssistant(text) {
  assistantPrompt.value = { text, ts: Date.now() }
}

const resumeText = computed(() => resumeData.value?.resume_text || '')
const resumeInfo = computed(() => resumeData.value?.resume_info || null)

// 优化建议确认状态：只有全部建议都被用户确认（接受/保留/编辑）后，第 4 步才算完成
const suggestionList = computed(() => matchResult.value?.optimizationSuggestions || [])
const pendingSuggestionCount = computed(
  () => suggestionList.value.filter((s) => !s.status || s.status === 'pending').length
)
const suggestionsAllConfirmed = computed(
  () => suggestionList.value.length > 0 && pendingSuggestionCount.value === 0
)

const aiContext = computed(() => ({
  resume: resumeText.value,
  originalResume: originalResume.value,
  optimizedResume: optimizedResume.value,
  jd: jdText.value,
  resumeInfo: resumeInfo.value,
  jdAnalysis: jdAnalysis.value,
  matchAnalysis: matchResult.value,
  optimizedMatchAnalysis: optimizedMatchResult.value,
  originalMatchScore: originalMatchScore.value,
  optimizedMatchScore: optimizedMatchScore.value,
  optimizationSuggestions: matchResult.value?.optimizationSuggestions || [],
  appliedChanges: appliedChanges.value,
  currentSection: activeSection.value,
}))

const sections = [
  { id: 'section-resume', label: '简历' },
  { id: 'section-jd', label: 'JD' },
  { id: 'section-match', label: '匹配分析' },
  { id: 'section-optimization', label: '优化建议' },
  { id: 'section-optimized-resume', label: '优化后简历' },
]

const sectionRefs = {}

function setSectionRef(el, id) {
  if (el) {
    sectionRefs[id] = el
  }
}

function scrollToSection(id) {
  activeSection.value = id
  const el = sectionRefs[id]
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

let observer = null

onMounted(() => {
  restoreState()
  // 移动端内容区不再是独立滚动容器，观察器以浏览器视口为 root
  const isMobile = window.matchMedia('(max-width: 767px)').matches
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          activeSection.value = entry.target.id
        }
      })
    },
    {
      root: isMobile ? null : document.querySelector('.content-scroll'),
      rootMargin: '-5% 0px -80% 0px',
      threshold: 0,
    }
  )

  sections.forEach(({ id }) => {
    const el = sectionRefs[id]
    if (el) observer.observe(el)
  })
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})

function deepClone(obj) {
  return obj ? JSON.parse(JSON.stringify(obj)) : null
}

function handleResumeUpdate(data) {
  resumeData.value = data
  originalResume.value = deepClone(data?.resume_info)
  optimizedResume.value = deepClone(data?.resume_info)
  matchResult.value = null
  jdAnalysis.value = null
  appliedChanges.value = []
  originalMatchScore.value = null
  optimizedMatchScore.value = null
  optimizedMatchResult.value = null
  error.value = ''
  jdError.value = ''
}

function handleResetResume() {
  resumeData.value = null
  originalResume.value = null
  optimizedResume.value = null
  matchResult.value = null
  jdAnalysis.value = null
  appliedChanges.value = []
  originalMatchScore.value = null
  optimizedMatchScore.value = null
  optimizedMatchResult.value = null
  error.value = ''
  jdError.value = ''
  sessionStorage.removeItem(STORAGE_KEY)
}

async function handleJdAnalyze() {
  if (!jdText.value.trim()) {
    jdError.value = '请先粘贴招聘 JD'
    return
  }

  jdLoading.value = true
  jdError.value = ''
  jdAnalysis.value = null

  try {
    jdAnalysis.value = await analyzeJd(jdText.value.trim())
  } catch (err) {
    jdError.value = err.message || 'JD 分析失败，请稍后重试'
  } finally {
    jdLoading.value = false
  }
}

// 将 AI 返回的建议标准化：补齐 id / status / type 等前端状态字段
function normalizeSuggestions(result) {
  const list = result?.optimizationSuggestions || []
  list.forEach((s, i) => {
    if (!s.id) s.id = `sg-${i + 1}`
    if (!s.type) s.type = 'modify'
    if (!s.status) s.status = 'pending'
  })
  return result
}

async function handleMatchAnalyze() {
  if (!jdText.value.trim()) {
    error.value = '请先粘贴招聘 JD'
    return
  }
  if (!resumeText.value) {
    error.value = '请先上传简历'
    return
  }

  matchLoading.value = true
  error.value = ''
  matchResult.value = null

  try {
    matchResult.value = normalizeSuggestions(
      await matchResumeJd(resumeText.value, jdText.value.trim())
    )
    originalMatchScore.value = matchResult.value?.matchScore ?? null
    optimizedMatchScore.value = null
    optimizedMatchResult.value = null
  } catch (err) {
    error.value = err.message || '匹配分析失败，请稍后重试'
  } finally {
    matchLoading.value = false
  }
}

// 仅在用户确认后写入 optimizedResume；支持 itemIndex 精确定位与 add/delete 类型
function updateOptimizedField(field, before, after, itemIndex, type) {
  if (!optimizedResume.value || !field) return

  const current = optimizedResume.value[field]

  if (Array.isArray(current)) {
    let updated = [...current]

    if (type === 'add') {
      updated.push(after)
    } else if (type === 'delete') {
      const idx = resolveItemIndex(current, before, itemIndex)
      if (idx >= 0) updated.splice(idx, 1)
    } else {
      // modify / enhance：优先 itemIndex，退化为 before 前缀模糊匹配
      const idx = resolveItemIndex(current, before, itemIndex)
      if (idx >= 0) {
        updated[idx] = after
      } else if (after) {
        updated.push(after)
      }
    }

    optimizedResume.value = { ...optimizedResume.value, [field]: updated }
  } else if (typeof current === 'string' || current == null) {
    if (type !== 'delete') {
      optimizedResume.value = { ...optimizedResume.value, [field]: after }
    }
  }
}

function resolveItemIndex(list, before, itemIndex) {
  if (Number.isInteger(itemIndex) && itemIndex >= 0 && itemIndex < list.length) {
    return itemIndex
  }
  if (before) {
    return list.findIndex((item) =>
      String(item).includes(String(before).slice(0, 20))
    )
  }
  return -1
}

function getSuggestion(index) {
  return matchResult.value?.optimizationSuggestions?.[index]
}

function recordChange(suggestion, status, finalAfter) {
  appliedChanges.value.push({
    type: 'ai',
    status, // accepted / edited / kept
    index: suggestion.id,
    field: suggestion.field || 'projects',
    suggestionType: suggestion.type || 'modify',
    before: suggestion.before,
    after: finalAfter,
    acceptedAt: Date.now(),
  })
}

// 接受修改：写入 optimizedResume
function handleApplyChange({ index, after }) {
  const suggestion = getSuggestion(index)
  if (!suggestion || suggestion.status === 'accepted') return

  const finalAfter = after || suggestion.after
  suggestion.status = 'accepted'
  suggestion.after = finalAfter

  recordChange(suggestion, 'accepted', finalAfter)
  updateOptimizedField(
    suggestion.field || 'projects',
    suggestion.before,
    finalAfter,
    suggestion.itemIndex,
    suggestion.type
  )
}

// 保留原文：不修改 optimizedResume，只记录用户决策
function handleKeepChange(index) {
  const suggestion = getSuggestion(index)
  if (!suggestion || suggestion.status === 'kept') return

  suggestion.status = 'kept'
  recordChange(suggestion, 'kept', suggestion.before)
}

// 用户编辑建议后确认：以用户编辑内容为谁，写入 optimizedResume
function handleEditConfirm({ index, after }) {
  const suggestion = getSuggestion(index)
  if (!suggestion || !after) return

  suggestion.status = 'edited'
  suggestion.after = after

  recordChange(suggestion, 'edited', after)
  updateOptimizedField(
    suggestion.field || 'projects',
    suggestion.before,
    after,
    suggestion.itemIndex,
    suggestion.type
  )
}

function handleBatchApply() {
  const list = matchResult.value?.optimizationSuggestions || []
  list.forEach((_, index) => {
    const s = getSuggestion(index)
    if (s && s.status === 'pending') {
      handleApplyChange({ index })
    }
  })
}

function handleBatchKeep() {
  const list = matchResult.value?.optimizationSuggestions || []
  list.forEach((_, index) => {
    const s = getSuggestion(index)
    if (s && s.status === 'pending') {
      handleKeepChange(index)
    }
  })
}

function handleManualEdit({ field, before, after }) {
  if (!optimizedResume.value) return

  appliedChanges.value.push({
    type: 'manual',
    status: 'manual',
    field,
    before,
    after,
    acceptedAt: Date.now(),
  })

  optimizedResume.value = { ...optimizedResume.value, [field]: after }
}

// ---------- 工作流状态持久化：刷新页面不丢失 ----------
const STORAGE_KEY = 'ai-job-workbench-state'

function persistState() {
  try {
    sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        resumeData: resumeData.value,
        jdText: jdText.value,
        jdAnalysis: jdAnalysis.value,
        matchResult: matchResult.value,
        originalResume: originalResume.value,
        optimizedResume: optimizedResume.value,
        appliedChanges: appliedChanges.value,
        originalMatchScore: originalMatchScore.value,
        optimizedMatchScore: optimizedMatchScore.value,
        optimizedMatchResult: optimizedMatchResult.value,
      })
    )
  } catch (e) {
    // 存储失败（如超出容量）不影响功能
  }
}

function restoreState() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const state = JSON.parse(raw)
    resumeData.value = state.resumeData || null
    jdText.value = state.jdText || ''
    jdAnalysis.value = state.jdAnalysis || null
    matchResult.value = state.matchResult || null
    originalResume.value = state.originalResume || null
    optimizedResume.value = state.optimizedResume || null
    appliedChanges.value = state.appliedChanges || []
    originalMatchScore.value = state.originalMatchScore ?? null
    optimizedMatchScore.value = state.optimizedMatchScore ?? null
    optimizedMatchResult.value = state.optimizedMatchResult || null
  } catch (e) {
    // 数据损坏时忽略，从空状态开始
  }
}

watch(
  [
    resumeData,
    jdText,
    jdAnalysis,
    matchResult,
    originalResume,
    optimizedResume,
    appliedChanges,
    originalMatchScore,
    optimizedMatchScore,
    optimizedMatchResult,
  ],
  persistState,
  { deep: true }
)

function resumeInfoToText(info) {
  if (!info) return ''
  const parts = []
  if (info.name) parts.push(`姓名：${info.name}`)
  if (info.contact) parts.push(`联系方式：${info.contact}`)
  if (info.objective) parts.push(`求职意向：${info.objective}`)

  const educationItems = info.education?.length
    ? info.education
    : [[info.school, info.major].filter(Boolean).join(' ')].filter(Boolean)
  if (educationItems.length) {
    parts.push('教育经历：')
    educationItems.forEach((e) => parts.push(`- ${e}`))
  }
  if (info.skills?.length) parts.push(`技能：${info.skills.join('、')}`)
  if (info.projects?.length) {
    parts.push('项目经历：')
    info.projects.forEach((p) => parts.push(`- ${p}`))
  }
  if (info.internships?.length) {
    parts.push('实习/实践经历：')
    info.internships.forEach((p) => parts.push(`- ${p}`))
  }
  if (info.campusExperience?.length) {
    parts.push('校园经历：')
    info.campusExperience.forEach((p) => parts.push(`- ${p}`))
  }
  if (info.certificates?.length) {
    parts.push(`证书与奖项：${info.certificates.join('、')}`)
  }
  if (info.selfEvaluation) parts.push(`自我评价：${info.selfEvaluation}`)
  if (info.other?.length) {
    parts.push('其他信息：')
    info.other.forEach((p) => parts.push(`- ${p}`))
  }
  return parts.join('\n')
}

async function handleRematch() {
  if (!jdText.value.trim()) {
    error.value = '请先粘贴招聘 JD'
    return
  }
  if (!optimizedResume.value) {
    error.value = '请先上传简历'
    return
  }

  isRematching.value = true
  error.value = ''

  try {
    const optimizedText = resumeInfoToText(optimizedResume.value)
    const result = await matchResumeJd(optimizedText, jdText.value.trim())
    optimizedMatchResult.value = result
    optimizedMatchScore.value = result?.matchScore ?? null
    scrollToSection('section-match')
  } catch (err) {
    error.value = err.message || '重新匹配失败，请稍后重试'
  } finally {
    isRematching.value = false
  }
}
</script>

<template>
  <div class="layout">
    <Sidebar
      :active-section="activeSection"
      @navigate="scrollToSection"
    />

    <main class="main-content">
      <header class="top-header">
        <h1>AI 求职工作台</h1>
        <div class="steps">
          <div :class="['step', resumeInfo ? 'completed' : 'active']">
            <span class="step-number">1</span>
            <span class="step-label">上传简历</span>
          </div>
          <div class="step-line"></div>
          <div :class="['step', jdText.trim() ? 'completed' : 'active']">
            <span class="step-number">2</span>
            <span class="step-label">输入岗位JD</span>
          </div>
          <div class="step-line"></div>
          <div :class="['step', matchResult ? 'completed' : 'active']">
            <span class="step-number">3</span>
            <span class="step-label">匹配分析</span>
          </div>
          <div class="step-line"></div>
          <div :class="['step', suggestionsAllConfirmed ? 'completed' : 'active']">
            <span class="step-number">4</span>
            <span class="step-label">优化建议</span>
          </div>
          <div class="step-line"></div>
          <div :class="['step', suggestionsAllConfirmed ? 'completed' : 'active']">
            <span class="step-number">5</span>
            <span class="step-label">优化后简历</span>
          </div>
        </div>
      </header>

      <div class="content-scroll">
        <section
          :ref="(el) => setSectionRef(el, 'section-resume')"
          id="section-resume"
          class="workflow-section"
        >
          <ResumeUpload @update:resume="handleResumeUpdate" />
          <ResumeInfo
            v-if="resumeInfo"
            :info="resumeInfo"
            @reset="handleResetResume"
          />
          <ResumeAnalysis
            v-if="resumeInfo"
            :info="resumeInfo"
            :problems="matchResult?.resumeProblems || []"
          />
        </section>

        <section
          :ref="(el) => setSectionRef(el, 'section-jd')"
          id="section-jd"
          class="workflow-section"
        >
          <JdInput
            v-model="jdText"
            :loading="jdLoading"
            @analyze="handleJdAnalyze"
          />
          <p v-if="jdError" class="error-message">{{ jdError }}</p>
          <AnalysisResult v-if="jdAnalysis" :data="jdAnalysis" />
        </section>

        <section
          :ref="(el) => setSectionRef(el, 'section-match')"
          id="section-match"
          class="workflow-section"
        >
          <div class="match-actions">
            <button
              class="match-btn"
              @click="handleMatchAnalyze"
              :disabled="matchLoading || !resumeText || !jdText.trim()"
            >
              {{ matchLoading ? '分析中...' : '开始岗位匹配分析' }}
            </button>
          </div>

          <p v-if="error" class="error-message">{{ error }}</p>

          <MatchResult
            v-if="matchResult"
            :data="matchResult"
            :optimized-data="optimizedMatchResult"
            :original-score="originalMatchScore"
            :optimized-score="optimizedMatchScore"
          />
        </section>

        <section
          :ref="(el) => setSectionRef(el, 'section-optimization')"
          id="section-optimization"
          class="workflow-section"
        >
          <OptimizationPanel
            v-if="matchResult?.optimizationSuggestions?.length"
            :suggestions="matchResult.optimizationSuggestions"
            @apply="handleApplyChange"
            @keep="handleKeepChange"
            @edit-confirm="handleEditConfirm"
            @batch-apply="handleBatchApply"
            @batch-keep="handleBatchKeep"
            @view-optimized="scrollToSection('section-optimized-resume')"
          />
        </section>

        <section
          :ref="(el) => setSectionRef(el, 'section-optimized-resume')"
          id="section-optimized-resume"
          class="workflow-section"
        >
          <OptimizedResume
            v-if="optimizedResume"
            :original-resume="originalResume"
            :optimized-resume="optimizedResume"
            :applied-changes="appliedChanges"
            :original-match-score="originalMatchScore"
            :optimized-match-score="optimizedMatchScore"
            :is-rematching="isRematching"
            @manual-edit="handleManualEdit"
            @rematch="handleRematch"
          />
        </section>
      </div>
    </main>

    <ChatAssistant :context="aiContext" />
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #f5f7fa;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.top-header {
  background: #fff;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.top-header h1 {
  margin: 0 0 16px;
  font-size: 20px;
  color: #1f2937;
}

.steps {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #6b7280;
}

.step.active {
  color: #2563eb;
  font-weight: 600;
}

.step.completed {
  color: #10b981;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e5e7eb;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.step.active .step-number {
  background: #2563eb;
  color: #fff;
}

.step.completed .step-number {
  background: #10b981;
  color: #fff;
}

.step-line {
  width: 32px;
  height: 1px;
  background: #e5e7eb;
}

.content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  scroll-behavior: smooth;
}

.workflow-section {
  scroll-margin-top: 24px;
}

.match-actions {
  display: flex;
  justify-content: center;
}

.match-btn {
  padding: 12px 32px;
  background: #10b981;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

.match-btn:disabled {
  background: #6ee7b7;
  cursor: not-allowed;
}

.error-message {
  color: #dc2626;
  background: #fef2f2;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
}

/* 移动端：整页随 body 自然纵向滚动，不使用固定高度/内层滚动容器 */
@media (max-width: 767px) {
  .layout {
    flex-direction: column;
    height: auto;
    min-height: 100vh;
    min-height: 100dvh;
    overflow: visible;
  }

  .main-content {
    flex: none;
    overflow: visible;
  }

  .top-header {
    padding: 10px 14px;
  }

  .top-header h1 {
    margin-bottom: 10px;
    font-size: 17px;
  }

  /* 步骤条在窄屏内横向滑动，避免换行撑破布局 */
  .steps {
    gap: 6px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .step {
    flex-shrink: 0;
    font-size: 12px;
  }

  .step-number {
    width: 20px;
    height: 20px;
    font-size: 11px;
  }

  .step-line {
    width: 14px;
    flex-shrink: 0;
  }

  /* 内容区回到普通文档流，由 body 统一滚动；底部留出 FAB 安全距离 */
  .content-scroll {
    flex: none;
    overflow: visible;
    padding: 14px 14px 110px;
    gap: 16px;
  }

  /* sticky 顶部导航高度约 52px，跳转锚点时预留空间 */
  .workflow-section {
    scroll-margin-top: 64px;
  }

  .match-actions {
    justify-content: stretch;
  }

  .match-btn {
    width: 100%;
    padding: 12px 16px;
  }
}
</style>
