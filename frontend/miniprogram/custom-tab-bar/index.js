Component({
  data: {
    selected: 0,
    list: [
      {
        pagePath: "/pages/hall/hall",
        text: "大厅",
        icon: "跑"
      },
      {
        pagePath: "/pages/publish/publish",
        text: "发布",
        icon: "发"
      },
      {
        pagePath: "/pages/ai-chat/ai-chat",
        text: "AI",
        icon: "AI",
        center: true
      },
      {
        pagePath: "/pages/orderList/orderList",
        text: "订单",
        icon: "单"
      },
      {
        pagePath: "/pages/user/user",
        text: "我的",
        icon: "我"
      }
    ]
  },

  lifetimes: {
    attached() {
      this.updateSelected();
    }
  },

  pageLifetimes: {
    show() {
      this.updateSelected();
    }
  },

  methods: {
    updateSelected() {
      const pages = getCurrentPages();
      const current = pages[pages.length - 1];
      if (!current) return;

      const route = `/${current.route}`;
      const selected = this.data.list.findIndex(item => item.pagePath === route);
      if (selected !== -1 && selected !== this.data.selected) {
        this.setData({ selected });
      }
    },

    switchTab(event) {
      const index = Number(event.currentTarget.dataset.index);
      const item = this.data.list[index];
      if (!item || index === this.data.selected) return;

      wx.switchTab({
        url: item.pagePath
      });
    }
  }
});
