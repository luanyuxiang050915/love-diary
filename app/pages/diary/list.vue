<template>
  <view class="page" :style="cssVars">
    <!-- 男女双列日记 -->
    <view class="columns">
      <view class="column" v-for="col in columns" :key="col.key">
        <view class="col-head" :class="col.cls">
          <text class="col-emoji">{{ col.emoji }}</text>
          <text class="col-name">{{ col.label }}</text>
          <text class="col-count">{{ col.diaries.length }} 篇</text>
        </view>

        <view class="col-list">
          <block v-if="col.diaries.length > 0">
            <view
              class="rect-card"
              v-for="d in col.diaries"
              :key="d.id"
              @click="openDiary(d)"
              @longpress="maybeDel(d)"
            >
              <view class="card-top">
                <text class="card-date">{{ d.date }}</text>
                <text class="card-mood">{{ moodText(d.mood) }}</text>
                <text class="card-private" v-if="d.mine && !d.visible_to_partner">🔒</text>
              </view>
              <view class="card-body">{{ d.content }}</view>
              <view class="card-imgs" v-if="d.images && d.images.length">
                <image
                  v-for="(img, i) in d.images"
                  :key="i"
                  :src="imgUrl(img)"
                  mode="aspectFill"
                  class="card-img"
                />
              </view>
            </view>
          </block>
          <view class="col-empty" v-else>
            <text class="col-empty-emoji">{{ col.emptyEmoji }}</text>
            <text class="col-empty-text">{{ col.emptyText }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 写日记按钮 -->
    <view class="fab" @click="goWrite(0)">
      <text class="fab-text">+</text>
    </view>

    <!-- 对方日记只读弹窗 -->
    <view class="mask" v-if="showDetail" @click="showDetail = false">
      <view class="detail" @click.stop>
        <text class="detail-title">{{ detail.date }} · {{ moodText(detail.mood) }}</text>
        <scroll-view scroll-y class="detail-body">
          <text class="detail-content">{{ detail.content }}</text>
        </scroll-view>
        <button class="detail-close" @click="showDetail = false">关 闭</button>
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
      diaries: [],          // 双方日记合并，带 gender / mine 标记
      partnerBound: false,
      myGender: '',
      showDetail: false,
      detail: null,
    }
  },
  computed: {
    maleDiaries() { return this.diaries.filter(d => d.gender === '男') },
    femaleDiaries() { return this.diaries.filter(d => d.gender === '女') },
    columns() {
      return [
        {
          key: 'male', label: '男', emoji: '👦', cls: 'male',
          diaries: this.maleDiaries,
          emptyEmoji: '📭',
          emptyText: this.partnerBound ? '这里还没有男生的日记' : '还没有绑定另一半',
        },
        {
          key: 'female', label: '女', emoji: '👧', cls: 'female',
          diaries: this.femaleDiaries,
          emptyEmoji: '📭',
          emptyText: this.partnerBound ? '这里还没有女生的日记' : '还没有绑定另一半',
        },
      ]
    },
  },
  onShow() { applyTheme(); this.loadList() },

  methods: {
    async loadList() {
      const me = store.getUser() || {}
      this.myGender = me.gender === '男' || me.gender === '女' ? me.gender : ''

      const mine = await api.listDiaries()
      const partner = await api.getPartnerDiaries()
      const all = []

      ;(mine.ok ? mine.data : []).forEach(d => {
        all.push({ ...d, mine: true, gender: this.normGender(d.gender, this.myGender || '男') })
      })

      if (partner.ok) {
        this.partnerBound = true
        const pGender = (partner.data.find(x => x.gender) || {}).gender || ''
        partner.data.forEach(d => {
          all.push({ ...d, mine: false, gender: this.normGender(d.gender, pGender || '女') })
        })
      } else {
        this.partnerBound = false
      }

      all.sort((a, b) => {
        if (a.date === b.date) return (b.id || 0) - (a.id || 0)
        return a.date < b.date ? 1 : -1
      })
      this.diaries = all
    },
    normGender(g, fallback) {
      return (g === '男' || g === '女') ? g : fallback
    },
    openDiary(d) {
      if (d.mine) { this.goWrite(d.id); return }
      this.detail = d
      this.showDetail = true
    },
    maybeDel(d) {
      if (!d.mine) {
        uni.showToast({ title: '这是 TA 的日记，不能删除', icon: 'none' })
        return
      }
      this.delDiary(d.id)
    },
    goWrite(id) {
      const url = id ? `/pages/diary/write?diary_id=${id}` : '/pages/diary/write'
      uni.navigateTo({ url })
    },
    async delDiary(id) {
      const { confirm } = await uni.showModal({ title: '删除日记', content: '确定要删除吗？' })
      if (!confirm) return
      const { ok } = await api.deleteDiary(id)
      if (ok) { uni.showToast({ title: '已删除', icon: 'success' }); this.loadList() }
    },
    moodText(m) { return m || '无' },
    imgUrl(u) {
      if (u && (u.startsWith('http://') || u.startsWith('https://'))) return u
      return 'http://47.93.241.64:8000' + u
    },
  },
}
</script>

