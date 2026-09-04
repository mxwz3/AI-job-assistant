<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Object, required: true },
  optimizedData: { type: Object, default: null },
  originalScore: { type: Number, default: null },
  optimizedScore: { type: Number, default: null },
})

const emit = defineEmits(['send-to-assistant'])

const scoreClass = computed(() => {
  const score = props.data.matchScore
  if (score >= 90) return 'high'
  if (score >= 70) return 'medium'
  return 'low'
})

const scoreLabel = computed(() => {
  const score = props.data.matchScore
  if (score >= 90) return '高度匹配'
  if (score >= 70) return '基本匹配'
  return '匹配度较低'
})

// 基于已有匹配数据生成简短总结，不涉及任何算法改动
const scoreSummary = computed(() => {
  const score = props.data.matchScore || 0
  const missing = props.data.missingSkills || []
  const partial = (props.data.partialSkills || []).map((p) => p.skill)
  const gaps = [...missing.slice(0, 2), ...partial.slice(0, 2)].filter(Boolean)
  const gapText = gaps.length ? `，主要差距集中在${gaps.join('、')}等方面` : ''
  if (score >= 90) {
    return '简历与岗位高度匹配，核心要求均已覆盖，保持当前表达即可。'
  }
  if (score >= 70) {
    return `整体匹配较好${gapText}，针对这些内容优化简历后可以进一步提高岗位匹配度。`
  }
  return `当前匹配度较低${gapText}，建议参考下方优化建议逐条改进后重新匹配。`
})

const breakdown = computed(() => [
  { label: '技能匹配', value: props.data.skillMatch || 0 },
  { label: '项目匹配', value: props.data.projectMatch || 0 },
  { label: '经历匹配', value: props.data.experienceMatch || 0 },
  { label: '岗位要求覆盖', value: props.data.requirementCoverage || 0 },
])

function scoreBarClass(value) {
  if (value >= 90) return 'high'
  if (value >= 70) return 'medium'
  return 'low'
}

function escapeHtml(text) {
  return (text || '').replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])
  )
}

// 高亮原因文本中的技能关键词（先转义再加粗，避免注入）
function highlightReason(item) {
  const reason = escapeHtml(item.reason || '')
  const skill = escapeHtml(item.skill || '')
  if (!skill) return reason
  return reason.split(skill).join(`<strong>${skill}</strong>`)
}

function sendToAssistant(item) {
  emit(
    'send-to-assistant',
    `请针对目标岗位优化我简历中关于「${item.skill}」的描述。当前情况：${item.reason}`
  )
}

const hasOptimizedResult = computed(() => !!props.optimizedData)

const scoreDiff = computed(() => {
  if (props.originalScore == null || props.optimizedScore == null) return null
  return props.optimizedScore - props.originalScore
})

const newAdvantages = computed(() => {
  if (!props.optimizedData?.advantages || !props.data?.advantages) return []
  return props.optimizedData.advantages.filter(
    (item) => !props.data.advantages.includes(item)
  )
})

const remainingMissingSkills = computed(() => {
  if (!props.optimizedData?.missingSkills) return []
  return props.optimizedData.missingSkills
})

const resolvedMissingSkills = computed(() => {
  if (!props.data?.missingSkills || !props.optimizedData?.missingSkills) return []
  return props.data.missingSkills.filter(
    (skill) => !props.optimizedData.missingSkills.includes(skill)
  )
})
</script>

