<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { downloadResumePdf, fetchResumePdfBlob } from '../api/resume.js'

const props = defineProps({
  originalResume: { type: Object, default: null },
  optimizedResume: { type: Object, required: true },
  originalMatchScore: { type: Number, default: null },
  optimizedMatchScore: { type: Number, default: null },
  isRematching: { type: Boolean, default: false },
})

const emit = defineEmits(['manual-edit', 'rematch'])

const activeTab = ref('optimized')
const editingField = ref(null)
const editValue = ref('')
const isDownloading = ref(false)
const saveMessage = ref('')
const pdfMessage = ref('')
const pdfError = ref('')
const previewUrl = ref('')
const isPreviewLoading = ref(false)
const previewError = ref('')

const scoreDiff = computed(() => {
  if (props.originalMatchScore == null || props.optimizedMatchScore == null) return null
  return props.optimizedMatchScore - props.originalMatchScore
})

function educationList(info) {
  if (info?.education?.length) return info.education
  const fallback = [info?.school, info?.major].filter(Boolean).join(' ')
  return fallback ? [fallback] : []
}

const modules = computed(() => {
  const r = props.optimizedResume
  return [
    { key: 'name', title: '姓名', type: 'text', value: r.name || '', display: r.name || '未填写' },
    { key: 'contact', title: '联系方式', type: 'text', value: r.contact || '', display: r.contact || '未填写' },
    { key: 'objective', title: '求职意向', type: 'text', value: r.objective || '', display: r.objective || '未填写' },
    { key: 'education', title: '教育经历', type: 'list', value: educationList(r).join('\n'), display: toDisplay(educationList(r)) },
    { key: 'skills', title: '技能', type: 'list', value: (r.skills || []).join('、'), display: toDisplay(r.skills, true) },
    { key: 'projects', title: '项目经历', type: 'list', value: (r.projects || []).join('\n'), display: toDisplay(r.projects) },
    { key: 'internships', title: '实习/实践经历', type: 'list', value: (r.internships || []).join('\n'), display: toDisplay(r.internships) },
    { key: 'campusExperience', title: '校园经历', type: 'list', value: (r.campusExperience || []).join('\n'), display: toDisplay(r.campusExperience) },
    { key: 'certificates', title: '证书与奖项', type: 'list', value: (r.certificates || []).join('、'), display: toDisplay(r.certificates) },
    { key: 'selfEvaluation', title: '自我评价', type: 'text', value: r.selfEvaluation || '', display: r.selfEvaluation || '未填写' },
    { key: 'other', title: '其他信息', type: 'list', value: (r.other || []).join('\n'), display: toDisplay(r.other) },
  ]
})

function toDisplay(list, tag = false) {
  return list?.length ? list.map((s) => ({ text: s, tag })) : [{ text: '未填写', tag: false }]
}

const originalModules = computed(() => {
  const r = props.originalResume
  const join = (list) => (list?.length ? list.join('\n') : '未填写')
  return [
    { title: '姓名', value: r?.name || '未填写' },
    { title: '联系方式', value: r?.contact || '未填写' },
    { title: '求职意向', value: r?.objective || '未填写' },
    { title: '教育经历', value: join(educationList(r)) },
    { title: '技能', value: r?.skills?.length ? r.skills.join('、') : '未填写' },
    { title: '项目经历', value: join(r?.projects) },
    { title: '实习/实践经历', value: join(r?.internships) },
    { title: '校园经历', value: join(r?.campusExperience) },
    { title: '证书与奖项', value: r?.certificates?.length ? r.certificates.join('、') : '未填写' },
    { title: '自我评价', value: r?.selfEvaluation || '未填写' },
    { title: '其他信息', value: join(r?.other) },
  ]
})

function startEdit(module) {
  editingField.value = module.key
  editValue.value = module.value
}

function cancelEdit() {
  editingField.value = null
  editValue.value = ''
}

function saveEdit(module) {
  const after = editValue.value.trim()
  const before = module.value

  let updatedValue
  if (module.type === 'list') {
    updatedValue = after
      .split(/[、,，\n]/)
      .map((s) => s.trim())
      .filter(Boolean)
  } else {
    updatedValue = after
  }

  emit('manual-edit', {
    field: module.key,
    before,
    after: updatedValue,
  })

  editingField.value = null
  editValue.value = ''
}

function handleRematch() {
  emit('rematch')
}

function handleSaveAll() {
  saveMessage.value = '所有修改已保存'
  setTimeout(() => {
    saveMessage.value = ''
  }, 2000)
}

async function handleDownloadPdf() {
  isDownloading.value = true
  pdfError.value = ''
  pdfMessage.value = ''
  try {
    await downloadResumePdf(props.optimizedResume)
    pdfMessage.value = 'PDF 已生成，正在下载'
    setTimeout(() => {
      pdfMessage.value = ''
    }, 3000)
  } catch (err) {
    pdfError.value = 'PDF 生成失败，请稍后重试'
  } finally {
    isDownloading.value = false
  }
}

