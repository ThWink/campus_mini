const app = getApp();

Page({
  data: {
    username: '',
    phone: '',
    password: '',
    confirmPassword: ''
  },

  handleRegister() {
    const { username, phone, password, confirmPassword } = this.data;

    // 1. 基础校验
    if (!username || !phone || !password) {
      return wx.showToast({ title: '请填写完整信息', icon: 'none' });
    }
    if (password !== confirmPassword) {
      return wx.showToast({ title: '两次密码不一致', icon: 'none' });
    }
    if (phone.length !== 11) {
      return wx.showToast({ title: '手机号格式错误', icon: 'none' });
    }

    wx.showLoading({ title: '正在注册...' });

    // 2. 发起请求
    wx.request({
      url: app.globalData.baseUrl + '/user/register',
      method: 'POST',
      data: {
        username: username,
        password: password,
        phone: phone,
        role: 'USER' // 默认注册为普通用户
      },
      success: (res) => {
        wx.hideLoading();
        if (res.data.code === 200) {
          wx.showModal({
            title: '注册成功',
            content: '现在去登录吧',
            showCancel: false,
            success: () => {
              wx.navigateTo({ url: '/pages/login/login' });
            }
          });
        } else {
          wx.showModal({ title: '注册失败', content: res.data.msg, showCancel: false });
        }
      }
    });
  },

  goToLogin() {
    wx.navigateBack();
  }
});