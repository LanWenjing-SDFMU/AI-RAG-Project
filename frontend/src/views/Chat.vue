<template>
  <div class="chat-container">
    <!-- 顶部标题栏 -->
    <div class="chat-header">
      <div class="header-left">
        <span class="header-icon">💬</span>
        <div class="header-info">
          <h2 class="header-title">智能临床问答</h2>
          <p class="header-subtitle">基于RAG的病症分析与药物推荐系统</p>
        </div>
      </div>
      <div class="header-right">
        <el-button size="small" :icon="Delete" @click="clearMessages" class="clear-btn">清空对话</el-button>
      </div>
    </div>

    <!-- 消息主体区域 -->
    <div class="chat-body" ref="messagesRef">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message-row', msg.role === 'user' ? 'row-user' : 'row-assistant']"
      >
        <!-- 对方消息（AI）：头像在左，气泡在右 -->
        <template v-if="msg.role === 'assistant'">
          <div class="avatar avatar-assistant">🩺</div>
          <div class="message-content">
            <div class="message-bubble bubble-assistant" v-html="renderMarkdown(msg.content)"></div>
          </div>
        </template>
        <!-- 自己消息（用户）：气泡在左，头像在右 -->
        <template v-else>
          <div class="message-content">
            <div class="message-bubble bubble-user" v-html="renderMarkdown(msg.content)"></div>
          </div>
          <div class="avatar avatar-user">👤</div>
        </template>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="message-row row-assistant">
        <div class="avatar avatar-assistant">🩺</div>
        <div class="message-content">
          <div class="message-bubble bubble-assistant">
            <span class="thinking-dots">正在思考</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部输入区域 -->
    <div class="chat-footer">
      <div class="input-wrapper">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="2"
          placeholder="例如：我咳嗽（干咳无痰），推荐什么药？"
          @keydown.enter.exact.prevent="sendMessage"
          class="chat-textarea"
        />
        <el-button
          type="primary"
          :icon="Promotion"
          :loading="loading"
          @click="sendMessage"
          class="send-btn"
        >
          发送
        </el-button>
      </div>
      <div class="input-hint">💡 提示：您可以直接描述症状，机器人将基于知识库给出建议。</div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { Delete, Promotion } from '@element-plus/icons-vue'
import { chatApi } from '@/api'
import { useUserStore } from '@/stores/user'
import { marked } from 'marked'

const userStore = useUserStore()
const messagesRef = ref(null)
const inputText = ref('')
const loading = ref(false)

const messages = ref([
  {
    role: 'assistant',
    content: '请医生输入病症？',
    timestamp: new Date().toLocaleTimeString(),
  },
])

function renderMarkdown(content) {
  if (!content) return ''
  return marked(content)
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

async function clearMessages() {
  try {
    await chatApi.clearHistory('default', userStore.workId)
  } catch (err) {
    console.error('清空历史记录失败:', err)
  }
  messages.value = [
    {
      role: 'assistant',
      content: '对话已清空，请重新输入症状。',
      timestamp: new Date().toLocaleTimeString(),
    },
  ]
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  messages.value.push({
    role: 'user',
    content: text,
    timestamp: new Date().toLocaleTimeString(),
  })
  inputText.value = ''
  scrollToBottom()

  loading.value = true

  // 先插入一个空的 AI 消息占位
  const aiMsgIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: '',
    timestamp: new Date().toLocaleTimeString(),
  })

  try {
    const token = localStorage.getItem('token') || ''
    const operator = userStore.workId
    const url = `/api/chat/qa?operator=${encodeURIComponent(operator)}`
    const body = JSON.stringify({ input: text, session_id: 'default' })

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body,
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // 保留最后一个不完整的行

      for (const line of lines) {
        if (!line.trim()) continue
        try {
          const parsed = JSON.parse(line)
          if (parsed.response) {
            messages.value[aiMsgIndex].content += parsed.response
            scrollToBottom()
          }
        } catch (e) {
          // 忽略解析错误
        }
      }
    }

    // 处理缓冲区剩余内容
    if (buffer.trim()) {
      try {
        const parsed = JSON.parse(buffer)
        if (parsed.response) {
          messages.value[aiMsgIndex].content += parsed.response
        }
      } catch (e) {}
    }

    // 如果最终内容为空，显示默认提示
    if (!messages.value[aiMsgIndex].content) {
      messages.value[aiMsgIndex].content = '抱歉，没有检索到相关信息。'
    }
  } catch (err) {
    console.error('发送消息失败:', err)
    messages.value[aiMsgIndex].content = '抱歉，服务出现错误，请稍后重试。'
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
/* ========================================
   整体容器
   ======================================== */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f0f2f5;
}

