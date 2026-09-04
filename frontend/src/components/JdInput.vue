<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

defineEmits(['update:modelValue', 'analyze'])
</script>

<template>
  <section class="card input-section">
    <label class="label" for="jd-input">招聘 JD</label>
    <textarea
      id="jd-input"
      class="textarea"
      :value="modelValue"
      placeholder="在此粘贴完整的招聘岗位描述（JD）..."
      rows="12"
      :disabled="loading"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <div class="actions">
      <button
        class="btn-primary"
        type="button"
        :disabled="loading || !modelValue.trim()"
        @click="$emit('analyze')"
      >
        {{ loading ? '分析中...' : '开始分析' }}
      </button>
    </div>
  </section>
</template>
