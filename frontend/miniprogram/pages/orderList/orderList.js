const app = getApp();

Page({
  data: {
    type: '', 
    orders: []
  },

  onLoad(options) {
    this.setData({ type: options.type });
    this.loadOrders();
  },

  onShow() {
    this.loadOrders();
  },

  loadOrders() {
    const userId = wx.getStorageSync('userId');
    const isPublished = this.data.type === 'published';
    const url = isPublished ? '/order/myPublished' : '/order/myTasks';
    const params = isPublished ? { userId: userId } : { runnerId: userId };

    wx.request({
      url: app.globalData.baseUrl + url,
      data: params,
      method: 'GET',
      success: (res) => {
        if (res.data.code === 200) {
          this.setData({ orders: res.data.data });
        }
      }
    });
  },

  handleComplete(e) {
    const orderId = e.currentTarget.dataset.id;
    wx.request({
      url: app.globalData.baseUrl + '/order/complete',
      method: 'POST',
      data: { orderId: orderId },
      success: (res) => {
        if (res.data.code === 200) {
          wx.showToast({ title: '操作成功', icon: 'success' });
          this.loadOrders();
        }
      }
    });
  },

  goToEvaluate(e) {
    const orderId = e.currentTarget.dataset.id;
    const taskId = e.currentTarget.dataset.taskid;
    const title = e.currentTarget.dataset.title;
    wx.navigateTo({
      url: `/pages/evaluate/evaluate?orderId=${orderId}&taskId=${taskId}&title=${encodeURIComponent(title)}`
    });
  }
});