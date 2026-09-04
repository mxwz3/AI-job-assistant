const API_BASE = '/api'

export async function uploadResume(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/upload_resume`, {
    method: 'POST',
    body: formData,
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || '简历上传失败')
  }

  return data
}

async function fetchPdfBlob(resumeInfo) {
  const response = await fetch(`${API_BASE}/resume/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(resumeInfo),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail || 'PDF 生成失败')
  }

  return response.blob()
}

export async function fetchResumePdfBlob(resumeInfo) {
  return fetchPdfBlob(resumeInfo)
}

export async function downloadResumePdf(resumeInfo, filenamePrefix = '优化后简历') {
  const blob = await fetchPdfBlob(resumeInfo)
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${filenamePrefix}_${resumeInfo.name || '未知'}.pdf`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
