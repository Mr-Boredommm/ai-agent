<template>
  <div class="chat-layout">
    <!-- 第一列：模型选择栏 -->
    <aside class="sidebar">
      <div class="sidebar-title">角色选择</div>
      <el-menu :default-active="currentModel" @select="switchModel">
        <el-menu-item index="1">模型A</el-menu-item>
        <el-menu-item index="2">模型B</el-menu-item>
        <el-menu-item index="3">模型C</el-menu-item>
      </el-menu>
    </aside>

    <!-- 第二列：对话主界面 -->
    <main class="chat-main">
      <div class="chat-messages">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="message"
          :class="msg.role"
        >
          <!-- 用头像替换“AI:”字样，仅AI消息显示头像 -->
          <img
            v-if="msg.role === 'ai'"
            :src="modelConfigs[currentModel].avatar"
            alt="AI头像"
            class="ai-avatar"
          />
          <span
            v-if="msg.role === 'ai'"
            v-html="renderMarkdown(msg.content)"
            class="markdown-body"
          ></span>
          <span v-else>{{ msg.content }}</span>
        </div>
        <!-- 新增：加载动画 -->
        <div v-if="loading" class="message ai loading-message">
          <span class="dot-flashing"></span>
          <span style="margin-left:8px;">AI正在思考...</span>
        </div>
      </div>
      <div class="chat-input-bar">
        <el-input
          v-model="input"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 3 }"
          placeholder="请输入内容"
          class="chat-input"
          @keyup.enter="send"
          clearable
          :disabled="loading"
        >
          <template #append>
            <el-button type="primary" @click="send" :loading="loading">发送</el-button>
          </template>
        </el-input>
      </div>
    </main>

    <!-- 第三列：主题元素 -->
    <aside class="theme-bar">
      <el-card>
        <img :src="modelConfigs[currentModel].themeImg" alt="本地图片" class="theme-img" />
      </el-card>
      <div class="theme-content">
        <!-- 可根据模型显示不同内容 -->
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { marked } from 'marked'
import char1 from '@/assets/char1.jpg'
import schar1 from '@/assets/schar1.png'

const input = ref('')
const messages = ref([
  { role: 'ai', content: '喵？' },
])
const loading = ref(false)

/* ====== DeepSeek API  ====== */
/* ====== DeepSeek API  ====== */
const DEEPSEEK_API_KEY = 'sk-cf33434e04a24ceb99c20e9d99c846ff'
/* ====== DeepSeek API  ====== */
/* ====== DeepSeek API  ====== */

function renderMarkdown(text) {
  return marked.parse(text)
}

