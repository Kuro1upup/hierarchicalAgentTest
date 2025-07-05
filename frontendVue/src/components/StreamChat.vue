<template>
  <div class="chat-container">
    <div class="chat-header">
      <h1>Hierarchical Agent Teams</h1>
    </div>
    
    <div class="chat-interface">
      <!-- 对话区域 -->
      <div ref="historyContainer" class="chat-history">
        <div v-for="(message, index) in messages" 
             :key="index" 
             class="message" 
             :class="message.role">
          <div class="avatar">
            <div v-if="message.role === 'assistant'" class="ai-avatar">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
              </svg>
            </div>
            <div v-else class="user-avatar">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path fill-rule="evenodd" d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
          <div class="content">
            <div v-if="message.isLoading" class="loading-indicator">
              <span class="indicator">Routing:</span>
              <div v-for="(agent, index) in message.agents" :key="index" class="path-node">
                {{ agent.current }} -> {{ agent.next }}
              </div>
            </div>
            <div v-else>
              <div v-if="message.role === 'assistant' && message.isStreaming">
                <TypingEffect 
                  :text="message.content" 
                  :isTypeing="isProcessing"
                  @complete="onTypingComplete(index)"
                />
              </div>
              <div v-else class="static-text">
                {{ message.content }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="input-area">
        <div class="input-container">
          <textarea 
            v-model="inputText" 
            @keydown.enter.exact.prevent="sendMessage"
            placeholder="Please enter your question and the maximum character limit is 5000 characters." 
            :disabled="isProcessing"
            rows="1"
            ref="textArea"
            maxlength="5000"
          ></textarea>
          <button 
            @click="sendMessage" 
            :disabled="isProcessing || !inputText.trim()"
            class="send-button"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
            </svg>
          </button>
        </div>
        <div class="status-bar">
          <span v-if="isProcessing"></span>
          <span v-else>Press Enter to send</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted, watch } from 'vue';
import { executeTeamStream, processStream } from '@/utils/api';
import TypingEffect from './TypingEffect.vue';

const inputText = ref('');
const isProcessing = ref(false);
const textArea = ref(null);
const historyContainer = ref(null);

// 对话消息
const messages = reactive([
  { 
    role: 'assistant', 
    content: 'Hello! I am an AI assistant who has implemented a hierarchical agent teams. How can I help you?', 
    isStreaming: false,
    isLoading: false
  }
]);

// 发送消息
const sendMessage = async () => {
  if (!inputText.value.trim() || isProcessing.value) return;
  
  // 添加用户消息
  const userMessage = inputText.value.trim();
  const messageList = [userMessage]
  messages.push({
    role: 'user',
    content: userMessage,
    isStreaming: false,
    isLoading: false
  });
  
  // 清空输入框
  inputText.value = '';
  isProcessing.value = true;
  
  messages.push({
    role: 'assistant',
    content: '',
    agents: [],
    isStreaming: true,
    isLoading: true
  });

  // 滚动到底部
  await nextTick();
  scrollToBottom();
  
  try {
    // 获取流式响应
    const stream = await executeTeamStream(messageList);
    
    // 处理流数据
    await processStream(
      stream,
      (currentAgent, nextAgent) => {
        const lastMessage = messages[messages.length - 1];
        const agentStatus = {
          current: currentAgent,
          next: nextAgent
        };
        lastMessage.agents.push(agentStatus);
      },
      (finalContent) => {
        // 处理完成
        console.log("complete>>", finalContent);
        
        isProcessing.value = false;
        const lastMessage = messages[messages.length - 1];
        lastMessage.content = finalContent;
        lastMessage.isLoading = false;
        scrollToBottom();
      }
    );
  } catch (error) {
    const lastMessage = messages[messages.length - 1];
    lastMessage.content = `抱歉，处理您的请求时出错了: ${error.message}`;
    lastMessage.isStreaming = false;
    isProcessing.value = false;
    scrollToBottom();
  }
};

// 打字完成回调
const onTypingComplete = (index) => {
  messages[index].isStreaming = false;
};

// 滚动到底部
const scrollToBottom = () => {
  
  if (historyContainer.value) {
    historyContainer.value.scrollTop = historyContainer.value.scrollHeight;
  }
};

// 自动调整输入框高度
const adjustTextareaHeight = () => {
  if (textArea.value) {
    textArea.value.style.height = 'auto';
    textArea.value.style.height = `${textArea.value.scrollHeight}px`;
  }
};

// 监听输入框变化
watch(inputText, () => {
  adjustTextareaHeight();
});

onMounted(() => {
  adjustTextareaHeight();
});
</script>

<style scoped>
.chat-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Inter', 'Segoe UI', sans-serif;
  color: #333;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-header {
  text-align: center;
  margin-bottom: 20px;
}

.chat-header h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin-bottom: 8px;
  font-weight: 600;
}

.chat-header p {
  color: #6b7280;
  font-size: 0.9rem;
}

.chat-interface {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-history {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
  background-color: #f9fafb;
}

.message {
  display: flex;
  margin-bottom: 24px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.avatar {
  flex: 0 0 50px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  margin-right: 15px;
}

.ai-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-avatar svg {
  width: 20px;
  height: 20px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e5e7eb;
  color: #4b5563;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar svg {
  width: 20px;
  height: 20px;
}

.content {
  flex: 1;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
}

.message.assistant .content {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
}

.message.user .content {
  background: #eff6ff;
  border: 1px solid #dbeafe;
}

.static-text {
  white-space: pre-wrap;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.6);
  }
  40% {
    transform: scale(1);
  }
}

.input-area {
  padding: 15px;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.input-container {
  display: flex;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  overflow: hidden;
  background: white;
}

textarea {
  flex: 1;
  padding: 14px;
  border: none;
  outline: none;
  resize: none;
  font-size: 16px;
  line-height: 1.5;
  max-height: 150px;
  overflow-y: auto;
}

.send-button {
  width: 50px;
  background: #6366f1;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}

.send-button:disabled {
  background: #a5b4fc;
  cursor: not-allowed;
}

.send-button:not(:disabled):hover {
  background: #4f46e5;
}

.send-button svg {
  width: 20px;
  height: 20px;
}

.status-bar {
  padding: 8px 5px 0;
  font-size: 0.8rem;
  color: #6b7280;
  text-align: right;
}

.api-info {
  margin-top: 15px;
  text-align: center;
  font-size: 0.8rem;
  color: #6b7280;
}

/* .indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #6366f1;
  margin-right: 6px;
  animation: bounce 1.4s infinite ease-in-out both;
} */

.path-node {
  display: flex;
  min-width: calc(30% - 10px);
  margin-right: 8px;
  padding: 4px 8px;
  background: #e5e7eb;
  border-radius: 12px;
  font-size: 0.9rem;
  color: #1f2937;
  transition: background 0.3s, transform 0.3s;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
}

.path-fade-enter-active { transition: opacity 0.5s, transform 0.5s; }

.path-fade-enter-from { opacity: 0; transform: translateY(20px); }

.loading-indicator {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  border: 1px solid #ccc;
  padding: 10px;
  align-items: center;
}

/* .loading-indicator span {
  display: block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #6366f1;
  margin-right: 6px;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-indicator span:nth-child(2) {
  animation-delay: -0.16s;
} */

/* .path-node {
  flex: 1;
  min-width: calc(33.33% - 10px);
  height: 50px;
  background-color: lightblue;
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
} */

.loading-indicator:has(.path-node:nth-child(3)):not(:has(.path-node:nth-child(4))) {
  flex-wrap: nowrap;
}
</style>