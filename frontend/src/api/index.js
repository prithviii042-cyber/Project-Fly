const BASE = '/api'

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' }
  }
  if (body) opts.body = JSON.stringify(body)
  const res = await fetch(`${BASE}${path}`, opts)
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`)
  return data
}

export const api = {
  // Experiments
  listExperiments: () => request('GET', '/experiments'),
  getExperiment: (id) => request('GET', `/experiments/${id}`),
  createExperiment: (body) => request('POST', '/experiments', body),
  deleteExperiment: (id) => request('DELETE', `/experiments/${id}`),
  updateStatus: (id, status) => request('PATCH', `/experiments/${id}/status`, { status }),

  // Variants
  addVariant: (expId, body) => request('POST', `/experiments/${expId}/variants`, body),
  trackView: (expId, varId) => request('POST', `/experiments/${expId}/variants/${varId}/view`),
  trackConversion: (expId, varId) => request('POST', `/experiments/${expId}/variants/${varId}/convert`),

  // Claude AI
  analyzeExperiment: (id) => request('POST', `/experiments/${id}/analyze`),
  generateVariants: (body) => request('POST', '/experiments/generate-variants', body),
}
