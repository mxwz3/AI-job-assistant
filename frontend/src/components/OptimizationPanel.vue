<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  suggestions: { type: Array, required: true },
})

const emit = defineEmits([
  'apply',
  'keep',
  'edit-confirm',
  'batch-apply',
  'batch-keep',
  'view-optimized',
])

const editingIndex = ref(-1)
const editText = ref('')

const TYPE_LABELS = {
  modify: '修改',
  enhance: '强化',
  add: '新增',
  delete: '删除',
  keep: '保留',
}

const FIELD_LABELS = {
  projects: '项目经历',
  skills: '技能',
  education: '教育经历',
  internships: '实习/实践经历',
  campusExperience: '校园经历',
  certificates: '证书与奖项',
  selfEvaluation: '自我评价',
  basicInfo: '基本信息',
}

const STATUS_META = {
  pending: { label: '待确认', class: 'pending-badge' },
  accepted: { label: '✓ 已接受', class: 'accepted-badge' },
  kept: { label: '已保留原文', class: 'kept-badge' },
  edited: { label: '✓ 已编辑并采用', class: 'edited-badge' },
}

const stats = computed(() => {
  const total = props.suggestions.length
  const accepted = props.suggestions.filter((s) => s.status === 'accepted' || s.status === 'edited').length
  const kept = props.suggestions.filter((s) => s.status === 'kept').length
  const pending = props.suggestions.filter((s) => s.status === 'pending' || !s.status).length
  return { total, accepted, kept, pending }
})

function statusOf(item) {
  return STATUS_META[item.status] || STATUS_META.pending
}

function isPending(item) {
  return !item.status || item.status === 'pending'
}

function typeLabel(item) {
  return TYPE_LABELS[item.type] || '修改'
}

function fieldLabel(item) {
  return FIELD_LABELS[item.field] || item.field || '简历'
}

function startEdit(index, currentAfter) {
  editingIndex.value = index
  editText.value = currentAfter
}

function cancelEdit() {
  editingIndex.value = -1
  editText.value = ''
}

function confirmEdit(index) {
  const after = editText.value.trim()
  if (!after) return
  emit('edit-confirm', { index, after })
  editingIndex.value = -1
  editText.value = ''
}

function apply(index) {
  emit('apply', { index })
}

function keep(index) {
  emit('keep', index)
}

// 句子级 Diff：对比修改前/后，标记被删除与新增的句子（模板渲染依赖此函数）
function splitSentences(text) {
  if (!text) return []
  return text
    .split(/(?<=[。；;！？!?])\s*|\n+/)
    .map((s) => s.trim())
    .filter(Boolean)
}

function normalizeSentence(s) {
  return s.replace(/[\s，,。.；;：:！？!?、]/g, '')
}

function diffParts(item) {
  const beforeList = splitSentences(item.before)
  const afterList = splitSentences(item.after)
  const beforeSet = new Set(beforeList.map(normalizeSentence))
  const afterSet = new Set(afterList.map(normalizeSentence))
  return {
    before: beforeList.map((text) => ({ text, removed: !afterSet.has(normalizeSentence(text)) })),
    after: afterList.map((text) => ({ text, added: !beforeSet.has(normalizeSentence(text)) })),
  }
}

// 批量操作二次确认（确认后才走原有逻辑，不改变接受/保留行为）
function confirmBatchApply() {
  const n = stats.value.pending
  if (n === 0) return
  if (window.confirm(`确定接受全部 ${n} 项待确认建议吗？\n接受后建议内容将写入「优化后简历」。`)) {
    emit('batch-apply')
  }
}

function confirmBatchKeep() {
  const n = stats.value.pending
  if (n === 0) return
  if (window.confirm(`确定保留全部 ${n} 项待确认建议的原文吗？\n「优化后简历」将保持原始内容不变。`)) {
    emit('batch-keep')
  }
}
</script>

