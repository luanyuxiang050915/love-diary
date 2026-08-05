<template>
  <view class="page">
    <view class="logo">💕</view>
    <view class="title">恋爱日记</view>

    <input class="input" v-model="username" placeholder="用户名" />
    <input class="input" v-model="password" type="password" placeholder="密码" />

    <button class="btn" @click="doLogin">登 录</button>
    <view class="switch" @click="toRegister">还没有账号？去注册</view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import store from '../../common/store.js'

export default {
  data() {
    return { username: '', password: '' }
  },
  methods: {
    async doLogin() {
      if (!this.username || !this.password) {
        uni.showToast({ title: '请填写用户名和密码', icon: 'none' })
        return
      }
      uni.showLoading({ title: '登录中' })
      const { ok, data, msg } = await api.login({ username: this.username, password: this.password })
      uni.hideLoading()
      if (!ok) { uni.showToast({ title: msg, icon: 'none' }); return }
      store.login(data.token, data.user)
      uni.reLaunch({ url: '/pages/diary/list' })
    },
    toRegister() {
      uni.navigateTo({ url: '/pages/register/register' })
    },
  },
}
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 120rpx;
}
.logo { font-size: 80rpx; margin-bottom: 20rpx; }
.title { font-size: 36rpx; font-weight: bold; margin-bottom: 60rpx; color: #f8a5c2; }
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
.switch { margin-top: 30rpx; color: #999; font-size: 26rpx; }
</style>