<template>
  <section class="match-result">
    <header class="match-header">
      <div>
        <h2>岗位匹配分析</h2>
        <p class="position">目标岗位：{{ data.position }}</p>
      </div>
      <div class="score-card" :class="scoreClass">
        <div class="score-value">{{ data.matchScore }}%</div>
        <div class="score-label">{{ scoreLabel }}</div>
      </div>
    </header>

    <div v-if="hasOptimizedResult" class="compare-banner">
      <h3>优化前后对比</h3>
      <div class="compare-row">
        <div class="compare-box">
          <span class="compare-label">原始简历</span>
          <span class="compare-score">{{ originalScore != null ? originalScore + '%' : data.matchScore + '%' }}</span>
        </div>
        <div class="compare-arrow">→</div>
        <div class="compare-box highlight">
          <span class="compare-label">优化后简历</span>
          <span class="compare-score">{{ optimizedScore != null ? optimizedScore + '%' : '-' }}</span>
        </div>
        <div v-if="scoreDiff != null" class="compare-diff" :class="scoreDiff >= 0 ? 'positive' : 'negative'">
          {{ scoreDiff >= 0 ? '+' : '' }}{{ scoreDiff }}%
        </div>
      </div>

      <div class="compare-details">
        <div v-if="newAdvantages.length" class="compare-section gained">
          <div class="compare-section-title">✅ 新增优势</div>
          <ul>
            <li v-for="(item, index) in newAdvantages" :key="index">{{ item }}</li>
          </ul>
        </div>

        <div v-if="resolvedMissingSkills.length" class="compare-section resolved">
          <div class="compare-section-title">🎯 已补齐技能</div>
          <div class="skill-tags">
            <span v-for="skill in resolvedMissingSkills" :key="skill" class="skill-tag">{{ skill }}</span>
          </div>
        </div>

        <div v-if="remainingMissingSkills.length" class="compare-section still-missing">
          <div class="compare-section-title">❌ 仍然缺失</div>
          <div class="skill-tags">
            <span v-for="skill in remainingMissingSkills" :key="skill" class="skill-tag">{{ skill }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="breakdown">
      <h3>匹配度拆解</h3>
      <div class="breakdown-list">
        <div v-for="item in breakdown" :key="item.label" class="breakdown-item">
          <div class="breakdown-info">
            <span class="breakdown-label">{{ item.label }}</span>
            <span class="breakdown-value">{{ item.value }}%</span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :class="scoreBarClass(item.value)"
              :style="{ width: `${item.value}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <div class="skills-match">
      <h3>技能匹配情况</h3>

      <div v-if="data.matchedSkills?.length" class="match-group matched">
        <div class="group-title">
          <span class="group-badge green">已匹配 {{ data.matchedSkills.length }}</span>
        </div>
        <div class="skill-tags">
          <span v-for="skill in data.matchedSkills" :key="skill" class="skill-tag">
            {{ skill }}
          </span>
        </div>
      </div>

      <div v-if="data.partialSkills?.length" class="match-group partial">
        <div class="group-title">
          <span class="group-badge yellow">部分匹配 {{ data.partialSkills.length }}</span>
        </div>
        <div class="skill-details">
          <div
            v-for="(item, index) in data.partialSkills"
            :key="index"
            class="skill-detail"
          >
            <div class="skill-detail-head">
              <span class="skill-name">{{ item.skill }}</span>
              <button
                type="button"
                class="btn-send-ai"
                @click="sendToAssistant(item)"
              >
                发给 AI 助手优化
              </button>
            </div>
            <span class="skill-reason" v-html="highlightReason(item)"></span>
          </div>
        </div>
      </div>

      <div v-if="data.missingSkills?.length" class="match-group missing">
        <div class="group-title">
          <span class="group-badge red">不匹配 {{ data.missingSkills.length }}</span>
        </div>
        <div class="skill-tags">
          <span v-for="skill in data.missingSkills" :key="skill" class="skill-tag">
            {{ skill }}
          </span>
        </div>
      </div>

      <p v-if="!data.matchedSkills?.length && !data.partialSkills?.length && !data.missingSkills?.length" class="empty">
        暂无技能匹配分析
      </p>
    </div>

    <div class="cards">
      <div class="card advantage">
        <h3>我的优势</h3>
        <ul v-if="data.advantages?.length">
          <li v-for="(item, index) in data.advantages" :key="index">{{ item }}</li>
        </ul>
        <p v-else class="empty">暂无明确优势</p>
      </div>

      <div class="card problems">
        <h3>简历问题与建议</h3>
        <div v-if="data.resumeProblems?.length" class="problem-list">
          <div
            v-for="(item, index) in data.resumeProblems"
            :key="index"
            class="problem-item"
          >
            <div class="problem-title">{{ item.problem }}</div>
            <div class="problem-suggestion">建议：{{ item.suggestion }}</div>
          </div>
        </div>
        <p v-else class="empty">暂无简历问题</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.match-result {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.compare-banner {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.compare-banner h3 {
  margin: 0 0 16px;
  font-size: 15px;
  color: #1f2937;
}

.compare-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.compare-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 14px 24px;
  border-radius: 10px;
  background: #fff;
  border: 1px solid #e5e7eb;
  min-width: 120px;
}

.compare-box.highlight {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.compare-label {
  font-size: 12px;
  color: #6b7280;
}

.compare-score {
  font-size: 26px;
  font-weight: 700;
  color: #1f2937;
}

.compare-arrow {
  font-size: 20px;
  color: #9ca3af;
}

.compare-diff {
  font-size: 18px;
  font-weight: 700;
  padding: 8px 14px;
  border-radius: 8px;
}

.compare-diff.positive {
  color: #047857;
  background: #d1fae5;
}

.compare-diff.negative {
  color: #991b1b;
  background: #fee2e2;
}

.compare-details {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.compare-section {
  border-radius: 8px;
  padding: 14px;
}

.compare-section-title {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 10px;
}

.compare-section.gained {
  background: #f0fdf4;
  color: #166534;
}

.compare-section.resolved {
  background: #eff6ff;
  color: #1e40af;
}

.compare-section.still-missing {
  background: #fef2f2;
  color: #991b1b;
}

.compare-section ul {
  margin: 0;
  padding-left: 16px;
  font-size: 13px;
  line-height: 1.7;
}

.match-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

h2 {
  margin: 0 0 6px;
  font-size: 18px;
  color: #1f2937;
}

h3 {
  margin: 0 0 14px;
  font-size: 15px;
  color: #374151;
}

.position {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.score-card {
  text-align: center;
  padding: 20px 24px;
  border-radius: 12px;
  min-width: 240px;
  border: 2px solid transparent;
}

.score-card.high {
  background: #ecfdf5;
  border-color: #a7f3d0;
  color: #065f46;
}

.score-card.medium {
  background: #fffbeb;
  border-color: #fde68a;
  color: #92400e;
}

.score-card.low {
  background: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}

.score-value {
  font-size: 44px;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 13px;
  margin-top: 6px;
  font-weight: 600;
}

.score-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.75);
  border-radius: 4px;
  overflow: hidden;
  margin-top: 12px;
}

.score-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.score-bar-fill.high {
  background: #10b981;
}

.score-bar-fill.medium {
  background: #f59e0b;
}

.score-bar-fill.low {
  background: #ef4444;
}

.score-summary {
  margin: 12px 0 0;
  font-size: 12.5px;
  line-height: 1.6;
  color: #4b5563;
  text-align: left;
}

.breakdown {
  margin-bottom: 24px;
}

.breakdown-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.breakdown-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.breakdown-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #4b5563;
}

.breakdown-value {
  font-weight: 600;
  color: #1f2937;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-fill.high {
  background: #10b981;
}

.progress-fill.medium {
  background: #f59e0b;
}

.progress-fill.low {
  background: #ef4444;
}

.skills-match {
  margin-bottom: 24px;
}

.match-group {
  margin-bottom: 16px;
  padding: 14px;
  border-radius: 8px;
}

.match-group.matched {
  background: #f0fdf4;
}

.match-group.partial {
  background: #fffbeb;
}

.match-group.missing {
  background: #fef2f2;
}

.group-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 10px;
}

.match-group.matched .group-title {
  color: #166534;
}

.match-group.partial .group-title {
  color: #92400e;
}

.match-group.missing .group-title {
  color: #991b1b;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 13px;
  background: #fff;
  border: 1px solid currentColor;
}

.match-group.matched .skill-tag {
  color: #166534;
  border-color: #bbf7d0;
}

.match-group.missing .skill-tag {
  color: #991b1b;
  border-color: #fecaca;
}

.skill-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skill-detail {
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: #fff;
  padding: 12px;
  border-radius: 6px;
}

.skill-detail-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.skill-name {
  font-weight: 700;
  color: #92400e;
  font-size: 14px;
}

.skill-reason {
  font-size: 13px;
  color: #78350f;
  line-height: 1.6;
}

.skill-reason :deep(strong) {
  color: #92400e;
  font-weight: 700;
}

.btn-send-ai {
  flex-shrink: 0;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid #fcd34d;
  background: #fff;
  color: #b45309;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-send-ai:hover {
  background: #fef3c7;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.card {
  border-radius: 10px;
  padding: 18px;
}

.card h3 {
  margin: 0 0 12px;
  font-size: 15px;
}

.advantage {
  background: #f0fdf4;
  color: #14532d;
}

.advantage h3 {
  color: #166534;
}

.problems {
  background: #eff6ff;
  color: #1e3a8a;
}

.problems h3 {
  color: #1e40af;
}

ul {
  padding-left: 18px;
  margin: 0;
  font-size: 14px;
  line-height: 1.8;
}

.empty {
  color: #9ca3af;
  font-size: 14px;
  margin: 0;
}

.problem-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.problem-item {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  padding: 12px;
}

.problem-title {
  font-weight: 600;
  margin-bottom: 6px;
}

.problem-suggestion {
  font-size: 13px;
  color: #1e40af;
}
</style>
