<script setup>
const props = defineProps({
  activeSection: {
    type: String,
    default: 'section-resume',
  },
})

const emit = defineEmits(['navigate'])

// 核心工作流五步导航：仅保留岗位匹配闭环的关键阶段
const menuItems = [
  { icon: '📄', label: '上传简历', section: 'section-resume' },
  { icon: '📋', label: '上传 JD', section: 'section-jd' },
  { icon: '📊', label: '匹配分析', section: 'section-match' },
  { icon: '✨', label: '优化建议', section: 'section-optimization' },
  { icon: '📝', label: '优化后简历', section: 'section-optimized-resume' },
]

function handleClick(section) {
  emit('navigate', section)
}
</script>

<template>
  <aside class="sidebar">
    <div class="logo">
      <span class="logo-icon">🤖</span>
      <span class="logo-text">AI求职助手</span>
    </div>

    <nav class="menu">
      <a
        v-for="item in menuItems"
        :key="item.section"
        href="javascript:;"
        :class="['menu-item', { active: activeSection === item.section }]"
        @click="handleClick(item.section)"
      >
        <span class="menu-icon">{{ item.icon }}</span>
        <span class="menu-label">{{ item.label }}</span>
      </a>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 220px;
  min-width: 220px;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow-y: auto;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 20px;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.logo-icon {
  font-size: 22px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
}

.menu {
  display: flex;
  flex-direction: column;
  padding: 12px 14px;
  gap: 4px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  color: #4b5563;
  text-decoration: none;
  font-size: 14px;
  transition: background 0.2s;
  cursor: pointer;
}

.menu-item:hover {
  background: #f3f4f6;
}

.menu-item.active {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 600;
}

.menu-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

/* 移动端：侧边栏转为顶部导航，菜单可横向滑动 */
@media (max-width: 767px) {
  .sidebar {
    width: 100%;
    min-width: 100%;
    height: auto;
    flex-direction: row;
    align-items: center;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
    overflow: visible;
  }

  .logo {
    padding: 10px 12px 10px 14px;
    border-bottom: none;
    flex-shrink: 0;
  }

  .logo-icon {
    font-size: 18px;
  }

  .logo-text {
    font-size: 15px;
  }

  .menu {
    flex-direction: row;
    flex: 1;
    min-width: 0;
    padding: 8px 10px 8px 4px;
    gap: 2px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .menu-item {
    flex-shrink: 0;
    gap: 6px;
    padding: 8px 10px;
    font-size: 13px;
  }

  .menu-icon {
    font-size: 15px;
    width: auto;
  }
}
</style>
