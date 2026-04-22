const app = getApp();

Page({
  data: {
    orderId: null,
    taskId: null,
    orderTitle: '',
    rating: 5,
    content: '',
    tags: '',
    submitted: false,
    existingComment: null,
    isSubmitting: false
  },

  onLoad(options) {
    const title = options.title ? decodeURIComponent(options.title) : '订单评价';
    this.setData({
      orderId: Number(options.orderId),
      taskId: Number(options.taskId),
      orderTitle: title
    });
    this.loadExistingComment();
  },

  loadExistingComment() {
    const reviewerId = wx.getStorageSync('userId') || app.globalData.userId;
    if (!this.data.orderId || !reviewerId) return;

    wx.request({
      url: app.globalData.baseUrl + `/comment/order/${this.data.orderId}`,
      method: 'GET',
      success: (res) => {
        if (res.data.code === 200) {
          const existing = (res.data.data || []).find(item => Number(item.reviewerId) === Number(reviewerId));
          if (existing) {
            this.setData({
              existingComment: existing,
              submitted: true,
              rating: existing.score,
              content: existing.content || '',
              tags: existing.tags || ''
            });
          }
        }
      }
    });
  },

  onStarTap(e) {
    if (this.data.submitted) return;
    this.setData({ rating: Number(e.currentTarget.dataset.rating) });
  },

  onContentInput(e) {
    this.setData({ content: e.detail.value });
  },

  onTagsInput(e) {
    this.setData({ tags: e.detail.value });
  },

  submitEvaluate() {
    const { orderId, taskId, rating, content, tags, submitted, isSubmitting } = this.data;
    const reviewerId = wx.getStorageSync('userId') || app.globalData.userId;

    if (submitted || isSubmitting) return;
    if (!reviewerId) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }
    if (!content.trim()) {
      wx.showToast({ title: '请输入评价内容', icon: 'none' });
      return;
    }

    this.setData({ isSubmitting: true });
    wx.request({
      url: app.globalData.baseUrl + '/comment/add',
      method: 'POST',
      data: {
        orderId,
        taskId,
        reviewerId,
        score: rating,
        content: content.trim(),
        tags: tags.trim()
      },
      success: (res) => {
        if (res.data.code === 200) {
          this.setData({
            submitted: true,
            existingComment: res.data.data || null
          });
          wx.showToast({ title: '评价成功', icon: 'success' });
          setTimeout(() => {
            wx.navigateBack();
          }, 1200);
        } else {
          wx.showToast({ title: res.data.msg || '评价失败', icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络异常，请重试', icon: 'none' });
      },
      complete: () => {
        this.setData({ isSubmitting: false });
      }
    });
  }
});