/* ========================================
   顶部标题栏
   ======================================== */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: #fff;
  border-bottom: 1px solid #e8eaed;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 26px;
}

.header-info {
  display: flex;
  flex-direction: column;
}

.header-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1.3;
}

.header-subtitle {
  margin: 0;
  font-size: 12px;
  color: #999;
  line-height: 1.3;
}

.clear-btn {
  flex-shrink: 0;
}

/* ========================================
   消息主体区域
   ======================================== */
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 18px;
}

/* ===== 每条消息行 ===== */
.message-row {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
  align-items: flex-start;
}

.row-assistant {
  justify-content: flex-start;
}

.row-user {
  justify-content: flex-end;
}

/* ===== 头像 ===== */
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.avatar-assistant {
  background: #e8f5e9;
}

.avatar-user {
  background: #e3f2fd;
}

/* ===== 消息内容容器 ===== */
.message-content {
  max-width: 560px;
  min-width: 40px;
  display: flex;
  flex-direction: column;
}

/* ===== 气泡 - 紧凑排版 ===== */
.message-bubble {
  padding: 8px 12px;
  font-size: 14px;
  line-height: 1.55;
  word-break: break-word;
  white-space: pre-wrap;
}

.bubble-assistant {
  background: #fff;
  color: #1a1a1a;
  border-radius: 4px 12px 12px 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.bubble-user {
  background: #409EFF;
  color: #fff;
  border-radius: 12px 4px 12px 12px;
}

/* ===== 气泡内 Markdown 紧凑排版 ===== */
.message-bubble :deep(p) {
  margin: 3px 0;
}

.message-bubble :deep(p:first-child) {
  margin-top: 0;
}

.message-bubble :deep(p:last-child) {
  margin-bottom: 0;
}

.message-bubble :deep(ul),
.message-bubble :deep(ol) {
  margin: 3px 0;
  padding-left: 18px;
}

.message-bubble :deep(li) {
  margin: 1px 0;
  line-height: 1.55;
}

.message-bubble :deep(li > p) {
  margin: 1px 0;
}

.message-bubble :deep(strong) {
  font-weight: 600;
}

.message-bubble :deep(code) {
  background: rgba(0, 0, 0, 0.06);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 13px;
}

.bubble-user :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}

.message-bubble :deep(pre) {
  background: rgba(0, 0, 0, 0.04);
  padding: 8px 10px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 4px 0;
  font-size: 13px;
  line-height: 1.4;
}

.message-bubble :deep(pre code) {
  background: none;
  padding: 0;
  font-size: 13px;
}

.message-bubble :deep(h1),
.message-bubble :deep(h2),
.message-bubble :deep(h3),
.message-bubble :deep(h4) {
  margin: 5px 0 2px;
  font-size: 14px;
  font-weight: 600;
}

.message-bubble :deep(hr) {
  border: none;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  margin: 6px 0;
}

.message-bubble :deep(blockquote) {
  margin: 4px 0;
  padding: 2px 0 2px 10px;
  border-left: 3px solid #ddd;
  color: #666;
}

.message-bubble :deep(blockquote p) {
  margin: 1px 0;
}

.message-bubble :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 4px 0;
  font-size: 13px;
}

.message-bubble :deep(th),
.message-bubble :deep(td) {
  border: 1px solid #e0e0e0;
  padding: 4px 8px;
  text-align: left;
}

.message-bubble :deep(th) {
  background: rgba(0, 0, 0, 0.03);
  font-weight: 600;
}

.message-bubble :deep(a) {
  color: #409EFF;
  text-decoration: none;
}

/* ===== 时间戳 ===== */
.message-time {
  font-size: 11px;
  color: #b0b0b0;
  margin-top: 3px;
}

.row-assistant .message-time {
  text-align: left;
  padding-left: 2px;
}

.time-user {
  text-align: right;
  padding-right: 2px;
}

/* ========================================
   底部输入区域
   ======================================== */
.chat-footer {
  flex-shrink: 0;
  background: #fff;
  border-top: 1px solid #e8eaed;
  padding: 10px 18px 14px;
}

.input-wrapper {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.chat-textarea {
  flex: 1;
}

.send-btn {
  height: 52px;
  padding: 0 24px;
  font-size: 15px;
  border-radius: 6px;
  flex-shrink: 0;
}

.input-hint {
  font-size: 12px;
  color: #b0b0b0;
  margin-top: 6px;
  text-align: center;
}

/* ========================================
   思考动画
   ======================================== */
.thinking-dots::after {
  content: '';
  animation: dots 1.5s infinite;
}

@keyframes dots {
  0% { content: ''; }
  25% { content: '.'; }
  50% { content: '..'; }
  75% { content: '...'; }
  100% { content: ''; }
}
</style>
