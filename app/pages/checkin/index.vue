<template>
  <view class="page">
    <!-- 打卡按钮 -->
    <view class="checkin-card">
      <view class="checkin-btn" :class="{ done: st.today }" @click="doCheckin">
        <text class="checkin-emoji">{{ st.today ? '✅' : '🔥' }}</text>
        <text class="checkin-text">{{ st.today ? '今天已打卡' : '打卡想 TA' }}</text>
      </view>
      <view class="stats-row">
        <view class="stat"><text class="num">{{ st.streak }}</text><text class="label">连续天数</text></view>
        <view class="stat"><text class="num">{{ st.total }}</text><text class="label">累计天数</text></view>
        <view class="stat"><text class="num">{{ st.best }}</text><text class="label">最长纪录</text></view>
      </view>
    </view>

    <!-- 最近 30 天 -->
    <view class="section">
      <view class="section-title">最近 30 天</view>
      <view class="days">
        <view class="day" v-for="(d, i) in days" :key="i" :class="{ done: d.done }">
          <text>{{ d.done ? '❤' : '' }}</text>
        </view>
      </view>
      <view class="legend"><text>每天都来打卡，让爱不断线</text></view>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'

function fmt(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

export default {
  data() {
    return { st: { today: false, total: 0, streak: 0, best: 0, dates: [] }, days: [] }
  },
  onShow() { this.load() },
  methods: {
    async load() {
      const { ok, data } = await api.getCheckin()
      if (!ok) return
      this.st = data
      const set = new Set(data.dates)
      const days = []
      for (let i = 29; i >= 0; i--) {
        const d = new Date()
        d.setDate(d.getDate() - i)
        days.push({ key: fmt(d), done: set.has(fmt(d)) })
      }
      this.days = days
    },
    async doCheckin() {
      if (this.st.today) { uni.showToast({ title: '今天已经打过卡啦', icon: 'none' }); return }
      const { ok, msg } = await api.doCheckin()
      uni.showToast({ title: ok ? '打卡成功 ❤' : msg, icon: 'none' })
      if (ok) this.load()
    },
  },
}
</script>

<style scoped>
.page { padding-bottom: 80rpx; }
.checkin-card {
  background: linear-gradient(160deg, #fff0f5, #f3ecff);
  border-radius: 24rpx; margin: 30rpx; padding: 40rpx 30rpx; text-align: center;
}
.checkin-btn {
  width: 240rpx; height: 240rpx; margin: 0 auto 30rpx;
  background: linear-gradient(135deg, #ff6b9d, #f8a5c2);
  border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center;
  box-shadow: 0 14rpx 44rpx rgba(255, 107, 157, 0.45);
}
.checkin-btn.done { background: linear-gradient(135deg, #4ade80, #22c55e); box-shadow: 0 14rpx 44rpx rgba(74, 222, 128, 0.4); }
.checkin-emoji { font-size: 70rpx; }
.checkin-text { color: #fff; font-size: 28rpx; margin-top: 8rpx; }
.stats-row { display: flex; }
.stat { flex: 1; }
.num { display: block; font-size: 48rpx; font-weight: bold; color: #ff6b9d; }
.done + .stats-row .num { color: #333; }
.label { display: block; font-size: 22rpx; color: #999; margin-top: 4rpx; }
.section { background: #fff; border-radius: 24rpx; margin: 0 30rpx; padding: 24rpx 30rpx; }
.section-title { font-size: 26rpx; color: #999; margin-bottom: 20rpx; }
.days { display: flex; flex-wrap: wrap; gap: 10rpx; }
.day {
  width: 56rpx; height: 56rpx; border-radius: 14rpx;
  background: #f5f5f5; display: flex; align-items: center; justify-content: center;
  font-size: 24rpx; color: #fff;
}
.day.done { background: linear-gradient(135deg, #ff6b9d, #f8a5c2); }
.legend { text-align: center; font-size: 22rpx; color: #bbb; margin-top: 20rpx; }
</style>
