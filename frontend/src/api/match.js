const API_BASE = '/api'

export async function matchResumeJd(resume, jd) {
  const response = await fetch(`${API_BASE}/match`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume, jd }),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || '匹配分析失败')
  }

  return data
}
