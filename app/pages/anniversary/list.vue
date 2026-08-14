<template>
  <view class="page" :style="cssVars">
    <!-- 顶部日历：节假日 + 纪念日标注 -->
    <view class="cal-card">
      <view class="cal-header" @click="calOpen = !calOpen">
        <text class="cal-title">📅 纪念日日历</text>
        <text class="cal-toggle">{{ calOpen ? '收起 ▲' : '展开 ▼' }}</text>
      </view>

      <template v-if="calOpen">
        <view class="month-bar">
          <view class="m-btn" @click="prevMonth">‹</view>
          <text class="m-title">{{ year }} 年 {{ month }} 月</text>
          <view class="m-btn" @click="nextMonth">›</view>
        </view>

        <view class="weekdays">
          <text v-for="w in weekdays" :key="w" class="wd" :class="{ weekend: w === '日' || w === '六' }">{{ w }}</text>
        </view>

        <view class="days">
          <view
            class="day-cell"
            v-for="(d, i) in dayCells"
            :key="i"
            :class="{ blank: !d.day, today: d.today }"
          >
            <template v-if="d.day">
              <text class="d-num">{{ d.day }}</text>
              <text class="d-fest" v-if="d.festival">{{ d.festival }}</text>
              <view class="d-dots" v-if="d.kinds.length">
                <view v-for="k in d.kinds" :key="k" class="d-dot" :style="{ background: kindColor(k) }"></view>
              </view>
            </template>
          </view>
        </view>

        <view class="legend">
          <view class="lg-item">
            <view class="lg-dot holiday"></view>
            <text class="lg-text">节假日</text>
          </view>
          <view class="lg-item" v-for="k in kinds" :key="k.key">
            <view class="lg-dot" :style="{ background: k.color }"></view>
            <text class="lg-text">{{ k.label }}</text>
          </view>
        </view>
      </template>
    </view>

    <!-- 纪念日列表 -->
    <view class="item" v-for="a in list" :key="a.id" @click="openEdit(a)" @longpress="delItem(a.id)">
      <view class="left">
        <view class="name-row">
          <text class="name-emoji">{{ kindLabel(a.kind).split(' ')[0] }}</text>
          <text class="name">{{ a.name }}</text>
        </view>
        <text class="date">{{ a.date }}</text>
      </view>
      <view class="right">
        <text class="days" :class="{ today: a.days_left === 0, past: a.days_left < 0 }">{{ daysText(a) }}</text>
      </view>
    </view>

    <view class="empty" v-if="list.length === 0">
      <text>还没有纪念日，添加一个吧</text>
    </view>

    <!-- 添加按钮 -->
    <view class="fab" @click="openAdd">+</view>

    <!-- 添加/编辑弹窗 -->
    <view class="mask" v-if="showForm" @click="closeForm">
      <view class="popup" @click.stop>
        <text class="pop-title">{{ editingId ? '编辑纪念日' : '添加纪念日' }}</text>
        <input class="pop-input" v-model="form.name" placeholder="名称（如：在一起）" />
        <picker mode="date" :value="form.date" @change="e => form.date = e.detail.value">
          <view class="pop-input">{{ form.date || '选择日期' }}</view>
        </picker>
        <picker :range="kinds" range-key="label" :value="kindIndex" @change="e => form.kind = kinds[e.detail.value].key">
          <view class="pop-input">
            {{ kindLabel(form.kind) }}
          </view>
        </picker>
        <view class="pop-btns">
          <button class="pop-btn cancel" @click="closeForm">取消</button>
          <button class="pop-btn ok" @click="doSave">{{ editingId ? '保存' : '添加' }}</button>
        </view>
        <text class="pop-del" v-if="editingId" @click="doDelete">删除这个纪念日</text>
      </view>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'
import { ANNIV_KINDS, annivKindMeta, formatDate, daysInMonth, festivalOf } from '../../common/util.js'

