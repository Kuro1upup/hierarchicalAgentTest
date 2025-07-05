<template>
  <div class="typing-effect">
    <span class="text-content">{{ displayText }}</span>
    <span class="cursor" :class="{ blinking: isTyping }"></span>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({
  text: {
    type: String,
    default: ''
  },
  isTypeing: {
    type: Boolean,
    default: false // 是否正在打字
  },
  speed: {
    type: Number,
    default: 30 // 毫秒/字符
  }
});

const emit = defineEmits(['complete']);

const displayText = ref('');
const isTyping = ref(false);
let typingInterval = null;

// 开始打字效果
const startTyping = () => {
  if (typingInterval) clearInterval(typingInterval);
  
  displayText.value = '';
  isTyping.value = true;
  let index = 0;
  
  typingInterval = setInterval(() => {
    if (props.isTypeing || index < props.text.length) {
      displayText.value += props.text.charAt(index);
      index++;
    } else {
      clearInterval(typingInterval);
      isTyping.value = false;
      emit('complete');
    }
  }, props.speed);
};

// 当传入的文本变化时重新开始打字效果
watch(() => props.text, (newText) => {
  if (newText) {
    startTyping();
  }
});

// 组件挂载时如果有初始文本，开始打字
onMounted(() => {
  if (props.text) {
    startTyping();
  }
});
</script>

<style scoped>
.typing-effect {
  display: inline-block;
  position: relative;
}

.text-content {
  white-space: pre-wrap;
  word-break: break-word;
}

.cursor {
  display: inline-block;
  width: 8px;
  height: 1.2em;
  background-color: #3b82f6;
  margin-left: 3px;
  vertical-align: middle;
}

.blinking {
  animation: blink 1s infinite;
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0; }
  100% { opacity: 1; }
}
</style>