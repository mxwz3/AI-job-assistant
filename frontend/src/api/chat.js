const API_BASE = '/api'

export async function sendChatMessage({
  message,
  resume,
  originalResume,
  optimizedResume,
  jd,
  matchResult,
  optimizedMatchResult,
  originalMatchScore,
  optimizedMatchScore,
  history,
}) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      resume: resume || '',
      original_resume: originalResume || '',
      optimized_resume: optimizedResume || '',
      jd: jd || '',
      match_result: matchResult || null,
      optimized_match_result: optimizedMatchResult || null,
      original_match_score: originalMatchScore ?? null,
      optimized_match_score: optimizedMatchScore ?? null,
      history: history || [],
    }),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || 'AI 回复失败')
  }

  return data
}
