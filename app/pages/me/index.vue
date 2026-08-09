<template>
  <view class="page">
    <!-- 头像和昵称 -->
    <view class="header">
      <image class="avatar" :src="avatarUrl || '/static/default-avatar.png'" mode="aspectFill" @click="changeAvatar" />
      <view class="name-row">
        <text class="nickname" @click="changeNickname">{{ user.nickname || '未设置' }}</text>
        <text class="edit-hint">点击修改</text>
      </view>
    </view>

    <!-- 绑定码 -->
    <view class="section">
      <view class="section-title">情侣绑定</view>
      <block v-if="!user.partner_id">
        <view class="row">
          <view><text class="label">我的绑定码</text><text class="value selectable">{{ user.bind_code || '无' }}</text></view>
          <button class="small-btn" size="mini" @click="copyCode">复制</button>
        </view>
        <view class="row">
          <input class="bind-input" v-model="bindCode" placeholder="输入对方的绑定码" />
          <button class="small-btn" size="mini" @click="doBind">绑定</button>
        </view>
      </block>
      <block v-else>
        <view class="row">
          <text class="label">已与另一半绑定 ❤️</text>
        </view>
      </block>
    </view>

    <!-- 操作 -->
    <view class="section">
      <view class="section-title">账号</view>
      <view class="action" @click="changePwd">修改密码</view>
      <view class="action" @click="showLogs">登录记录</view>
      <view class="action danger" @click="doLogout">退出登录</view>
    </view>

    <!-- 互动 -->
    <view class="section">
      <view class="section-title">互动</view>
      <view class="action" @click="go('/pages/poke/index')">
        <text>💓 戳一戳</text>
        <text class="badge" v-if="pokeUnread > 0">{{ pokeUnread }}</text>
      </view>
      <view class="action" @click="go('/pages/wish/list')">✨ 心愿清单</view>
      <view class="action" @click="go('/pages/checkin/index')">🔥 爱的打卡</view>
      <view class="action" @click="go('/pages/whisper/list')">💬 悄悄话</view>
      <view class="action" @click="go('/pages/stats/mood')">📊 心情月报</view>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import store from '../../common/store.js'

export default {
  data() {
    return {
      user: {},
      bindCode: '',
      pokeUnread: 0,
    }
  },
  computed: {
    avatarUrl() {
      if (this.user.avatar) {
        if (this.user.avatar.startsWith('http')) return this.user.avatar
        return 'http://47.93.241.64:8000' + this.user.avatar
      }
      return ''
    },
  },
  onShow() { this.loadMe(); this.loadPokeUnread() },

  methods: {
    async loadMe() {
      const { ok, data } = await api.getMe()
      if (ok) { this.user = data; store.updateUser(data) }
    },

    async loadPokeUnread() {
      const { ok, data } = await api.getPokeUnread()
      if (ok) this.pokeUnread = data.unread
    },

    go(url) { uni.navigateTo({ url }) },

    changeNickname() {
      uni.showModal({ title: '修改昵称', editable: true, placeholderText: this.user.nickname || '', success: async (res) => {
        if (!res.confirm) return
        const nickname = res.content
        if (!nickname) return
        await api.updateMe({ nickname })
        this.loadMe()
      }})
    },

    changeAvatar() {
      uni.chooseImage({ count: 1, sizeType: ['compressed'], success: async (res) => {
        uni.showLoading({ title: '上传中' })
        const r = await api.uploadImage(res.tempFilePaths[0])
        uni.hideLoading()
        if (r.ok) {
          await api.updateMe({ avatar: r.url })
          this.loadMe()
        } else {
          uni.showToast({ title: r.msg, icon: 'none' })
        }
      }})
    },

    copyCode() {
      uni.setClipboardData({ data: this.user.bind_code, success: () => uni.showToast({ title: '已复制' }) })
    },

    async doBind() {
      if (!this.bindCode.trim()) return uni.showToast({ title: '请输入对方的绑定码', icon: 'none' })
      const { ok, msg } = await api.acceptBind(this.bindCode.trim().toUpperCase())
      if (ok) { uni.showToast({ title: msg, icon: 'success' }); this.bindCode = ''; this.loadMe() }
      else { uni.showToast({ title: msg, icon: 'none' }) }
    },

    changePwd() {
      uni.showModal({ title: '修改密码', editable: true, placeholderText: '输入新密码（至少6位）', success: async (res) => {
        if (!res.confirm || !res.content) return
        const newPassword = res.content
        uni.showModal({ title: '确认旧密码', editable: true, placeholderText: '输入旧密码', success: async (res2) => {
          if (!res2.confirm) return
          const { ok, msg } = await api.changePassword({ old_password: res2.content, new_password: newPassword })
          uni.showToast({ title: ok ? '密码修改成功' : msg, icon: ok ? 'success' : 'none' })
        }})
      }})
    },

    async showLogs() {
      const { ok, data } = await api.getLoginLogs()
      if (!ok || !data.length) { uni.showModal({ title: '登录记录', content: '暂无记录' }); return }
      const lines = data.slice(0, 10).map(log =>
        `${log.created_at.slice(0, 16)}\n${log.ip}  ${log.user_agent.slice(0, 60)}`
      ).join('\n\n')
      uni.showModal({ title: '最近登录', content: lines, showCancel: false, confirmText: '关闭' })
    },

    doLogout() {
      uni.showModal({ title: '退出登录', content: '确定要退出吗？', success: (res) => {
        if (res.confirm) { store.logout(); uni.reLaunch({ url: '/pages/login/login' }) }
      }})
    },
  },
}
</script>

<style scoped>
.page { padding-bottom: 60rpx; }
.header {
  display: flex; align-items: center;
  background: #fff; border-radius: 16rpx;
  padding: 40rpx 30rpx; margin: 20rpx 30rpx;
}
.avatar { width: 110rpx; height: 110rpx; border-radius: 50%; background: #f0f0f0; }
.name-row { margin-left: 24rpx; display: flex; flex-direction: column; }
.nickname { font-size: 34rpx; font-weight: bold; }
.edit-hint { font-size: 22rpx; color: #999; margin-top: 4rpx; }
.section {
  background: #fff; border-radius: 16rpx;
  padding: 24rpx 30rpx; margin: 0 30rpx 24rpx;
}
.section-title { font-size: 24rpx; color: #999; margin-bottom: 16rpx; }
.row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16rpx; }
.label { font-size: 28rpx; color: #333; }
.value { font-size: 28rpx; color: #f8a5c2; }
.selectable { user-select: all; }
.bind-input { flex: 1; height: 64rpx; background: #f5f5f5; border-radius: 8rpx; padding: 0 16rpx; font-size: 26rpx; margin-right: 16rpx; }
.small-btn { background: #f8a5c2; color: #fff; border-radius: 8rpx; }
.action { padding: 20rpx 0; font-size: 28rpx; color: #333; border-bottom: 1rpx solid #f0f0f0; display: flex; align-items: center; justify-content: space-between; }
.action:last-child { border-bottom: none; }
.badge {
  min-width: 36rpx; height: 36rpx; border-radius: 18rpx; text-align: center; line-height: 36rpx;
  background: #ff6b9d; color: #fff; font-size: 22rpx; padding: 0 10rpx;
}
.danger { color: #e74c3c; }
</style>
