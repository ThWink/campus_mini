const app = getApp();
const STORAGE_KEY = 'ai_chat_history';

Page({
  data: {
    inputValue: '',
    messageList: [],
    isLoading: false,
    scrollIntoView: '',
    showWelcome: true
  },

  chunkBuffer: '',
  receivedStream: false,

  onLoad() {
    this.loadHistory();
  },

  loadHistory() {
    const history = wx.getStorageSync(STORAGE_KEY);
    if (history && history.length > 0) {
      this.setData({
        messageList: history,
        showWelcome: this.isWelcomeOnly(history),
        scrollIntoView: `msg-${history.length - 1}`
      });
    } else {
      const welcomeMsg = {
        role: 'ai',
        content: '你好！我是智能跑腿助手，有什么可以帮你的吗？比如：\n• 如何发布任务？\n• 如何接单？\n• 评价在哪里？'
      };
      this.setData({
        messageList: [welcomeMsg],
        showWelcome: true
      });
    }
  },

  isWelcomeOnly(list) {
    return list.length === 0 || (
      list.length === 1 &&
      list[0].role === 'ai' &&
      list[0].content.indexOf('你好') !== -1
    );
  },

  saveHistory() {
    const list = this.data.messageList;
    if (list.length > 20) {
      wx.setStorageSync(STORAGE_KEY, list.slice(-20));
    } else {
      wx.setStorageSync(STORAGE_KEY, list);
    }
  },

  clearHistory() {
    wx.removeStorageSync(STORAGE_KEY);
    const welcomeMsg = {
      role: 'ai',
      content: '你好！我是智能跑腿助手，有什么可以帮你的吗？比如：\n• 如何发布任务？\n• 如何接单？\n• 评价在哪里？'
    };
    this.setData({
      messageList: [welcomeMsg],
      showWelcome: true
    });
  },

  onInput(e) {
    this.setData({
      inputValue: e.detail.value
    });
  },

  sendMessage() {
    const content = this.data.inputValue.trim();
    if (!content || this.data.isLoading) return;

    const userId = wx.getStorageSync('userId') || app.globalData.userId;

    const userMsg = { role: 'user', content: content };

    this.setData({
      messageList: this.data.messageList.concat(userMsg),
      inputValue: '',
      showWelcome: false,
      scrollIntoView: `msg-${this.data.messageList.length - 1}`
    });

    const aiMsg = { role: 'ai', content: '' };
    this.setData({
      messageList: this.data.messageList.concat(aiMsg),
      isLoading: true,
      scrollIntoView: `msg-${this.data.messageList.length - 1}`
    });

    this.chunkBuffer = '';
    this.receivedStream = false;

    const task = wx.request({
      url: app.globalData.baseUrl + '/api/ai/ask',
      method: 'POST',
      responseType: 'text',
      enableChunked: true,
      header: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      data: {
        user_id: userId,
        message: content
      },
      success: (res) => {
        if (!this.receivedStream && typeof res.data === 'string') {
          this.handleSseText(res.data);
          this.finishAiResponse();
        }
      },
      fail: (err) => {
        console.error('请求失败', err);
        this.appendAiContent('网络异常，请稍后再试。');
        this.finishAiResponse();
      },
      complete: () => {
        if (this.data.isLoading) {
          this.flushChunkBuffer();
          this.finishAiResponse();
        }
      }
    });

    task.onChunkReceived((res) => {
      try {
        this.receivedStream = true;
        this.handleSseText(this.arrayBufferToText(res.data));
      } catch (err) {
        console.error('AI分块解析失败', err);
      }
    });
  },

  arrayBufferToText(buffer) {
    if (typeof TextDecoder !== 'undefined') {
      return new TextDecoder('utf-8').decode(buffer);
    }

    const bytes = new Uint8Array(buffer);
    let binary = '';
    const chunkSize = 8192;
    for (let i = 0; i < bytes.length; i += chunkSize) {
      binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunkSize));
    }
    return decodeURIComponent(escape(binary));
  },

  handleSseText(text) {
    this.chunkBuffer += text;
    const parts = this.chunkBuffer.split(/\r?\n/);
    this.chunkBuffer = parts.pop() || '';

    parts.forEach(line => this.handleSseLine(line));
  },

  flushChunkBuffer() {
    if (!this.chunkBuffer) return;
    this.handleSseLine(this.chunkBuffer);
    this.chunkBuffer = '';
  },

  handleSseLine(line) {
    if (!line || !line.startsWith('data:')) return;

    const data = line.substring(5).trim();
    if (!data) return;
    if (data === '[DONE]') {
      this.finishAiResponse();
      return;
    }
    this.appendAiContent(data);
  },

  appendAiContent(content) {
    const list = this.data.messageList;
    const idx = list.length - 1;

    if (idx >= 0 && list[idx].role === 'ai') {
      list[idx].content += content;
      this.setData({
        messageList: list,
        scrollIntoView: `msg-${idx}`
      });
    }
  },

  finishAiResponse() {
    const list = this.data.messageList;
    const idx = list.length - 1;
    if (idx >= 0 && list[idx].role === 'ai' && !list[idx].content) {
      list[idx].content = '暂时没有收到 AI 回复，请稍后再试。';
      this.setData({ messageList: list });
    }
    this.setData({ isLoading: false });
    this.saveHistory();
  }
});
