const API_BASE = '/api'

export async function analyzeJd(jdText) {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jd_text: jdText }),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || '分析请求失败')
  }

  return data
}