<template>
  <section class="optimization-panel">
    <h2>AI 优化建议</h2>
    <p class="subtitle">
      AI 只提出建议，不会直接修改简历。逐条确认后才会写入「优化后简历」。
    </p>

    <div class="stats-bar">
      <span class="stat">AI 发现 <b>{{ stats.total }}</b> 项可优化内容</span>
      <span class="stat accepted">已接受 <b>{{ stats.accepted }}</b> 项</span>
      <span class="stat kept">已保留 <b>{{ stats.kept }}</b> 项</span>
      <span class="stat pending">待确认 <b>{{ stats.pending }}</b> 项</span>
      <div class="batch-actions">
        <button
          class="btn-batch-apply"
          :disabled="stats.pending === 0"
          @click="emit('batch-apply')"
        >
          全部接受
        </button>
        <button
          class="btn-batch-keep"
          :disabled="stats.pending === 0"
          @click="emit('batch-keep')"
        >
          全部保留
        </button>
      </div>
    </div>

    <div class="suggestion-list">
      <div
        v-for="(item, index) in suggestions"
        :key="item.id || index"
        :class="['suggestion-card', item.status || 'pending']"
      >
        <div class="card-header">
          <div class="header-left">
            <span class="number">#{{ index + 1 }}</span>
            <span class="field-chip">{{ fieldLabel(item) }}</span>
            <span class="type-chip">{{ typeLabel(item) }}</span>
          </div>
          <span :class="['status-badge', statusOf(item).class]">
            {{ statusOf(item).label }}
          </span>
        </div>

        <div class="field problem-field">
          <span class="field-label">问题</span>
          <p class="field-text">{{ item.problem || '表述不够具体或未能突出岗位匹配点' }}</p>
        </div>

        <div v-if="item.before" class="field original-field">
          <span class="field-label">修改前</span>
          <p class="field-text">{{ item.before }}</p>
        </div>

        <div class="field reason-field">
          <span class="field-label">修改原因</span>
          <p class="field-text">{{ item.reason || '该表述未能充分体现岗位要求的技能或经验' }}</p>
        </div>

        <div class="field suggested-field">
          <span class="field-label">修改后（AI 建议）</span>
          <div v-if="editingIndex === index" class="edit-area">
            <textarea v-model="editText" rows="4" class="edit-textarea"></textarea>
            <div class="edit-actions">
              <button class="btn-save" @click="confirmEdit(index)">确认并写入简历</button>
              <button class="btn-cancel" @click="cancelEdit">取消</button>
            </div>
          </div>
          <p v-else class="field-text suggested-text">
            <span
              v-for="(part, i) in diffParts(item).after"
              :key="i"
              :class="{ 'diff-added': part.added }"
            >{{ part.text }}</span>
          </p>
        </div>

        <div v-if="isPending(item) && editingIndex !== index" class="actions">
          <button class="btn-apply" @click="apply(index)">接受修改</button>
          <button class="btn-edit" @click="startEdit(index, item.after)">编辑</button>
          <button class="btn-keep" @click="keep(index)">保留原文</button>
        </div>
      </div>
    </div>

    <div class="panel-footer">
      <button class="btn-view-optimized" @click="emit('view-optimized')">
        查看优化后简历 →
      </button>
    </div>
  </section>
</template>

<style scoped>
.optimization-panel {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

h2 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #1f2937;
}

.subtitle {
  margin: 0 0 16px;
  color: #6b7280;
  font-size: 14px;
}

.stats-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  padding: 12px 16px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  margin-bottom: 20px;
}

.stat {
  font-size: 13px;
  color: #4b5563;
}

.stat b {
  font-size: 15px;
}

.stat.accepted b { color: #047857; }
.stat.kept b { color: #6b7280; }
.stat.pending b { color: #b45309; }

.batch-actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.batch-actions button {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
}

.btn-batch-apply {
  background: #10b981;
  color: #fff;
  border-color: #10b981;
}

.btn-batch-keep {
  background: #fff;
  color: #4b5563;
  border-color: #d1d5db;
}

.batch-actions button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.suggestion-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 18px;
  background: #fff;
  transition: border-color 0.2s;
}

.suggestion-card.accepted,
.suggestion-card.edited {
  border-color: #10b981;
  background: #f0fdf4;
}

.suggestion-card.kept {
  border-color: #e5e7eb;
  background: #f9fafb;
  opacity: 0.75;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.number {
  font-size: 13px;
  color: #9ca3af;
  font-weight: 600;
}

.field-chip {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 999px;
  background: #eff6ff;
  color: #1e40af;
  font-weight: 600;
}

.type-chip {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 999px;
  background: #f3f4f6;
  color: #4b5563;
}

.status-badge {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  font-weight: 600;
}

.pending-badge { color: #b45309; background: #fef3c7; }
.accepted-badge { color: #047857; background: #d1fae5; }
.edited-badge { color: #1e40af; background: #dbeafe; }
.kept-badge { color: #6b7280; background: #e5e7eb; }

.field {
  margin-bottom: 14px;
}

.field-label {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  color: #4b5563;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
  margin-bottom: 6px;
}

.stat-main {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.stat-main b {
  font-size: 14px;
  color: #047857;
}

/* 修改前/修改后区块对比：修改前弱化，修改后强化 */
.original-field {
  background: #f9fafb;
  border-radius: 8px;
  padding: 10px 12px;
}

.suggested-field {
  background: #f0fdf4;
  border-radius: 8px;
  padding: 10px 12px;
}

.original-text {
  color: #6b7280;
}

.suggested-text {
  color: #1f2937;
  font-weight: 500;
}

/* 句子级 Diff：删除内容删除线弱化，新增内容绿色高亮 */
.diff-removed {
  text-decoration: line-through;
  color: #b3b9c2;
}

.diff-added {
  background: #bbf7d0;
  color: #065f46;
  padding: 0 2px;
  border-radius: 3px;
  font-weight: 600;
}

.field-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: #374151;
}

.problem-field .field-text { color: #991b1b; }

.original-field .field-text {
  color: #6b7280;
  text-decoration: line-through;
  text-decoration-color: #d1d5db;
}

.reason-field .field-text { color: #92400e; }

.suggested-text {
  color: #065f46;
  font-weight: 500;
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

.actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.actions button,
.edit-actions button {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
}

.btn-apply {
  background: #10b981;
  color: #fff;
  border-color: #10b981;
}

.btn-edit {
  background: #fff;
  color: #2563eb;
  border-color: #bfdbfe;
}

.btn-keep {
  background: #fff;
  color: #6b7280;
  border-color: #e5e7eb;
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

.panel-footer {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: center;
}

.btn-view-optimized {
  padding: 10px 24px;
  border-radius: 8px;
  border: none;
  background: #10b981;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-view-optimized:hover:not(:disabled) {
  background: #059669;
}

.btn-view-optimized:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}
</style>
