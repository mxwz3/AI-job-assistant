<script setup>
import { computed } from 'vue'

const props = defineProps({
  info: { type: Object, required: true },
  problems: { type: Array, default: () => [] },
})

const hasEducation = computed(() => props.info.school || props.info.major)

const advantages = computed(() => {
  const list = []
  if (props.info.skills?.length >= 5) {
    list.push(`技能覆盖较广，掌握 ${props.info.skills.length} 项技能`)
  } else if (props.info.skills?.length > 0) {
    list.push('具备核心技能：' + props.info.skills.slice(0, 3).join('、'))
  }
  if (props.info.projects?.length >= 2) {
    list.push(`项目经历丰富，共有 ${props.info.projects.length} 个项目`)
  } else if (props.info.projects?.length === 1) {
    list.push('有实际项目经验')
  }
  if (props.info.school) {
    list.push('教育背景完整')
  }
  return list
})

const potentialProblems = computed(() => {
  const list = []
  if (!props.info.skills?.length) {
    list.push('未识别到技能关键词，建议补充技术栈')
  }
  if (!props.info.projects?.length) {
    list.push('未识别到项目经历，建议补充项目案例')
  }
  if (!props.info.school || !props.info.major) {
    list.push('教育信息识别不完整，建议检查简历格式')
  }
  if (props.problems?.length) {
    props.problems.forEach((p) => {
      list.push(`${p.problem}：${p.suggestion}`)
    })
  }
  return list
})
</script>

<template>
  <section class="resume-analysis">
    <h2>简历分析</h2>

    <div class="analysis-grid">
      <div class="card base-info">
        <h3>基本信息</h3>
        <div class="info-row">
          <span class="label">姓名</span>
          <span class="value">{{ info.name || '未识别' }}</span>
        </div>
        <div class="info-row">
          <span class="label">学校</span>
          <span class="value">{{ info.school || '未识别' }}</span>
        </div>
        <div class="info-row">
          <span class="label">专业</span>
          <span class="value">{{ info.major || '未识别' }}</span>
        </div>
      </div>

      <div class="card skills-card">
        <h3>技能</h3>
        <div v-if="info.skills?.length" class="tags">
          <span v-for="skill in info.skills" :key="skill" class="tag">{{ skill }}</span>
        </div>
        <p v-else class="empty">未识别到技能</p>
      </div>

      <div class="card projects-card">
        <h3>项目经历</h3>
        <ul v-if="info.projects?.length">
          <li v-for="(project, index) in info.projects" :key="index">{{ project }}</li>
        </ul>
        <p v-else class="empty">未识别到项目经历</p>
      </div>

      <div class="card education-card">
        <h3>教育背景</h3>
        <p v-if="hasEducation" class="value">
          {{ info.school }} {{ info.major }}
        </p>
        <p v-else class="empty">未识别到完整教育背景</p>
      </div>
    </div>

    <div class="summary-row">
      <div class="card summary-card advantage">
        <h3>优势</h3>
        <ul v-if="advantages.length">
          <li v-for="(item, index) in advantages" :key="index">{{ item }}</li>
        </ul>
        <p v-else class="empty">暂无明确优势</p>
      </div>

      <div class="card summary-card problem">
        <h3>可能存在的问题</h3>
        <ul v-if="potentialProblems.length">
          <li v-for="(item, index) in potentialProblems" :key="index">{{ item }}</li>
        </ul>
        <p v-else class="empty">未发现明显问题</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.resume-analysis {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

h2 {
  margin: 0 0 16px;
  font-size: 18px;
  color: #1f2937;
}

h3 {
  margin: 0 0 12px;
  font-size: 15px;
  color: #374151;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.card {
  border-radius: 10px;
  padding: 16px;
  background: #f9fafb;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid #f3f4f6;
}

.info-row:last-child {
  border-bottom: none;
}

.label {
  color: #6b7280;
  font-size: 13px;
}

.value {
  color: #1f2937;
  font-weight: 600;
  font-size: 14px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: #eff6ff;
  color: #2563eb;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 13px;
}

ul {
  margin: 0;
  padding-left: 18px;
  font-size: 14px;
  color: #374151;
  line-height: 1.7;
}

li {
  margin-bottom: 6px;
}

.empty {
  color: #9ca3af;
  font-size: 14px;
  margin: 0;
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.summary-card {
  background: #f0fdf4;
}

.summary-card h3 {
  color: #166534;
}

.summary-card.problem {
  background: #fef2f2;
}

.summary-card.problem h3 {
  color: #991b1b;
}

.summary-card ul {
  color: #374151;
}
</style>
