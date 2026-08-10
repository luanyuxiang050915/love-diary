<template>
  <view class="page">
    <view class="hero-card">
      <view class="heart-btn" :class="{ active: poking }" @click="doPoke">
        <text class="heart">💓</text>
      </view>
      <text class="hero-title">戳一戳 TA</text>
      <text class="hero-sub">{{ poking ? '已发送！等 TA 来回应你' : '点一下，让 TA 知道你在想 TA' }}</text>
      <button class="btn" @click="doPoke">{{ poking ? '再戳一下' : '戳一戳' }}</button>
    </view>

    <view class="section">
      <view class="section-head">
        <text class="section-title">收到的戳一戳</text>
        <text class="link" v-if="unread > 0" @click="markRead">全部已读</text>
      </view>
      <block v-if="pokes.length > 0">
        <view class="poke-item" v-for="p in pokes" :key="p.id" :class="{ unread: !p.is_read }">
          <text class="poke-icon">{{ p.is_read ? '💗' : '💓' }}</text>
          <view class="poke-main">
            <text class="poke-name">{{ p.from_nickname }}</text>
            <text class="poke-time">{{ fmtTime(p.created_at) }}</text>
          </view>
          <text class="poke-state" :class="{ unread: !p.is_read }">{{ p.is_read ? '已读' : '未读' }}</text>
        </view>
      </block>
      <view class="empty" v-else>还没有收到戳一戳</view>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'

export default {
  data() {
    return { pokes: [], unread: 0, poking: false }
  },
  onShow() { applyTheme(); this.load() },
  methods: {
    async load() {
      const [r1, r2] = await Promise.all([api.getPokes(), api.getPokeUnread()])
      if (r1.ok) this.pokes = r1.data
      if (r2.ok) this.unread = r2.data.unread
    },
    async doPoke() {
      const { ok, msg } = await api.sendPoke()
      if (ok) {
        this.poking = true
        uni.showToast({ title: '已戳了 TA 一下 💓', icon: 'none' })
        setTimeout(() => { this.poking = false }, 1500)
      } else {
        uni.showToast({ title: msg, icon: 'none' })
      }
    },
    async markRead() {
      const { ok } = await api.readPokes()
      if (ok) { this.unread = 0; this.load() }
    },
    fmtTime(s) { return s ? s.slice(5, 16) : '' },
  },
}
</script>

<style scoped>
.page { padding-bottom: 80rpx; }
.hero-card {
  background: linear-gradient(160deg, var(--pink-soft), var(--card));
  border-radius: 24rpx; margin: 30rpx;
  padding: 50rpx 30rpx; text-align: center;
  box-shadow: 0 8rpx 30rpx rgba(248, 165, 194, 0.2);
}
.heart-btn {
  width: 180rpx; height: 180rpx; margin: 0 auto 24rpx;
  background: linear-gradient(135deg, #f8a5c2, #ff6b9d);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 12rpx 40rpx rgba(255, 107, 157, 0.45);
  transition: all 0.25s;
}
.heart-btn.active { transform: scale(1.12); }
.heart { font-size: 90rpx; }
.hero-title { display: block; font-size: 36rpx; font-weight: bold; color: var(--text); }
.hero-sub { display: block; font-size: 24rpx; color: var(--muted); margin: 12rpx 0 28rpx; }
.btn {
  background: linear-gradient(135deg, #f8a5c2, #ff6b9d); color: #fff;
  border-radius: 40rpx; font-size: 30rpx; width: 60%;
}
.section {
  background: var(--card); border-radius: 24rpx; margin: 0 30rpx;
  padding: 24rpx 30rpx;
}
.section-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16rpx; }
.section-title { font-size: 26rpx; color: var(--muted); }
.link { font-size: 24rpx; color: var(--pink); }
.poke-item { display: flex; align-items: center; padding: 20rpx 0; border-bottom: 1rpx solid var(--border); }
.poke-item:last-child { border-bottom: none; }
.poke-item.unread { background: var(--pink-soft); margin: 0 -12rpx; padding: 20rpx 12rpx; border-radius: 12rpx; }
.poke-icon { font-size: 40rpx; margin-right: 20rpx; }
.poke-main { flex: 1; }
.poke-name { display: block; font-size: 28rpx; color: var(--text); }
.poke-time { font-size: 22rpx; color: var(--muted); margin-top: 4rpx; }
.poke-state { font-size: 22rpx; color: var(--muted); }
.poke-state.unread { color: #ff6b9d; font-weight: bold; }
.empty { text-align: center; color: var(--muted); font-size: 26rpx; padding: 40rpx 0; }
</style>
