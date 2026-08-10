<template>
  <view class="page">
    <!-- 月份切换 -->
    <view class="month-bar">
      <text class="month-btn" @click="prevMonth">‹</text>
      <text class="month-text">{{ month }}</text>
      <text class="month-btn" @click="nextMonth">›</text>
    </view>

    <view class="summary-card">
      <text class="s-emoji">📊</text>
      <view class="s-main">
        <text class="s-title">{{ month }} 心情月报</text>
        <text class="s-sub">{{ report.total > 0 ? `这个月你写了 ${report.total} 篇带心情的日记` : '这个月还没有带心情的日记' }}</text>
      </view>
    </view>

    <!-- 心情排行 -->
    <view class="section">
      <view class="section-title">心情排行</view>
      <block v-if="report.stats.length > 0">
        <view class="mood-row" v-for="(s, i) in report.stats" :key="i">
          <text class="mood-rank">{{ i + 1 }}</text>
          <text class="mood-name">{{ s.mood }}</text>
          <view class="mood-bar"><view class="mood-fill" :style="{ width: barWidth(s.count) + '%' }"></view></view>
          <text class="mood-count">{{ s.count }} 篇</text>
        </view>
      </block>
      <view class="empty" v-else>多写几篇日记，下个月就有月报啦 ✍️</view>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'

export default {
  data() {
    const d = new Date()
    return { month: `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`, report: { total: 0, stats: [] } }
  },
  onShow() { applyTheme(); this.load() },
  methods: {
    async load() {
      const { ok, data } = await api.getMoodReport(this.month)
      if (ok) this.report = data
      else uni.showToast({ title: '加载失败', icon: 'none' })
    },
    barWidth(count) {
      const max = this.report.stats.length ? this.report.stats[0].count : 1
      return Math.max(count / max * 100, 8)
    },
    prevMonth() {
      const [y, m] = this.month.split('-').map(Number)
      const d = new Date(y, m - 2, 1)
      this.month = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
      this.load()
    },
    nextMonth() {
      const [y, m] = this.month.split('-').map(Number)
      const d = new Date(y, m, 1)
      this.month = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
      this.load()
    },
  },
}
</script>

<style scoped>
.page { padding-bottom: 80rpx; }
.month-bar { display: flex; align-items: center; justify-content: center; gap: 40rpx; margin: 30rpx 0 10rpx; }
.month-btn { width: 70rpx; height: 70rpx; border-radius: 50%; background: var(--card); text-align: center; line-height: 70rpx; font-size: 40rpx; color: var(--pink); box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.06); }
.month-text { font-size: 32rpx; font-weight: bold; color: var(--text); letter-spacing: 2rpx; }
.summary-card {
  background: linear-gradient(135deg, var(--pink-soft), var(--purple-soft));
  border-radius: 24rpx; margin: 20rpx 30rpx; padding: 30rpx;
  display: flex; align-items: center;
}
.s-emoji { font-size: 60rpx; margin-right: 20rpx; }
.s-title { display: block; font-size: 30rpx; font-weight: bold; color: var(--text); }
.s-sub { display: block; font-size: 24rpx; color: var(--muted); margin-top: 8rpx; }
.section { background: var(--card); border-radius: 24rpx; margin: 20rpx 30rpx; padding: 24rpx 30rpx; }
.section-title { font-size: 26rpx; color: var(--muted); margin-bottom: 20rpx; }
.mood-row { display: flex; align-items: center; margin-bottom: 22rpx; }
.mood-rank {
  width: 40rpx; height: 40rpx; border-radius: 12rpx; text-align: center; line-height: 40rpx;
  font-size: 22rpx; font-weight: bold; color: #fff; background: linear-gradient(135deg, #f8a5c2, #ff6b9d); margin-right: 16rpx; flex-shrink: 0;
}
.mood-name { width: 140rpx; font-size: 26rpx; color: var(--text); }
.mood-bar { flex: 1; height: 20rpx; background: var(--bg); border-radius: 10rpx; overflow: hidden; margin: 0 16rpx; }
.mood-fill { height: 100%; background: linear-gradient(90deg, #f8a5c2, #c44dff); border-radius: 10rpx; transition: width .5s; }
.mood-count { font-size: 22rpx; color: var(--muted); flex-shrink: 0; }
.empty { text-align: center; color: var(--muted); font-size: 26rpx; padding: 50rpx 0; }
</style>
