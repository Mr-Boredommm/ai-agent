<template>
  <div class="chat-layout">
    <!-- 第一列：模型选择栏 -->
    <aside class="sidebar">
      <div class="sidebar-title">角色选择</div>
      <el-menu :default-active="currentModel" @select="switchModel">
        <el-menu-item index="1">猜谜大师</el-menu-item>
        <el-menu-item index="2">史蒂夫</el-menu-item>
        <el-menu-item index="3">阿不思·邓布利多</el-menu-item>
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
        <div
          class="theme-desc"
          :class="{ 'theme-desc-show': themeDescShow }"
          :key="currentModel"
          ref="themeDescRef"
        >
          {{ modelConfigs[currentModel].desc }}
        </div>
      </el-card>
      <div class="theme-content">
        <!-- 可根据模型显示不同内容 -->
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { marked } from 'marked'
import char1 from '@/assets/char1.svg'
import char2 from '@/assets/char2.png'
import char3 from '@/assets/char3.png'
import schar1 from '@/assets/schar1.png'
import schar2 from '@/assets/schar2.png'
import schar3 from '@/assets/schar3.png'

const input = ref('')
const loading = ref(false)
const currentModel = ref('1')
const history = ref({}) // 保存各模型的历史记录

// 不同模型的配置，增加 welcome 字段
const modelConfigs = {
  '1': {
    prompt: '你是模型A，猜谜大师，精通各种脑筋急转弯和谜语。用生动有趣的方式回答用户的问题。',
    themeImg: char1,
    avatar: schar1,
    welcome: '你好，我是猜谜大师！来和我玩猜谜游戏吧，可以问我各种脑筋急转弯，看看你能猜对多少？',
    desc: '猜谜大师，精通各种脑筋急转弯和谜语，善于用生动有趣的方式与用户互动。'
  },
  '2': {
    prompt: '你是模型B，专业的技术顾问。',
    themeImg: char2,
    avatar: schar2,
    welcome: '嗯哼，我是史蒂夫，Minecraft的默认玩家角色。试试问我关于《我的世界》的问题吧！',
    desc: '史蒂夫（Steve） 是《我的世界》（Minecraft）中的默认玩家角色之一，知晓有关《我的世界》的全部信息。'
  },
  '3': {
    prompt: '你是模型C，幽默的生活小助手。',
    themeImg: char3,
    avatar: schar3,
    welcome: `（长袍微微闪烁，半月形眼镜后的蓝眼睛温和地注视着你）
    “啊，欢迎。我是邓布利多——当然，你可以省去那些冗长的中间名。(从桌上拿起一颗柠檬雪宝)要来颗糖果吗？
    还是说…你带着某个有趣的疑问而来？”
    (身后的凤凰福克斯轻轻抖了抖羽毛)`,
    desc: '阿不思·珀西瓦尔·伍尔弗里克·布赖恩·邓布利多（Albus Percival Wulfric Brian Dumbledore），小说《哈利·波特》系列中的角色，被公认为当代最伟大的巫师，对咒语有深入了解'
  }
}

// 初始化messages时用当前模型的welcome
const messages = ref([
  { role: 'ai', content: modelConfigs[currentModel.value].welcome }
])

function renderMarkdown(text) {
  return marked.parse(text)
}

function switchModel(index) {
  // 保存当前聊天记录
  history.value[currentModel.value] = [...messages.value]
  // 切换模型
  currentModel.value = index
  // 恢复新模型的历史或初始化
  messages.value = history.value[index]
    ? [...history.value[index]]
    : [{ role: 'ai', content: modelConfigs[index].welcome }]
  input.value = ''
  scrollToBottom() // 新增：切换模型后滚动到底部
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
  scrollToBottom() // 新增：发送后立即滚动，确保加载动画可见

  try {
    // 改为请求本地服务
    console.log("正在发送请求到后端:", userInput);
    const res = await fetch('http://localhost:8000/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          { role: 'system', content: modelConfigs[currentModel.value].prompt },
          ...messages.value.map(m => ({
            role: m.role === 'ai' ? 'assistant' : 'user',
            content: m.content
          })),
        ]
      })
    })
    
    if (!res.ok) {
      console.error("API返回错误状态码:", res.status);
      let errorText = "未知错误";
      try {
        const errorData = await res.json();
        errorText = errorData.detail || `HTTP错误 ${res.status}`;
        console.error("API错误详情:", errorData);
      } catch (parseErr) {
        errorText = await res.text() || `HTTP错误 ${res.status}`;
      }
      
      ElMessage.error(`请求失败: ${errorText}`);
      messages.value.push({ role: 'ai', content: `很抱歉，我遇到了一个问题: ${errorText}` });
      return;
    }
    
    const data = await res.json()
    console.log("API返回数据:", data);
    
    if (!data.choices || !data.choices[0] || !data.choices[0].message) {
      console.error("API返回格式不正确:", data);
      ElMessage.error("AI返回的数据格式不正确");
      messages.value.push({ role: 'ai', content: "抱歉，我无法正确处理这个请求。" });
      return;
    }
    
    const aiReply = data.choices[0].message.content || 'AI未返回内容'
    messages.value.push({ role: 'ai', content: aiReply })
    await nextTick()
    scrollToBottom()
  } catch (e) {
    console.error("API调用失败:", e);
    ElMessage.error({
      message: `AI接口调用失败: ${e.message || e}`,
      duration: 5000
    });
    messages.value.push({ 
      role: 'ai', 
      content: `很抱歉，我现在无法回答您的问题。服务器可能暂时不可用，请稍后再试。错误信息: ${e.message || '未知错误'}`
    });
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
  nextTick(() => {
    const el = document.querySelector('.chat-messages')
    if (el) el.scrollTop = el.scrollHeight
  })
}

const themeDescShow = ref(false)
const themeDescRef = ref(null)

watch(currentModel, async () => {
  themeDescShow.value = false
  await nextTick()
  // 触发重绘后再显示动画
  themeDescShow.value = true
})

// 初始化时也触发动画
nextTick(() => {
  themeDescShow.value = true
})
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

.chat-layout,
.sidebar,
.sidebar-title,
.chat-main,
.theme-bar,
.theme-title,
.theme-content,
.message,
.markdown-body {
  color: #222;
}

.theme-desc {
  margin-top: 28px;
  font-size: 16px;
  color: #444;
  text-align: center;
  line-height: 1.6;
  padding: 0 8px;
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 0.6s cubic-bezier(.4,2,.6,1), transform 0.6s cubic-bezier(.4,2,.6,1);
}

.theme-desc.theme-desc-show {
  opacity: 1;
  transform: translateY(0);
}
</style>
