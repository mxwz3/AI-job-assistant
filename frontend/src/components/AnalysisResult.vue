<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Object, required: true },
})

const listCards = computed(() => [
  { title: '岗位职责', items: props.data.responsibilities, icon: '📋' },
  { title: 'AI 技能', items: props.data.ai_skills, icon: '🤖' },
  { title: '产品技能', items: props.data.product_skills, icon: '📦' },
  { title: '软技能', items: props.data.soft_skills, icon: '💬' },
  { title: '硬性要求', items: props.data.requirements, icon: '✅' },
])
</script>

<template>
  <section class="results">
    <h2 class="results-title">分析结果</h2>

    <div class="card summary-card">
      <h3>岗位名称</h3>
      <p>{{ data.job_title }}</p>
    </div>

    <div class="list-grid">
      <div
        v-for="card in listCards"
        :key="card.title"
        class="card list-card"
      >
        <h3>{{ card.icon }} {{ card.title }}</h3>
        <ul v-if="card.items?.length">
          <li v-for="(item, index) in card.items" :key="index">{{ item }}</li>
        </ul>
        <p v-else class="empty">暂无</p>
      </div>
    </div>
  </section>
</template>