/* ====== DeepSeek API 调用与对话传输部分开始 ====== */
/* ====== DeepSeek API 调用与对话传输部分开始 ====== */
/* ====== DeepSeek API 调用与对话传输部分开始 ====== */
/* ====== DeepSeek API 调用与对话传输部分开始 ====== */
/* ====== DeepSeek API 调用与对话传输部分开始 ====== */
async function send() {
  const userInput = input.value.trim()
  if (!userInput) return

  messages.value.push({ role: 'user', content: userInput })
  input.value = ''
  loading.value = true

  try {
    const res = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEEPSEEK_API_KEY}`
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          { role: 'system', content: 'You are a helpful assistant.' },
          ...messages.value.map(m => ({
            role: m.role === 'ai' ? 'assistant' : 'user',
            content: m.content
          })),
        ]
      })
    })
    const data = await res.json()
    const aiReply = data.choices?.[0]?.message?.content || 'AI未返回内容'
    messages.value.push({ role: 'ai', content: aiReply })
    await nextTick()
    scrollToBottom()
  } catch (e) {
    ElMessage.error('AI接口调用失败')
  } finally {
    loading.value = false
  }
}
/* ====== DeepSeek API 调用与对话传输部分结束 ====== */
/* ====== DeepSeek API 调用与对话传输部分结束 ====== */
/* ====== DeepSeek API 调用与对话传输部分结束 ====== */
/* ====== DeepSeek API 调用与对话传输部分结束 ====== */
/* ====== DeepSeek API 调用与对话传输部分结束 ====== */

function scrollToBottom() {
  const el = document.querySelector('.chat-messages')
  if (el) el.scrollTop = el.scrollHeight
}
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: #f5f6fa;
  font-size: 18px; /* 全局字体调大 */
}

.sidebar {
  width: 15vw;
  min-width: 180px;
  max-width: 260px;
  background: #fff;
  border-right: 1px solid #ebeef5;
  padding: 28px 16px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.sidebar-title {
  font-weight: bold;
  margin-bottom: 20px;
  font-size: 22px; /* 标题更大 */
}

.chat-main {
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  padding: 32px;
  box-sizing: border-box;
  background: #f9fafc;
  font-size: 18px; /* 主区字体加大 */
}

.chat-messages {
  flex: 1 1 0;
  overflow-y: auto;
  margin-bottom: 20px;
  padding-right: 12px;
}

.message {
  margin-bottom: 16px;
  padding: 14px 22px;
  border-radius: 10px;
  max-width: 75%;
  word-break: break-all;
  font-size: 16px;
}

.message.ai {
  background: #e6f7ff;
  align-self: flex-start;
}

.message.user {
  background: #d3f9d8;
  align-self: flex-end;
  margin-left: auto;
}

.chat-input-bar {
  display: flex;
  align-items: center;
}

.chat-input {
  width: 100%;
  font-size: 18px;
  /* 让textarea最多显示三行，超出显示滚动条 */
  .el-textarea__inner {
    resize: none;
    max-height: 110px; /* 约等于3行，略加高 */
    overflow-y: auto;
    font-size: 16px;
  }
}

.theme-bar {
  width: 27vw;
  min-width: 260px;
  max-width: 440px;
  background: #fff;
  border-left: 1px solid #ebeef5;
  padding: 28px 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  font-size: 18px;
}

.theme-content {
  flex: 1 1 0;
}

/* markdown 样式字体同步加大 */
.markdown-body h1,
.markdown-body h2,
.markdown-body h3 {
  font-weight: bold;
  margin: 12px 0 8px 0;
  font-size: 1.25em;
}
.markdown-body p {
  margin: 0 0 10px 0;
  font-size: 1em;
}
.markdown-body strong {
  font-weight: bold;
}
.markdown-body code {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 1em;
}
.markdown-body ul, .markdown-body ol {
  margin: 0 0 10px 24px;
  font-size: 1em;
}
.markdown-body blockquote {
  border-left: 4px solid #e6f7ff;
  background: #f6f8fa;
  margin: 10px 0;
  padding: 8px 16px;
  color: #555;
  font-style: italic;
  font-size: 1em;
}

/* 加载动画样式 */
.dot-flashing {
  position: relative;
  width: 16px;
  height: 16px;
  border-radius: 8px;
  background-color: #409eff;
  color: #409eff;
  animation: dotFlashing 1s infinite linear alternate;
  display: inline-block;
}
@keyframes dotFlashing {
  0% { opacity: 1; }
  50% { opacity: .3; }
  100% { opacity: 1; }
} 

.theme-img {
  width: 100%;
  padding: 8px;
  object-fit: cover;
  transition: transform 0.3s cubic-bezier(.4,2,.6,1), box-shadow 0.3s;
  box-shadow: none;
}

.theme-img:hover {
  transform: scale(1.08);
  box-shadow: 0 8px 28px #409eff55;
  z-index: 2;
}

/* AI头像样式同步加大 */
.ai-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 12px;
  vertical-align: middle;
  border: 1.5px solid #1a237e; /* 深蓝色描边 */
  transition: transform 0.3s cubic-bezier(.4,2,.6,1), box-shadow 0.3s;
  box-shadow: none;
}

.ai-avatar:hover {
  transform: scale(1.08);
  box-shadow: 0 8px 28px #409eff55;
  z-index: 2;
}
</style>
