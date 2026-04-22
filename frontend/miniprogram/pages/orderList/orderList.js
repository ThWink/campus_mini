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
    const params = isPublished ? { userId } : { runnerId: userId };

    wx.request({
      url: app.globalData.baseUrl + url,
      data: params,
      method: 'GET',
      success: (res) => {
        if (res.data.code === 200) {
          const orders = (res.data.data || []).map(item => Object.assign({}, item, {
            evaluatedByMe: false
          }));
          this.setData({ orders });
          this.loadEvaluationStatus(orders, userId);
        }
      }
    });
  },

  loadEvaluationStatus(orders, userId) {
    if (!userId || !orders || orders.length === 0) return;
    orders.forEach((order) => {
      if (Number(order.status) !== 2) return;
      wx.request({
        url: app.globalData.baseUrl + `/comment/order/${order.id}`,
        method: 'GET',
        success: (res) => {
          if (res.data.code === 200) {
            const evaluated = (res.data.data || []).some(item => Number(item.reviewerId) === Number(userId));
            if (evaluated) {
              const next = this.data.orders.map(item => {
                if (Number(item.id) === Number(order.id)) {
                  return Object.assign({}, item, { evaluatedByMe: true });
                }
                return item;
              });
              this.setData({ orders: next });
            }
          }
        }
      });
    });
  },

  handleComplete(e) {
    const orderId = e.currentTarget.dataset.id;
    wx.request({
      url: app.globalData.baseUrl + '/order/complete',
      method: 'POST',
      data: { orderId },
      success: (res) => {
        if (res.data.code === 200) {
          wx.showToast({ title: '操作成功', icon: 'success' });
          this.loadOrders();
        } else {
          wx.showToast({ title: res.data.msg || '操作失败', icon: 'none' });
        }
      }
    });
  },

  goToEvaluate(e) {
    const orderId = e.currentTarget.dataset.id;
    const taskId = e.currentTarget.dataset.taskid;
    const title = e.currentTarget.dataset.title || '订单评价';
    wx.navigateTo({
      url: `/pages/evaluate/evaluate?orderId=${orderId}&taskId=${taskId}&title=${encodeURIComponent(title)}`
    });
  }
});
