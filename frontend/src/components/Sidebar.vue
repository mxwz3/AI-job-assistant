<script setup>
import { ref } from 'vue'

const props = defineProps({
  activeSection: {
    type: String,
    default: 'section-resume',
  },
})

const emit = defineEmits(['navigate'])

// 移动端菜单展开状态（桌面端 CSS 下菜单始终显示，此状态无影响）
const menuOpen = ref(false)

// 核心工作流五步导航：仅保留岗位匹配闭环的关键阶段
const menuItems = [
  { icon: '📄', label: '上传简历', section: 'section-resume' },
  { icon: '📋', label: '上传 JD', section: 'section-jd' },
  { icon: '📊', label: '匹配分析', section: 'section-match' },
  { icon: '✨', label: '优化建议', section: 'section-optimization' },
  { icon: '📝', label: '优化后简历', section: 'section-optimized-resume' },
]

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}

function handleClick(section) {
  menuOpen.value = false
  emit('navigate', section)
}
</script>

<template>
  <aside class="sidebar">
    <div class="logo">
      <span class="logo-icon">🤖</span>
      <span class="logo-text">AI求职助手</span>
    </div>

    <button
      class="menu-toggle"
      type="button"
      aria-label="打开导航菜单"
      @click="toggleMenu"
    >
      ☰
    </button>

    <!-- 移动端展开菜单时的透明遮罩，点击关闭 -->
    <div
      v-if="menuOpen"
      class="menu-backdrop"
      @click="menuOpen = false"
    ></div>

    <nav class="menu" :class="{ open: menuOpen }">
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

/* 汉堡按钮与遮罩仅在移动端显示 */
.menu-toggle {
  display: none;
}

.menu-backdrop {
  display: none;
}

/* 移动端：侧边栏变为 sticky 顶部导航条，菜单折叠为下拉面板 */
@media (max-width: 767px) {
  .sidebar {
    position: sticky;
    top: 0;
    z-index: 40;
    width: 100%;
    min-width: 100%;
    height: auto;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
    overflow: visible;
  }

  .logo {
    padding: 10px 14px;
    border-bottom: none;
  }

  .logo-icon {
    font-size: 18px;
  }

  .logo-text {
    font-size: 16px;
  }

  .menu-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    margin-right: 10px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background: #fff;
    color: #1f2937;
    font-size: 18px;
    line-height: 1;
    cursor: pointer;
  }

  /* 菜单默认收起（占位为 0），展开时为绝对定位下拉面板 */
  .menu {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    flex-direction: column;
    padding: 8px 12px 12px;
    gap: 2px;
    background: #fff;
    border-bottom: 1px solid #e5e7eb;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    max-height: 60vh;
    overflow-y: auto;
  }

  .menu.open {
    display: flex;
  }

  .menu-item {
    padding: 12px 14px;
    font-size: 15px;
  }

  .menu-icon {
    font-size: 17px;
    width: 24px;
  }

  .menu-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: -1;
    background: rgba(0, 0, 0, 0.25);
  }
}
</style>
