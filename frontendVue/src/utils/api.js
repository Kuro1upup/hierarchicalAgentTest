/**
 * 调用流式API并返回可读流
 * @param {string} messages - 消息列表
 * @returns {Promise<ReadableStream>} - 可读流
 */
export const executeTeamStream = async (messages) => {
  try {
    const response = await fetch(`http://localhost:8000/agentTask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 如果需要认证，添加认证头
        // 'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        messages: messages,
        max_depth: 150, // 最大递归次数
        stream: true, // 是否启用流式响应
      })
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error('响应体不可读');
    }

    return response.body;
  } catch (error) {
    console.error('API调用错误:', error);
    throw error;
  }
};

/**
 * 处理流式响应
 * @param {ReadableStream} stream - 可读流
 * @param {function} onData - 数据回调
 * @param {function} onComplete - 完成回调
 */
export const processStream = async (stream, onData, onComplete) => {
  const reader = stream.getReader();
  const decoder = new TextDecoder('utf-8');
  let result = '';
  
  try {
    while (true) {
      const { value, done } = await reader.read();
      
      if (done) {

        onComplete(result);
        return;
      }
      
      // 处理数据块
      const textChunk = decoder.decode(value, { stream: true });
      // 这里可以根据需要处理文本块，例如去除多余的空格或换行
      const jsonChunk = JSON.parse(textChunk);
      if (jsonChunk.currentAgent !== 'supervisor') {
        result += "The response of " + jsonChunk.currentAgent + " is: " + jsonChunk.messages + "\n";
      } else {
        result += "Routing to the next agent: " + jsonChunk.nextAgent + "\n";
      }
      onData(jsonChunk.currentAgent, jsonChunk.nextAgent);
    }
  } catch (error) {
    console.error('流处理错误:', error);
    onComplete(result, error);
  } finally {
    reader.releaseLock();
  }
};