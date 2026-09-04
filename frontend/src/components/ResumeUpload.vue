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
    <p class="hint">仅支持 PDF 格式</p>

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

.hint {
  margin: 0 0 16px;
  color: #6b7280;
  font-size: 14px;
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
</style>