async function loadPreview() {
  isPreviewLoading.value = true
  previewError.value = ''
  try {
    const blob = await fetchResumePdfBlob(props.optimizedResume)
    if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value)
    }
    previewUrl.value = URL.createObjectURL(blob)
  } catch (err) {
    previewError.value = 'PDF 预览生成失败，请稍后重试'
  } finally {
    isPreviewLoading.value = false
  }
}

watch(activeTab, (tab) => {
  if (tab === 'preview' && !isPreviewLoading.value) {
    loadPreview()
  }
})

onUnmounted(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
})
</script>

<template>
  <section class="optimized-resume">
    <header class="panel-header">
      <div>
        <h2>我的优化后简历</h2>
        <p class="subtitle">基于 AI 建议或手动编辑形成的真实可编辑简历</p>
      </div>
    </header>

    <div class="tabs">
      <button
        :class="['tab', { active: activeTab === 'original' }]"
        @click="activeTab = 'original'"
      >
        原始简历
      </button>
      <button
        :class="['tab', { active: activeTab === 'optimized' }]"
        @click="activeTab = 'optimized'"
      >
        优化后简历
      </button>
      <button
        :class="['tab', { active: activeTab === 'preview' }]"
        @click="activeTab = 'preview'"
      >
        PDF 预览
      </button>
    </div>

    <div v-if="activeTab === 'preview'" class="pdf-preview">
      <div class="preview-toolbar">
        <button
          class="btn-refresh"
          :disabled="isPreviewLoading"
          @click="loadPreview"
        >
          {{ isPreviewLoading ? '正在生成 PDF...' : '刷新预览' }}
        </button>
        <button
          class="btn-download"
          :disabled="isDownloading"
          @click="handleDownloadPdf"
        >
          {{ isDownloading ? '生成中...' : '下载 PDF' }}
        </button>
      </div>
      <p v-if="previewError" class="pdf-error">{{ previewError }}</p>
      <p v-if="pdfMessage" class="pdf-message">{{ pdfMessage }}</p>
      <p v-if="pdfError" class="pdf-error">{{ pdfError }}</p>
      <div v-if="isPreviewLoading" class="preview-loading">正在生成预览...</div>
      <iframe
        v-else-if="previewUrl"
        :src="previewUrl"
        class="pdf-frame"
        title="优化后简历 PDF 预览"
      ></iframe>
      <p class="pdf-disclaimer">
        预览与下载内容一致，均根据当前优化后简历实时生成，不会修改原始 PDF。
      </p>
    </div>

    <div v-else-if="activeTab === 'original'" class="resume-content readonly">
      <div
        v-for="module in originalModules"
        :key="module.title"
        class="module-card"
      >
        <h3 class="module-title">{{ module.title }}</h3>
        <p class="module-text">{{ module.value }}</p>
      </div>
    </div>

    <div v-else class="resume-content">
      <div
        v-for="module in modules"
        :key="module.key"
        class="module-card"
      >
        <div class="module-header">
          <h3 class="module-title">{{ module.title }}</h3>
          <button
            v-if="editingField !== module.key"
            class="btn-edit"
            @click="startEdit(module)"
          >
            编辑
          </button>
        </div>

        <div v-if="editingField === module.key" class="edit-area">
          <textarea
            v-model="editValue"
            rows="4"
            class="edit-textarea"
            :placeholder="module.type === 'list' ? '多个项目用换行或顿号分隔' : '请输入内容'"
          ></textarea>
          <div class="edit-actions">
            <button class="btn-save" @click="saveEdit(module)">保存</button>
            <button class="btn-cancel" @click="cancelEdit">取消</button>
          </div>
        </div>

        <div v-else class="module-display">
          <div v-if="module.type === 'list' && Array.isArray(module.display)" class="list-items">
            <span
              v-for="(item, idx) in module.display"
              :key="idx"
              :class="['list-item', { tag: item.tag }]"
            >
              {{ item.text }}
            </span>
          </div>
          <p v-else class="module-text">{{ module.display }}</p>
        </div>
      </div>

      <div class="match-compare">
        <h3 class="compare-title">匹配度对比</h3>
        <div class="score-row">
          <div class="score-box">
            <span class="score-label">原始匹配度</span>
            <span class="score-value">{{ originalMatchScore != null ? originalMatchScore + '%' : '-' }}</span>
          </div>
          <div class="score-arrow">→</div>
          <div class="score-box highlight">
            <span class="score-label">优化后匹配度</span>
            <span class="score-value">{{ optimizedMatchScore != null ? optimizedMatchScore + '%' : '-' }}</span>
          </div>
          <div v-if="scoreDiff != null" class="score-diff" :class="scoreDiff >= 0 ? 'positive' : 'negative'">
            {{ scoreDiff >= 0 ? '+' : '' }}{{ scoreDiff }}%
          </div>
        </div>
      </div>

      <div class="action-bar">
        <button class="btn-save-all" @click="handleSaveAll">
          保存修改
        </button>
        <button
          class="btn-rematch"
          :disabled="isRematching"
          @click="handleRematch"
        >
          {{ isRematching ? '重新匹配中...' : '使用此简历重新匹配' }}
        </button>
        <button
          class="btn-download"
          :disabled="isDownloading"
          @click="handleDownloadPdf"
        >
          {{ isDownloading ? '生成中...' : '下载 PDF' }}
        </button>
      </div>

      <p v-if="saveMessage" class="save-message">{{ saveMessage }}</p>
      <p v-if="pdfMessage" class="pdf-message">{{ pdfMessage }}</p>
      <p v-if="pdfError" class="pdf-error">{{ pdfError }}</p>

      <p class="pdf-disclaimer">
        说明：下载的 PDF 是根据优化后的简历内容生成的新版本，不会修改您上传的原始 PDF。
      </p>
    </div>
  </section>
