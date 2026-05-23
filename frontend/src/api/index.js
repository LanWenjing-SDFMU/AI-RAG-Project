import request from './request'

// ==================== 认证 ====================
export const authApi = {
  login(data) {
    return request.post('/auth/login', data)
  },
  register(data) {
    return request.post('/auth/register', data)
  },
}

// ==================== 仪表盘 ====================
export const dashboardApi = {
  getStats() {
    return request.get('/dashboard/stats')
  },
}

// ==================== 诊断记录 ====================
export const diagnosisApi = {
  getRecords(search = '') {
    return request.get('/diagnosis/records', { params: { search } })
  },
  getRecord(id) {
    return request.get(`/diagnosis/records/${id}`)
  },
  createRecord(data, operator = '') {
    return request.post('/diagnosis/records', data, { params: { operator } })
  },
  updateRecord(id, data, operator = '') {
    return request.put(`/diagnosis/records/${id}`, data, { params: { operator } })
  },
  deleteRecord(id, operator = '') {
    return request.delete(`/diagnosis/records/${id}`, { params: { operator } })
  },
  syncToKB(id, operator = '') {
    return request.post(`/diagnosis/records/${id}/sync-kb`, null, { params: { operator } })
  },
}

// ==================== 知识库 ====================
export const kbApi = {
  getDocuments() {
    return request.get('/knowledge-base/documents')
  },
  uploadFile(file, operator = '') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('operator', operator)
    return request.post('/knowledge-base/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  deleteDocument(sourceName, operator = '') {
    return request.delete(`/knowledge-base/documents/${encodeURIComponent(sourceName)}`, {
      params: { operator },
    })
  },
}

// ==================== 智能问答 ====================
export const chatApi = {
  sendMessage(data, operator = '') {
    return request.post('/chat/qa', data, { params: { operator } })
  },
  clearHistory(sessionId = 'default', operator = '') {
    return request.post('/chat/clear-history', null, {
      params: { session_id: sessionId, operator },
    })
  },
}

// ==================== 鉴别诊断 ====================
export const diagnosisAssistApi = {
  generate(data, operator = '') {
    return request.post('/diagnosis-assist/generate', data, { params: { operator } })
  },
}

// ==================== 用药安全核查 ====================
export const drugSafetyApi = {
  check(data, operator = '') {
    return request.post('/drug-safety/check', data, { params: { operator } })
  },
}

// ==================== 操作日志 ====================
export const logApi = {
  getList(params) {
    return request.get('/logs/list', { params })
  },
  getStats() {
    return request.get('/logs/stats')
  },
  getActionTypes() {
    return request.get('/logs/action-types')
  },
}
