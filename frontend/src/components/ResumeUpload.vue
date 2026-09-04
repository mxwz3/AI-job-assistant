<script setup>
import { ref } from 'vue'
import { uploadResume } from '../api/resume.js'

const emit = defineEmits(['update:resume'])

const file = ref(null)
const loading = ref(false)
const result = ref(null)
const error = ref('')

function handleFileChange(event) {
  const selected = event.target.files[0]
  if (selected && selected.type !== 'application/pdf') {
    error.value = '请选择 PDF 格式的简历'
    file.value = null
    return
  }
  error.value = ''
  file.value = selected
}

async function handleUpload() {
  if (!file.value) {
    error.value = '请先选择简历文件'
    return
  }

  loading.value = true
  error.value = ''
  result.value = null

  try {
    result.value = await uploadResume(file.value)
    if (result.value.success) {
      emit('update:resume', result.value)
    }
  } catch (err) {
    error.value = err.message || '上传失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="resume-upload">
    <h2>上传简历</h2>

    <div class="usage-tips">
      <p class="tips-title">使用说明</p>
      <ul>
        <li>支持 PDF 格式简历</li>
        <li>建议简历控制在 1-3 页以内</li>
        <li>建议文本内容不超过 6000 字</li>
        <li>过长简历可能影响 AI 分析效果</li>
      </ul>
    </div>

    <div class="file-row">
      <input
        type="file"
        accept="application/pdf"
        @change="handleFileChange"
        class="file-input"
      />
      <button
        class="upload-btn"
        @click="handleUpload"
        :disabled="!file || loading"
      >
        {{ loading ? '解析中...' : '上传并解析' }}
      </button>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="result?.success" class="success-tip">
      ✅ 简历解析成功，已提取关键信息用于匹配分析
    </div>
    <div v-else-if="result?.success === false" class="error">
      解析失败：{{ result.error }}
    </div>
  </section>
</template>

<style scoped>
.resume-upload {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

h2 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #1f2937;
}

.usage-tips {
  margin: 0 0 16px;
  padding: 10px 14px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  color: #1e40af;
  font-size: 13px;
  line-height: 1.7;
}

.usage-tips .tips-title {
  margin: 0 0 2px;
  font-weight: 600;
}

.usage-tips ul {
  margin: 0;
  padding-left: 18px;
}

.usage-tips li {
  margin-bottom: 2px;
}

.file-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.file-input {
  flex: 1;
  min-width: 200px;
}

.upload-btn {
  padding: 10px 24px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 15px;
}

.upload-btn:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

.error {
  margin-top: 16px;
  color: #ef4444;
}

.success-tip {
  margin-top: 16px;
  color: #10b981;
  font-size: 14px;
}

/* 移动端：上传区改为纵向堆叠，按钮占满整行便于点击 */
@media (max-width: 767px) {
  .resume-upload {
    padding: 16px;
  }

  .file-row {
    flex-direction: column;
    align-items: stretch;
  }

  .file-input {
    min-width: 0;
  }

  .upload-btn {
    width: 100%;
  }
}
</style>
