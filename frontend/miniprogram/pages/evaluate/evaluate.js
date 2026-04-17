const app = getApp();

Page({
  data: {
    orderId: null,
    taskId: null,
    orderTitle: '',
    rating: 5,
    content: '',
    submitted: false
  },

  onLoad(options) {
    this.setData({
      orderId: options.orderId,
      taskId: options.taskId,
      orderTitle: decodeURIComponent(options.title) || '订单评价'
    });
  },

  onStarTap(e) {
    const rating = e.currentTarget.dataset.rating;
    this.setData({ rating });
  },

  onContentInput(e) {
    this.setData({ content: e.detail.value });
  },

  submitEvaluate() {
    const { taskId, rating, content } = this.data;
    
    if (!content.trim()) {
      wx.showToast({ title: '请输入评价内容', icon: 'none' });
      return;
    }

    wx.request({
      url: app.globalData.baseUrl + '/comment/add',
      method: 'POST',
      data: {
        taskId: taskId,
        score: rating,
        content: content
      },
      success: (res) => {
        if (res.data.code === 200) {
          this.setData({ submitted: true });
          wx.showToast({ title: '评价成功', icon: 'success' });
          setTimeout(() => {
            wx.navigateBack();
          }, 1500);
        } else {
          wx.showToast({ title: res.data.msg || '评价失败', icon: 'none' });
        }
      }
    });
  }
});
