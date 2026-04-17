Page({
  data: { userInfo: null },

  onShow() {
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo) {
      this.setData({ userInfo });
    } else {
      wx.reLaunch({ url: '/pages/login/login' });
    }
  },

  // 退出登录
  handleLogout() {
    wx.showModal({
      title: '提示',
      content: '确定退出账号吗？',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorageSync(); 
          wx.showToast({ title: '退出成功', icon: 'success' }); // 确保提示语正确
          setTimeout(() => {
            wx.reLaunch({ url: '/pages/login/login' });
          }, 800);
        }
      }
    });
  },

  // 跳转逻辑
  navToList(e) {
    const type = e.currentTarget.dataset.type;
    wx.navigateTo({
      url: `/pages/orderList/orderList?type=${type}`
    });
  },

  navToChat() {
    wx.navigateTo({
      url: '/pages/ai-chat/ai-chat'
    });
  }
});