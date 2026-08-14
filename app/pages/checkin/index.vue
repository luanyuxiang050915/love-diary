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

    <!-- 打卡日历：本月，左右翻页查看历史 -->
    <view class="section">
      <view class="section-head">
        <text class="section-title">打卡日历</text>
        <text class="section-tip">左右翻页可查历史</text>
      </view>
      <view class="month-bar">
        <view class="m-btn" @click="prevMonth">‹</view>
        <text class="m-title">{{ year }}年{{ month }}月</text>
        <view class="m-btn" @click="nextMonth">›</view>
      </view>
      <view class="cal-head">
        <text class="cal-wd" v-for="w in weekdays" :key="w" :class="{ weekend: w === '日' || w === '六' }">{{ w }}</text>
      </view>
      <view class="cal-row" v-for="(r, ri) in rows" :key="ri">
        <template v-for="(c, ci) in r" :key="ci">
          <view class="day blank" v-if="!c"></view>
          <view class="day" v-else :class="{ done: c.done, today: c.today }">
            <text class="day-num">{{ c.num }}</text>
            <text class="day-heart" v-if="c.done">❤</text>
          </view>
        </template>
      </view>
      <view class="legend">❤ 已打卡 · 累计打卡 {{ st.total }} 天</view>
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
    const d = new Date()
    return {
      st: { today: false, total: 0, streak: 0, best: 0, dates: [] },
      rows: [],
      weekdays: ['日', '一', '二', '三', '四', '五', '六'],
      year: d.getFullYear(),
      month: d.getMonth() + 1,
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
      const monthStr = `${this.year}-${String(this.month).padStart(2, '0')}`
      const [st, monthRes] = await Promise.all([
        api.getCheckin(),
        api.getCheckin({ month: monthStr }),
      ])
      if (!st.ok) return
      this.st = st.data
      const set = new Set(monthRes.ok ? monthRes.data.dates : [])

      // 当月日历：按星期对齐，7 列换行
      const first = new Date(this.year, this.month - 1, 1)
      const pad = first.getDay()
      const total = new Date(this.year, this.month, 0).getDate()
      const todayStr = fmt(new Date())
      const rows = []
      let row = []
      for (let i = 0; i < pad; i++) row.push(null)
      for (let day = 1; day <= total; day++) {
        const key = `${this.year}-${String(this.month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
        row.push({ key, num: day, done: set.has(key), today: key === todayStr })
        if (row.length === 7) { rows.push(row); row = [] }
      }
      if (row.length) {
        while (row.length < 7) row.push(null)
        rows.push(row)
      }
      this.rows = rows
    },
    prevMonth() {
      if (this.month === 1) { this.year--; this.month = 12 } else this.month--
      this.load()
    },
    nextMonth() {
      const now = new Date()
      if (this.year === now.getFullYear() && this.month === now.getMonth() + 1) {
        uni.showToast({ title: '只能看到本月哦', icon: 'none' })
        return
      }
      if (this.month === 12) { this.year++; this.month = 1 } else this.month++
      this.load()
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
.section-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18rpx; }
.section-title { font-size: 26rpx; color: var(--muted); }
.section-tip { font-size: 22rpx; color: var(--pink); }
.month-bar { display: flex; align-items: center; justify-content: center; gap: 36rpx; margin-bottom: 20rpx; }
.m-btn {
  width: 58rpx; height: 58rpx; border-radius: 50%;
  background: var(--pink-soft);
  display: flex; align-items: center; justify-content: center;
  font-size: 34rpx; color: var(--pink);
}
.m-title { font-size: 30rpx; font-weight: bold; color: var(--text); letter-spacing: 2rpx; }
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
