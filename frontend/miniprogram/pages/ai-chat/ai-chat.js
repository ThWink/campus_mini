const app = getApp();
const STORAGE_KEY = 'ai_chat_history';

Page({
  data: {
    inputValue: '',
    messageList: [],
    isLoading: false,
    scrollIntoView: ''
  },

  onLoad() {
    this.loadHistory();
  },

  loadHistory() {
    const history = wx.getStorageSync(STORAGE_KEY);
    if (history && history.length > 0) {
      this.setData({
        messageList: history,
        scrollIntoView: `msg-${history.length - 1}`
      });
    } else {
      const welcomeMsg = {
        role: 'ai',
        content: '你好！我是智能跑腿助手，有什么可以帮你的吗？比如：\n• 如何发布任务？\n• 如何接单？\n• 评价在哪里？'
      };
      this.setData({
        messageList: [welcomeMsg]
      });
    }
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
      messageList: [welcomeMsg]
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
      messageList: [...this.data.messageList, userMsg],
      inputValue: '',
      scrollIntoView: `msg-${this.data.messageList.length - 1}`
    });

    const aiMsg = { role: 'ai', content: '' };
    this.setData({
      messageList: [...this.data.messageList, aiMsg],
      isLoading: true,
      scrollIntoView: `msg-${this.data.messageList.length - 1}`
    });

    const that = this;
    const task = wx.request({
      url: 'http://localhost:8080/api/ai/ask',
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
      fail: (err) => {
        console.error('请求失败', err);
        that.setData({ isLoading: false });
      }
    });

    task.onChunkReceived((res) => {
      const arrayBuffer = res.data;
      const text = new TextDecoder().decode(arrayBuffer);
      
      const lines = text.split('\n');
      lines.forEach(line => {
        if (line.startsWith('data:')) {
          const data = line.substring(5).trim();
          if (data === '[DONE]' || data === '') {
            that.setData({ isLoading: false });
            that.saveHistory();
          } else {
            const list = that.data.messageList;
            const idx = list.length - 1;
            
            if (idx >= 0 && list[idx].role === 'ai') {
              list[idx].content += data;
              that.setData({ messageList: list });
            }
          }
        }
      });
    });
  }
});
