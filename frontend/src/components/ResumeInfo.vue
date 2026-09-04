<script setup>
const props = defineProps({
  info: { type: Object, required: true },
})

const emit = defineEmits(['reset'])
</script>

<template>
  <section class="resume-info">
    <div class="section-header">
      <h2>简历信息</h2>
      <button class="reset-btn" @click="$emit('reset')">重新上传</button>
    </div>
    <div class="info-grid">
      <div class="info-item">
        <span class="label">姓名</span>
        <span class="value">{{ info.name || '未识别' }}</span>
      </div>
      <div class="info-item">
        <span class="label">学校</span>
        <span class="value">{{ info.school || '未识别' }}</span>
      </div>
      <div class="info-item">
        <span class="label">专业</span>
        <span class="value">{{ info.major || '未识别' }}</span>
      </div>
    </div>

    <div class="info-block">
      <span class="label">技能</span>
      <div v-if="info.skills?.length" class="tags">
        <span v-for="skill in info.skills" :key="skill" class="tag">{{ skill }}</span>
      </div>
      <span v-else class="empty">未识别到技能</span>
    </div>

    <div class="info-block">
      <span class="label">项目经历</span>
      <ul v-if="info.projects?.length">
        <li v-for="(project, index) in info.projects" :key="index">{{ project }}</li>
      </ul>
      <span v-else class="empty">未识别到项目经历</span>
    </div>
  </section>
</template>

<style scoped>
.resume-info {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

h2 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
}

.reset-btn {
  padding: 6px 14px;
  background: #fff;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
}

.reset-btn:hover {
  color: #2563eb;
  border-color: #bfdbfe;
  background: #eff6ff;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-block {
  margin-top: 16px;
}

.label {
  color: #6b7280;
  font-size: 13px;
}

.value {
  color: #1f2937;
  font-weight: 600;
  font-size: 15px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.tag {
  background: #eff6ff;
  color: #2563eb;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 13px;
}

.empty {
  color: #9ca3af;
  font-size: 14px;
  margin-top: 6px;
}

ul {
  margin-top: 8px;
  padding-left: 18px;
  color: #374151;
  font-size: 14px;
}

li {
  margin-bottom: 6px;
}
</style>