<style scoped>
.page { padding-bottom: 140rpx; }

/* ---------- 双列布局 ---------- */
.columns {
  display: flex;
  align-items: flex-start;
  padding: 24rpx 20rpx 0;
  gap: 20rpx;
}
.column { flex: 1; min-width: 0; }

.col-head {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  height: 72rpx;
  border-radius: 14rpx;
  margin-bottom: 18rpx;
  font-weight: bold;
}
.col-head.male { background: rgba(59, 130, 246, 0.12); color: #3b82f6; }
.col-head.female { background: rgba(248, 165, 194, 0.18); color: #f06292; }
.col-emoji { font-size: 30rpx; }
.col-name { font-size: 30rpx; }
.col-count { font-size: 22rpx; font-weight: normal; opacity: 0.75; }

.col-list { display: flex; flex-direction: column; }

/* ---------- 矩形日记卡片 ---------- */
.rect-card {
  background: var(--card);
  border: 1rpx solid var(--border);
  border-radius: 12rpx;
  padding: 22rpx;
  margin-bottom: 18rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.04);
}
.card-top { display: flex; align-items: center; margin-bottom: 12rpx; }
.card-date { font-size: 22rpx; color: var(--muted); margin-right: 12rpx; flex-shrink: 0; }
.card-mood {
  font-size: 22rpx;
  color: var(--pink);
  background: var(--pink-soft);
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}
.card-private { font-size: 22rpx; margin-left: auto; }
.card-body {
  font-size: 26rpx;
  color: var(--text);
  line-height: 1.65;
  display: -webkit-box;
  -webkit-line-clamp: 7;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-all;
}
.card-imgs { display: flex; flex-wrap: wrap; gap: 8rpx; margin-top: 12rpx; }
.card-img { width: 150rpx; height: 150rpx; border-radius: 10rpx; }

/* ---------- 空状态 ---------- */
.col-empty {
  background: var(--card);
  border: 1rpx dashed var(--border);
  border-radius: 12rpx;
  padding: 44rpx 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--muted);
  font-size: 22rpx;
}
.col-empty-emoji { font-size: 44rpx; margin-bottom: 10rpx; }
.col-empty-text { text-align: center; line-height: 1.5; }

/* ---------- 写日记按钮 ---------- */
.fab {
  position: fixed;
  bottom: 40rpx;
  right: 40rpx;
  width: 100rpx;
  height: 100rpx;
  background: var(--pink);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(248, 165, 194, 0.5);
}
.fab-text { font-size: 50rpx; color: #fff; }

/* ---------- 对方日记只读弹窗 ---------- */
.mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 999;
}
.detail {
  width: 600rpx;
  max-height: 70vh;
  background: var(--card);
  border-radius: 24rpx;
  padding: 36rpx 32rpx 28rpx;
  display: flex;
  flex-direction: column;
}
.detail-title { font-size: 28rpx; font-weight: bold; color: var(--pink); margin-bottom: 18rpx; }
.detail-body { flex: 1; max-height: 48vh; }
.detail-content { font-size: 28rpx; color: var(--text); line-height: 1.7; }
.detail-close {
  margin-top: 24rpx;
  height: 76rpx;
  line-height: 76rpx;
  border-radius: 12rpx;
  background: var(--pink);
  color: #fff;
  font-size: 28rpx;
  text-align: center;
}
</style>
