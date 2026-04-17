const app = getApp();

Page({
  data: {
    orderList: [],
    isLoading: false
  },

  onShow() { this.fetchOrderList(); },

  fetchOrderList() {
    this.setData({ isLoading: true });
    wx.request({
      url: app.globalData.baseUrl + '/order/listPending',
      method: 'GET',
      success: (res) => {
        if (res.data.code === 200) {
          this.setData({ orderList: res.data.data });
        }
      },
      complete: () => {
        this.setData({ isLoading: false });
      }
    });
  },

  handleAcceptOrder(e) {
    const orderId = e.currentTarget.dataset.id;
    const order = e.currentTarget.dataset.item; 
    const myId = wx.getStorageSync('userId');

    if (order && order.publisherId == myId) {
      wx.showModal({
        title: '提示',
        content: '你不能抢自己发布的订单。',
        showCancel: false
      });
      return;
    }

    wx.showModal({
      title: '确认接单',
      content: '确定要领取这个任务吗？',
      success: (res) => {
        if (res.confirm) {
          wx.request({
            url: app.globalData.baseUrl + '/order/accept',
            method: 'POST',
            data: { orderId: orderId, runnerId: myId },
            success: (res) => {
              if (res.data.code === 200) {
                wx.showToast({ title: '接单成功' });
                this.fetchOrderList();
              } else {
                wx.showToast({ title: res.data.msg || '接单失败', icon: 'none' });
              }
            }
          })
        }
      }
    });
  },

  navToChat() {
    wx.navigateTo({
      url: '/pages/ai-chat/ai-chat'
    });
  }
})