</template>

<style scoped>
.optimized-resume {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.panel-header {
  margin-bottom: 16px;
}

h2 {
  margin: 0 0 6px;
  font-size: 18px;
  color: #1f2937;
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 12px;
}

.tab {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #6b7280;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.tab:hover {
  background: #f3f4f6;
}

.tab.active {
  background: #eff6ff;
  color: #2563eb;
}

.resume-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.module-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 16px;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.module-title {
  margin: 0;
  font-size: 15px;
  color: #374151;
}

.btn-edit {
  padding: 4px 12px;
  border-radius: 6px;
  border: 1px solid #bfdbfe;
  background: #fff;
  color: #2563eb;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.module-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: #374151;
  white-space: pre-line;
}

.list-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.list-item {
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
}

.list-item.tag {
  padding: 4px 10px;
  border-radius: 999px;
  background: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.edit-area {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.edit-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
}

.edit-textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

.edit-actions {
  display: flex;
  gap: 10px;
}

.edit-actions button {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
}

.btn-save {
  background: #3b82f6;
  color: #fff;
  border-color: #3b82f6;
}

.btn-cancel {
  background: #fff;
  color: #6b7280;
  border-color: #e5e7eb;
}

.readonly .module-card {
  background: #f9fafb;
}

.match-compare {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 18px;
  background: #f8fafc;
}

.compare-title {
  margin: 0 0 14px;
  font-size: 15px;
  color: #374151;
}

.score-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.score-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 20px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #e5e7eb;
  min-width: 100px;
}

.score-box.highlight {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.score-label {
  font-size: 12px;
  color: #6b7280;
}

.score-value {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
}

.score-arrow {
  font-size: 20px;
  color: #9ca3af;
}

.score-diff {
  font-size: 18px;
  font-weight: 700;
  padding: 6px 12px;
  border-radius: 6px;
}

.score-diff.positive {
  color: #047857;
  background: #d1fae5;
}

.score-diff.negative {
  color: #991b1b;
  background: #fee2e2;
}

.action-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-bar button {
  flex: 1;
  min-width: 140px;
  padding: 12px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-save-all {
  background: #10b981;
  color: #fff;
}

.btn-save-all:hover {
  background: #059669;
}

.btn-rematch {
  background: #4f46e5;
  color: #fff;
}

.btn-rematch:hover {
  background: #4338ca;
}

.btn-rematch:disabled {
  background: #a5b4fc;
  cursor: not-allowed;
}

.btn-download {
  background: #fff;
  color: #4f46e5;
  border: 1px solid #4f46e5;
}

.btn-download:hover {
  background: #eef2ff;
}

.btn-download:disabled {
  color: #a5b4fc;
  border-color: #a5b4fc;
  cursor: not-allowed;
}

.save-message {
  text-align: center;
  color: #047857;
  font-size: 14px;
  margin: 0;
  font-weight: 600;
}

.pdf-message {
  text-align: center;
  color: #1e40af;
  font-size: 14px;
  margin: 0;
  font-weight: 600;
}

.pdf-error {
  text-align: center;
  color: #b91c1c;
  font-size: 14px;
  margin: 0;
  font-weight: 600;
}

.pdf-disclaimer {
  text-align: center;
  color: #6b7280;
  font-size: 12px;
  margin: 0;
}

.pdf-preview {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-toolbar {
  display: flex;
  gap: 12px;
}

.preview-toolbar button {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-refresh {
  background: #4f46e5;
  color: #fff;
  border: none;
}

.btn-refresh:hover {
  background: #4338ca;
}

.btn-refresh:disabled {
  background: #a5b4fc;
  cursor: not-allowed;
}

.preview-loading {
  padding: 60px 0;
  text-align: center;
  color: #6b7280;
  font-size: 14px;
  background: #f9fafb;
  border: 1px dashed #e5e7eb;
  border-radius: 10px;
}

.pdf-frame {
  width: 100%;
  height: 720px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #f9fafb;
}
</style>
