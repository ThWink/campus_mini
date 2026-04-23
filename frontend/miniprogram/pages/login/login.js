const app = getApp();

Page({
  data: {
    username: '',
    password: ''
  },

  onUsernameInput(e) {
    this.setData({ username: e.detail.value });
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  // 登录处理
  handleLogin() {
    const { username, password } = this.data;

    // 1. 表单校验
    if (!username || !password) {
      wx.showToast({ title: '请填写完整信息', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '正在登录...' });

    // 2. 调用后端接口
    wx.request({
      url: app.globalData.baseUrl + '/user/login', // 确保 app.js 里定义了 baseUrl
      method: 'POST',
      data: {
        username: username,
        password: password
      },
      // 因为后端用了 @RequestBody，默认 header 为 application/json 即可
      success: (res) => {
        wx.hideLoading();
        if (res.data.code === 200) {
          const loginUser = res.data.data;
          
          // 3. 存储登录状态（关键：后续发单/接单全靠它）
          wx.setStorageSync('userId', loginUser.id);
          wx.setStorageSync('userInfo', loginUser);
          
          wx.showToast({ title: '登录成功', icon: 'success' });

          // 4. 延迟跳转到 TabBar 首页（大厅）
          setTimeout(() => {
            wx.switchTab({
              url: '/pages/hall/hall'
            });
          }, 1000);
        } else {
          wx.showModal({
            title: '登录失败',
            content: res.data.msg || '用户名或密码错误',
            showCancel: false
          });
        }
      },
      fail: () => {
        wx.hideLoading();
        wx.showToast({ title: '服务器连接失败', icon: 'none' });
      }
    });
  },

  // 跳转注册页
  goToRegister() {
    wx.navigateTo({
      url: '/pages/register/register'
    });
  }
});
