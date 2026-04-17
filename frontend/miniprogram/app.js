// app.js
App({
  /**
   * 当小程序初始化完成时，会触发 onLaunch（全局只触发一次）
   */
  onLaunch() {
    // 1. 展示本地存储能力 (保留默认日志逻辑)
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    // 2. 自动登录校验逻辑
    // 如果用户已经登录过，userId 会存在缓存中
    const userId = wx.getStorageSync('userId');
    const userInfo = wx.getStorageSync('userInfo');

    if (userId && userInfo) {
      // 如果已登录，把信息同步到全局变量，方便各页面直接调用
      this.globalData.userId = userId;
      this.globalData.userInfo = userInfo;
      console.log('检测到已登录用户ID:', userId);
      
      // 注意：由于 app.json 首页是 login，
      // 我们在登录页的 onLoad 里会判断并自动跳转到大厅。
    } else {
      console.log('当前处于未登录状态');
    }

    // 3. 获取系统信息 (可选，用于做适配)
    const systemInfo = wx.getSystemInfoSync();
    this.globalData.systemInfo = systemInfo;
  },

  /**
   * 全局变量存储
   */
  globalData: {
    userInfo: null,
    userId: null,
    
    // 🔴 核心配置：指向你的 Spring Boot 后端地址
    // 提醒：在微信开发者工具“本地设置”中勾选“不校验合法域名”
    baseUrl: 'http://localhost:8080',
    
    // 如果你用手机预览，请把 localhost 换成你电脑的局域网 IP
    // 例如: baseUrl: 'http://www.oscloud.xyz:8899'
  }
})