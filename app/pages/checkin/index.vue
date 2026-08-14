<template>
  <view class="page" :style="cssVars">
    <!-- 打卡按钮 -->
    <view class="checkin-card">
      <view class="date-line">
        <text class="date-year">{{ yearText }}</text>
        <text class="date-main">{{ monthDayText }}</text>
        <text class="date-week">{{ weekText }}</text>
      </view>
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
      <view class="cal-group" v-for="g in groups" :key="g.label">
        <text class="cal-month">{{ g.label }}</text>
        <view class="cal-head">
          <text class="cal-wd" v-for="w in weekdays" :key="w" :class="{ weekend: w === '日' || w === '六' }">{{ w }}</text>
        </view>
        <view class="cal-row" v-for="(r, ri) in g.rows" :key="ri">
          <template v-for="(c, ci) in r" :key="ci">
            <view class="day blank" v-if="!c"></view>
            <view class="day" v-else :class="{ done: c.done, today: c.today }">
              <text class="day-num">{{ c.num }}</text>
              <text class="day-heart" v-if="c.done">❤</text>
            </view>
          </template>
        </view>
      </view>
      <view class="legend"><text>❤ 已打卡 · 每天都来，让爱不断线</text></view>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'

function fmt(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

export default {
  data() {
    return {
      st: { today: false, total: 0, streak: 0, best: 0, dates: [] },
      groups: [],
      weekdays: ['日', '一', '二', '三', '四', '五', '六'],
    }
  },
  computed: {
    yearText() {
      const d = new Date()
      return `${d.getFullYear()}年`
    },
    monthDayText() {
      const d = new Date()
      return `${d.getMonth() + 1}月${d.getDate()}日`
    },
    weekText() {
      return `星期${this.weekdays[new Date().getDay()]}`
    },
  },
  onShow() { applyTheme(); this.load() },
  methods: {
    async load() {
      const { ok, data } = await api.getCheckin()
      if (!ok) return
      this.st = data
      const set = new Set(data.dates)
      // 最近 30 天，按月分组：每组带星期对齐的空格 + 当月日期
      const groups = []
      let cur = null
      for (let i = 29; i >= 0; i--) {
        const d = new Date()
        d.setDate(d.getDate() - i)
        const key = fmt(d)
        const label = `${d.getMonth() + 1}月`
        if (!cur || cur.label !== label) {
          const first = new Date(d.getFullYear(), d.getMonth(), 1)
          cur = { label, pad: first.getDay(), days: [] }
          groups.push(cur)
        }
        cur.days.push({ key, num: d.getDate(), done: set.has(key), today: i === 0 })
      }
      // 每组按 7 列换行，第一行前面补当月 1 号的星期偏移空格
      this.groups = groups.map(g => {
        const rows = []
        let row = []
        for (let i = 0; i < g.pad; i++) row.push(null)
        g.days.forEach(c => {
          row.push(c)
          if (row.length === 7) { rows.push(row); row = [] }
        })
        if (row.length) {
          while (row.length < 7) row.push(null)
          rows.push(row)
        }
        return { label: g.label, rows }
      })
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
  background: linear-gradient(160deg, var(--pink-soft), var(--purple-soft));
  border-radius: 24rpx; margin: 30rpx; padding: 40rpx 30rpx; text-align: center;
}
.date-line { margin-bottom: 30rpx; }
.date-year { display: block; font-size: 24rpx; color: var(--muted); letter-spacing: 4rpx; }
.date-main {
  display: block; font-size: 52rpx; font-weight: bold;
  color: var(--text); margin-top: 6rpx; letter-spacing: 2rpx;
}
.date-week {
  display: inline-block; margin-top: 14rpx;
  font-size: 24rpx; color: var(--pink);
  background: var(--card); border-radius: 20rpx;
  padding: 6rpx 28rpx;
}
.checkin-btn {
  width: 240rpx; height: 240rpx; margin: 0 auto 30rpx;
  background: linear-gradient(135deg, var(--hot), var(--pink));
  border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center;
  box-shadow: 0 14rpx 44rpx rgba(255, 107, 157, 0.45);
}
.checkin-btn.done { background: linear-gradient(135deg, #4ade80, #22c55e); box-shadow: 0 14rpx 44rpx rgba(74, 222, 128, 0.4); }
.checkin-emoji { font-size: 70rpx; }
.checkin-text { color: #fff; font-size: 28rpx; margin-top: 8rpx; }
.stats-row { display: flex; }
.stat { flex: 1; }
.num { display: block; font-size: 48rpx; font-weight: bold; color: var(--hot); }
.done + .stats-row .num { color: var(--text); }
.label { display: block; font-size: 22rpx; color: var(--muted); margin-top: 4rpx; }
.section { background: var(--card); border-radius: 24rpx; margin: 0 30rpx; padding: 24rpx 30rpx; }
.section-title { font-size: 26rpx; color: var(--muted); margin-bottom: 20rpx; }
.cal-group { margin-bottom: 24rpx; }
.cal-group:last-child { margin-bottom: 0; }
.cal-month {
  display: inline-block;
  font-size: 24rpx; font-weight: bold;
  background: var(--pink-soft); color: var(--pink);
  border-radius: 12rpx; padding: 4rpx 18rpx; margin-bottom: 14rpx;
}
.cal-head { display: flex; gap: 10rpx; margin-bottom: 10rpx; }
.cal-wd { flex: 1; text-align: center; font-size: 22rpx; color: var(--muted); }
.cal-wd.weekend { color: var(--pink); }
.cal-row { display: flex; gap: 10rpx; }
.day {
  flex: 1; aspect-ratio: 1; border-radius: 14rpx;
  background: var(--input-bg);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.day.blank { background: transparent; }
.day-num { font-size: 26rpx; color: var(--text); line-height: 1.2; }
.day.today .day-num { color: var(--pink); font-weight: bold; }
.day-heart { font-size: 20rpx; line-height: 1.2; color: #fff; }
.day.done { background: linear-gradient(135deg, var(--hot), var(--pink)); }
.day.done .day-num { color: #fff; font-weight: bold; }
.day.done.today { box-shadow: 0 0 0 4rpx var(--hot); }
.day.today:not(.done) { background: var(--pink-soft); box-shadow: 0 0 0 4rpx var(--pink); }
.legend { text-align: center; font-size: 22rpx; color: var(--muted); margin-top: 20rpx; }
</style>
