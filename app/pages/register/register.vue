<template>
  <view class="page">
    <view class="logo">💕</view>
    <view class="title">注册新账号</view>

    <input class="input" v-model="username" placeholder="用户名（至少2个字符）" />
    <input class="input" v-model="password" type="password" placeholder="密码（至少6位）" />
    <input class="input" v-model="nickname" placeholder="昵称（可不填，默认为用户名）" />

    <button class="btn" @click="doRegister">注 册</button>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import store from '../../common/store.js'

export default {
  data() {
    return { username: '', password: '', nickname: '' }
  },
  methods: {
    async doRegister() {
      if (!this.username || !this.password) {
        uni.showToast({ title: '用户名和密码不能为空', icon: 'none' })
        return
      }
      uni.showLoading({ title: '注册中' })
      const { ok, msg } = await api.register({
        username: this.username,
        password: this.password,
        nickname: this.nickname,
      })
      if (!ok) { uni.hideLoading(); uni.showToast({ title: msg, icon: 'none' }); return }

      // 注册成功后自动登录拿 token
      const r = await api.login({ username: this.username, password: this.password })
      uni.hideLoading()
      if (!r.ok) { uni.showToast({ title: r.msg, icon: 'none' }); return }
      store.login(r.data.token, r.data.user)
      uni.reLaunch({ url: '/pages/diary/list' })
    },
  },
}
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 100rpx;
}
.logo { font-size: 80rpx; margin-bottom: 20rpx; }
.title { font-size: 34rpx; font-weight: bold; margin-bottom: 60rpx; color: #f8a5c2; }
.input {
  width: 85%;
  height: 90rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 0 30rpx;
  margin-bottom: 24rpx;
  font-size: 30rpx;
}
.btn {
  width: 85%;
  height: 90rpx;
  background: #f8a5c2;
  color: #fff;
  border-radius: 16rpx;
  font-size: 32rpx;
  text-align: center;
  line-height: 90rpx;
  margin-top: 20rpx;
}
</style>
