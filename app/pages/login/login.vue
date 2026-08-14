<template>
  <view class="page" :style="cssVars">
    <view class="logo">💕</view>
    <view class="title">恋爱日记</view>

    <input class="input" v-model="username" placeholder="用户名" />
    <input class="input" v-model="password" type="password" placeholder="密码" />

    <button class="btn" @click="doLogin">登 录</button>
    <view class="switch-row">
      <text class="switch" @click="toRegister">还没有账号？去注册</text>
      <text class="switch link" @click="openPwd">修改密码</text>
    </view>

    <!-- 修改密码弹窗 -->
    <view class="mask" v-if="showPwd" @click="showPwd = false">
      <view class="popup" @click.stop>
        <text class="pop-title">🔒 修改密码</text>
        <input class="pop-input" v-model="pwdForm.username" placeholder="用户名" />
        <input class="pop-input" v-model="pwdForm.oldPwd" type="password" placeholder="旧密码" />
        <input class="pop-input" v-model="pwdForm.newPwd" type="password" placeholder="新密码（至少 6 位）" />
        <input class="pop-input" v-model="pwdForm.confirmPwd" type="password" placeholder="确认新密码" />
        <button class="pop-btn" @click="doChangePwd">确认修改</button>
        <text class="pop-cancel" @click="showPwd = false">取消</text>
      </view>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'
import store from '../../common/store.js'

export default {
  data() {
    return {
      username: '',
      password: '',
      showPwd: false,
      pwdForm: { username: '', oldPwd: '', newPwd: '', confirmPwd: '' },
    }
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
    openPwd() {
      this.pwdForm = { username: this.username, oldPwd: '', newPwd: '', confirmPwd: '' }
      this.showPwd = true
    },
    async doChangePwd() {
      const f = this.pwdForm
      if (!f.username || !f.oldPwd || !f.newPwd) {
        uni.showToast({ title: '请填写完整信息', icon: 'none' })
        return
      }
      if (f.newPwd.length < 6) {
        uni.showToast({ title: '新密码至少 6 位', icon: 'none' })
        return
      }
      if (f.newPwd !== f.confirmPwd) {
        uni.showToast({ title: '两次输入的新密码不一致', icon: 'none' })
        return
      }
      uni.showLoading({ title: '修改中' })
      const { ok, msg } = await api.resetPassword({
        username: f.username,
        old_password: f.oldPwd,
        new_password: f.newPwd,
      })
      uni.hideLoading()
      if (ok) {
        uni.showToast({ title: '密码修改成功', icon: 'success' })
        this.showPwd = false
        this.password = ''
      } else {
        uni.showToast({ title: msg, icon: 'none' })
      }
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
.title { font-size: 36rpx; font-weight: bold; margin-bottom: 60rpx; color: var(--pink); }
.input {
  width: 85%;
  height: 90rpx;
  background: var(--card);
  border-radius: 16rpx;
  padding: 0 30rpx;
  margin-bottom: 24rpx;
  font-size: 30rpx;
}
.btn {
  width: 85%;
  height: 90rpx;
  background: var(--pink);
  color: #fff;
  border-radius: 16rpx;
  font-size: 32rpx;
  text-align: center;
  line-height: 90rpx;
  margin-top: 20rpx;
}
.switch-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40rpx;
  margin-top: 30rpx;
}
.switch { color: var(--muted); font-size: 26rpx; }
.switch.link { color: var(--pink); }

/* ---------- 修改密码弹窗 ---------- */
.mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 999;
}
.popup {
  width: 600rpx;
  background: var(--card);
  border-radius: 24rpx;
  padding: 40rpx 36rpx 32rpx;
  display: flex;
  flex-direction: column;
}
.pop-title { font-size: 32rpx; font-weight: bold; text-align: center; margin-bottom: 28rpx; }
.pop-input {
  width: 100%;
  height: 84rpx;
  background: var(--bg);
  border-radius: 14rpx;
  padding: 0 24rpx;
  margin-bottom: 20rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}
.pop-btn {
  width: 100%;
  height: 84rpx;
  line-height: 84rpx;
  background: var(--pink);
  color: #fff;
  border-radius: 14rpx;
  font-size: 30rpx;
  text-align: center;
  margin-top: 6rpx;
}
.pop-cancel { text-align: center; color: var(--muted); font-size: 26rpx; margin-top: 20rpx; }
</style>
