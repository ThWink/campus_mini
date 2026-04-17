const app = getApp();

Page({
  data: {
    title: '',
    description: '',
    reward: ''
  },

  inputTitle(e) { this.setData({ title: e.detail.value }); },
  inputDesc(e) { this.setData({ description: e.detail.value }); },
  inputReward(e) { this.setData({ reward: e.detail.value }); },

  submitTask() {
    const { title, description, reward } = this.data;
    const userId = wx.getStorageSync('userId'); 

    if (!userId) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }

    if (!title || !reward) {
      wx.showToast({ title: '标题和金额不能为空', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '发布中...' });

    wx.request({
      url: app.globalData.baseUrl + '/task/save', 
      method: 'POST',
      data: {
        // 🔴 必须叫 publisherId，与你的 Java Task 实体类保持一致
        publisherId: userId, 
        title: title,
        description: description,
        reward: parseFloat(reward)
      },
      success: (res) => {
        if (res.data.code === 200) {
          wx.showToast({ title: '发布成功', icon: 'success' });
          this.setData({ title: '', description: '', reward: '' });
          setTimeout(() => {
            wx.switchTab({ url: '/pages/hall/hall' });
          }, 1500);
        } else {
          wx.showToast({ title: res.data.msg || '服务器报错', icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络异常', icon: 'none' });
      },
      complete: () => { wx.hideLoading(); }
    });
  }
})