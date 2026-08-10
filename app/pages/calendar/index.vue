<template>
  <view class="page">
    <!-- 月份切换 -->
    <view class="month-bar">
      <view class="m-btn" @click="prevMonth">‹</view>
      <text class="m-title">{{ year }} 年 {{ month }} 月</text>
      <view class="m-btn" @click="nextMonth">›</view>
    </view>

    <!-- 星期 -->
    <view class="weekdays">
      <text v-for="w in weekdays" :key="w" class="wd" :class="{ weekend: w === '日' || w === '六' }">{{ w }}</text>
    </view>

    <!-- 日期格子 -->
    <view class="days">
      <view class="day-cell" v-for="(d, i) in dayCells" :key="i" :class="{ blank: !d.day, today: d.today }">
        <template v-if="d.day">
          <text class="d-num">{{ d.day }}</text>
          <view class="d-dots">
            <view v-for="k in d.kinds" :key="k" class="d-dot" :style="{ background: kindColor(k) }"></view>
          </view>
        </template>
      </view>
    </view>

    <!-- 图例 -->
    <view class="legend">
      <view class="lg-item" v-for="k in kinds" :key="k.key">
        <view class="lg-dot" :style="{ background: k.color }"></view>
        <text class="lg-text">{{ k.label }}</text>
      </view>
    </view>

    <!-- 本月纪念日 -->
    <view class="month-list">
      <text class="ml-title">本月纪念日</text>
      <block v-if="monthAnniv.length > 0">
        <view class="ml-item" v-for="a in monthAnniv" :key="a.id">
          <view class="ml-dot" :style="{ background: kindColor(a.kind) }"></view>
          <view class="ml-main">
            <text class="ml-name">{{ a.name }}</text>
            <text class="ml-date">{{ a.date }}</text>
          </view>
          <text class="ml-days" :class="{ today: a.days_left === 0 }">{{ daysText(a) }}</text>
        </view>
      </block>
      <view class="ml-empty" v-else>这个月没有纪念日</view>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'
import { ANNIV_KINDS, annivKindMeta, daysInMonth } from '../../common/util.js'

export default {
  data() {
    const d = new Date()
    return {
      year: d.getFullYear(),
      month: d.getMonth() + 1,
      weekdays: ['日', '一', '二', '三', '四', '五', '六'],
      kinds: ANNIV_KINDS,
      annivs: [],
    }
  },
  computed: {
    dayCells() {
      const first = new Date(this.year, this.month - 1, 1)
      const startPad = first.getDay()
      const total = daysInMonth(this.year, this.month)
      const cells = []
      for (let i = 0; i < startPad; i++) cells.push({ day: 0 })
      const today = new Date()
      const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
      for (let day = 1; day <= total; day++) {
        const dateStr = `${this.year}-${String(this.month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
        cells.push({ day, dateStr, today: dateStr === todayStr, kinds: this.kindsOf(dateStr) })
      }
      return cells
    },
    monthAnniv() {
      const pre = `${this.year}-${String(this.month).padStart(2, '0')}`
      const list = this.annivs.filter(a => (a.date || '').startsWith(pre))
      return list.sort((a, b) => (a.date < b.date ? -1 : 1))
    },
  },
  onShow() {
    applyTheme()
    this.load()
  },
  methods: {
    async load() {
      const { ok, data } = await api.listAnniversaries()
      if (ok) this.annivs = data
    },
    kindsOf(dateStr) {
      const [y, m, d] = dateStr.split('-').map(Number)
      const kinds = []
      this.annivs.forEach(a => {
        const [ay, am, ad] = (a.date || '').split('-').map(Number)
        if (am === m && ad === d) kinds.push(a.kind || 'love')
      })
      return [...new Set(kinds)]
    },
    kindColor(kind) {
      return annivKindMeta(kind).color
    },
    prevMonth() {
      if (this.month === 1) { this.year--; this.month = 12 } else this.month--
    },
    nextMonth() {
      if (this.month === 12) { this.year++; this.month = 1 } else this.month++
    },
    daysText(a) {
      if (a.days_left == null) return ''
      if (a.days_left === 0) return '就是今天 🎉'
      if (a.days_left > 0) return `还有 ${a.days_left} 天`
      return `已过 ${Math.abs(a.days_left)} 天`
    },
  },
}
</script>

<style scoped>
.page { padding: 30rpx 30rpx 80rpx; }

.month-bar { display: flex; align-items: center; justify-content: center; gap: 40rpx; margin-bottom: 26rpx; }
.m-btn {
  width: 64rpx; height: 64rpx; border-radius: 50%; background: var(--card);
  display: flex; align-items: center; justify-content: center;
  font-size: 34rpx; color: var(--pink); box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}
.m-title { font-size: 32rpx; font-weight: bold; color: var(--text); letter-spacing: 2rpx; }

.weekdays { display: flex; margin-bottom: 12rpx; }
.wd { flex: 1; text-align: center; font-size: 24rpx; color: var(--muted); }
.wd.weekend { color: var(--pink); }

.days {
  display: flex; flex-wrap: wrap;
  background: var(--card); border-radius: 24rpx; padding: 20rpx 12rpx;
}
.day-cell {
  width: calc(100% / 7); aspect-ratio: 1.05; display: flex; flex-direction: column;
  align-items: center; justify-content: center; border-radius: 16rpx;
}
.day-cell.today { background: var(--pink-soft); }
.d-num { font-size: 28rpx; color: var(--text); }
.day-cell.today .d-num { color: var(--pink); font-weight: bold; }
.d-dots { display: flex; gap: 6rpx; margin-top: 6rpx; height: 12rpx; }
.d-dot { width: 12rpx; height: 12rpx; border-radius: 50%; }

.legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 26rpx; margin-top: 24rpx; }
.lg-item { display: flex; align-items: center; gap: 8rpx; }
.lg-dot { width: 16rpx; height: 16rpx; border-radius: 50%; }
.lg-text { font-size: 22rpx; color: var(--muted); }

.month-list {
  margin-top: 36rpx; background: var(--card); border-radius: 24rpx; padding: 26rpx 30rpx;
}
.ml-title { display: block; font-size: 26rpx; color: var(--muted); margin-bottom: 16rpx; }
.ml-item { display: flex; align-items: center; padding: 16rpx 0; border-bottom: 1rpx solid var(--border); }
.ml-item:last-child { border-bottom: none; }
.ml-dot { width: 18rpx; height: 18rpx; border-radius: 50%; margin-right: 18rpx; flex-shrink: 0; }
.ml-main { flex: 1; }
.ml-name { display: block; font-size: 28rpx; color: var(--text); }
.ml-date { display: block; font-size: 22rpx; color: var(--muted); margin-top: 4rpx; }
.ml-days { font-size: 24rpx; color: var(--muted); }
.ml-days.today { color: var(--pink); font-weight: bold; }
.ml-empty { text-align: center; color: var(--muted); font-size: 26rpx; padding: 30rpx 0; }
</style>