export default {
  data() {
    const d = new Date()
    return {
      list: [],
      showForm: false,
      editingId: null,
      form: { name: '', date: formatDate(), kind: 'love' },
      kinds: ANNIV_KINDS,
      // 日历状态
      calOpen: true,
      year: d.getFullYear(),
      month: d.getMonth() + 1,
      weekdays: ['日', '一', '二', '三', '四', '五', '六'],
      annivs: [],
    }
  },
  onShow() { applyTheme(); this.loadList() },
  computed: {
    kindIndex() {
      const i = this.kinds.findIndex(k => k.key === this.form.kind)
      return i < 0 ? 0 : i
    },
    dayCells() {
      const first = new Date(this.year, this.month - 1, 1)
      const startPad = first.getDay()
      const total = daysInMonth(this.year, this.month)
      const cells = []
      for (let i = 0; i < startPad; i++) cells.push({ day: 0 })
      const t = new Date()
      const todayStr = `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, '0')}-${String(t.getDate()).padStart(2, '0')}`
      for (let day = 1; day <= total; day++) {
        const dateStr = `${this.year}-${String(this.month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
        cells.push({
          day,
          dateStr,
          today: dateStr === todayStr,
          festival: festivalOf(dateStr),
          kinds: this.kindsOf(dateStr),
        })
      }
      return cells
    },
  },
  methods: {
    kindColor(kind) { return annivKindMeta(kind).color },
    kindLabel(kind) { return annivKindMeta(kind).label },
    kindsOf(dateStr) {
      const [y, m, d] = dateStr.split('-').map(Number)
      const kinds = []
      this.annivs.forEach(a => {
        const [ay, am, ad] = (a.date || '').split('-').map(Number)
        if (am === m && ad === d) kinds.push(a.kind || 'love')
      })
      return [...new Set(kinds)]
    },
    async loadList() {
      const { ok, data } = await api.listAnniversaries()
      if (ok) { this.list = data; this.annivs = data }
    },
    daysText(a) {
      if (a.days_left == null) return ''
      if (a.days_left === 0) return '就是今天 🎉'
      if (a.days_left > 0) return `还有 ${a.days_left} 天`
      return `已过 ${Math.abs(a.days_left)} 天`
    },
    prevMonth() {
      if (this.month === 1) { this.year--; this.month = 12 } else this.month--
    },
    nextMonth() {
      if (this.month === 12) { this.year++; this.month = 1 } else this.month++
    },
    openAdd() { this.editingId = null; this.form = { name: '', date: formatDate(), kind: 'love' }; this.showForm = true },
    openEdit(a) { this.editingId = a.id; this.form = { name: a.name, date: a.date, kind: a.kind || 'love' }; this.showForm = true },
    closeForm() { this.showForm = false; this.editingId = null },
    async doSave() {
      if (!this.form.name) { uni.showToast({ title: '请输入名称', icon: 'none' }); return }
      const { ok, msg } = this.editingId
        ? await api.updateAnniversary(this.editingId, this.form)
        : await api.createAnniversary(this.form)
      if (ok) { uni.showToast({ title: '已保存', icon: 'success' }); this.closeForm(); this.loadList() }
      else { uni.showToast({ title: msg, icon: 'none' }) }
    },
    async delItem(id) {
      const { confirm } = await uni.showModal({ title: '删除', content: '确定要删除这个纪念日吗？' })
      if (!confirm) return
      await api.deleteAnniversary(id)
      uni.showToast({ title: '已删除', icon: 'success' })
      this.loadList()
    },
    async doDelete() {
      if (!this.editingId) return
      await api.deleteAnniversary(this.editingId)
      uni.showToast({ title: '已删除', icon: 'success' })
      this.closeForm(); this.loadList()
    },
  },
}
</script>

<style scoped>
.page { padding-bottom: 140rpx; }

/* ---------- 顶部日历 ---------- */
.cal-card {
  background: var(--card);
  border-radius: 20rpx;
  padding: 22rpx 24rpx 28rpx;
  margin: 20rpx 24rpx;
  box-shadow: 0 4rpx 18rpx rgba(0, 0, 0, 0.05);
}
.cal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 16rpx;
}
.cal-title { font-size: 30rpx; font-weight: bold; color: var(--text); }
.cal-toggle { font-size: 24rpx; color: var(--muted); }

.month-bar { display: flex; align-items: center; justify-content: center; gap: 40rpx; margin-bottom: 22rpx; }
.m-btn {
  width: 58rpx; height: 58rpx; border-radius: 50%;
  background: var(--pink-soft);
  display: flex; align-items: center; justify-content: center;
  font-size: 34rpx; color: var(--pink);
}
.m-title { font-size: 30rpx; font-weight: bold; color: var(--text); }

.weekdays { display: flex; margin-bottom: 10rpx; }
.wd { flex: 1; text-align: center; font-size: 22rpx; color: var(--muted); }
.wd.weekend { color: var(--pink); }

.days { display: flex; flex-wrap: wrap; }
.day-cell {
  width: calc(100% / 7);
  aspect-ratio: 1.05;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding-top: 8rpx;
  border-radius: 12rpx;
  box-sizing: border-box;
}
.day-cell.today { background: var(--pink-soft); }
.d-num { font-size: 26rpx; color: var(--text); line-height: 1.2; }
.day-cell.today .d-num { color: var(--pink); font-weight: bold; }
.d-fest {
  font-size: 17rpx;
  color: #e74c3c;
  margin-top: 2rpx;
  line-height: 1.1;
  transform: scale(0.92);
  white-space: nowrap;
}
.d-dots { display: flex; gap: 5rpx; margin-top: 4rpx; height: 10rpx; }
.d-dot { width: 10rpx; height: 10rpx; border-radius: 50%; }

.legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 20rpx; margin-top: 20rpx; }
.lg-item { display: flex; align-items: center; gap: 8rpx; }
.lg-dot { width: 16rpx; height: 16rpx; border-radius: 50%; }
.lg-dot.holiday { background: #e74c3c; }
.lg-text { font-size: 20rpx; color: var(--muted); }

/* ---------- 纪念日列表 ---------- */
.item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--card);
  border-radius: 16rpx;
  padding: 26rpx 28rpx;
  margin: 0 24rpx 18rpx;
}
.left { display: flex; flex-direction: column; }
.name-row { display: flex; align-items: center; }
.name-emoji { font-size: 30rpx; margin-right: 10rpx; }
.name { font-size: 30rpx; font-weight: bold; }
.date { font-size: 24rpx; color: var(--muted); margin-top: 6rpx; }
.days { font-size: 28rpx; color: var(--pink); }
.days.today { color: #e74c3c; font-weight: bold; }
.days.past { color: var(--muted); }
.fab {
  position: fixed; bottom: 40rpx; right: 40rpx;
  width: 100rpx; height: 100rpx;
  background: var(--pink); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 50rpx;
  box-shadow: 0 4rpx 12rpx rgba(248, 165, 194, 0.5);
}
.mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 999;
}
.popup {
  width: 600rpx; background: var(--card); border-radius: 24rpx; padding: 40rpx;
}
.pop-title { font-size: 32rpx; font-weight: bold; display: block; margin-bottom: 30rpx; }
.pop-input {
  width: 100%; height: 80rpx; background: var(--bg);
  border-radius: 12rpx; padding: 0 20rpx; margin-bottom: 20rpx;
  font-size: 28rpx; line-height: 80rpx;
}
.pop-btns { display: flex; gap: 20rpx; margin-top: 20rpx; }
.pop-btn { flex: 1; height: 80rpx; line-height: 80rpx; border-radius: 12rpx; font-size: 28rpx; text-align: center; }
.pop-btn.cancel { background: var(--input-bg); color: var(--muted); }
.pop-btn.ok { background: var(--pink); color: #fff; }
.pop-del { display: block; text-align: center; color: #e74c3c; font-size: 26rpx; margin-top: 26rpx; }
.empty { text-align: center; color: var(--muted); font-size: 28rpx; padding-top: 120rpx; }
</style>
