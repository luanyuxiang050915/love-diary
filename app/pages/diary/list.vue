<template>
  <view class="page">
    <!-- 日记卡片列表 -->
    <block v-if="diaries.length > 0">
      <view class="card" v-for="d in diaries" :key="d.id" @click="goWrite(d.id)" @longpress="delDiary(d.id)">
        <view class="card-header">
          <text class="card-date">{{ d.date }}</text>
          <text class="card-mood">{{ moodText(d.mood) }}</text>
          <text class="card-vis" v-if="!d.visible_to_partner">🔒</text>
        </view>
        <view class="card-body">{{ d.content }}</view>
        <view class="card-images" v-if="d.images.length">
          <image v-for="(img, i) in d.images" :key="i" :src="imgUrl(img)" mode="aspectFill" class="card-img" />
        </view>
      </view>
    </block>

    <view class="empty" v-else>
      <text class="empty-icon">📝</text>
      <text>还没有日记，写一篇吧</text>
    </view>

    <!-- 悬浮写日记按钮 -->
    <view class="fab" @click="goWrite(0)">
      <text class="fab-text">+</text>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'
import { MOODS } from '../../common/util.js'

export default {
  data() {
    return { diaries: [] }
  },
  onShow() { applyTheme(); this.loadList() },

  // 导航栏右侧"TA的日记"按钮（H5 用 buttons，小程序/App 需在 pages.json 配置）
  // 这里通过 onNavigationBarButtonTap 处理（需在 pages.json diary/list 中配置 buttons）
  // 简化：列表底部放一个入口，或者用下拉刷新

  methods: {
    async loadList() {
      const { ok, data } = await api.listDiaries()
      if (ok) this.diaries = data
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
    goPartner() {
      uni.navigateTo({ url: '/pages/partner/diaries' })
    },
  },
}
</script>

<style scoped>
.page { padding-bottom: 140rpx; }
.card {
  background: var(--card);
  margin: 20rpx 30rpx;
  border-radius: 16rpx;
  padding: 28rpx;
}
.card-header { display: flex; align-items: center; margin-bottom: 14rpx; }
.card-date { font-size: 24rpx; color: var(--muted); margin-right: 16rpx; }
.card-mood { font-size: 24rpx; color: var(--pink); background: var(--pink-soft); padding: 4rpx 14rpx; border-radius: 8rpx; }
.card-vis { font-size: 22rpx; margin-left: auto; }
.card-body { font-size: 28rpx; color: var(--text); line-height: 1.7; display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden; }
.card-images { display: flex; flex-wrap: wrap; margin-top: 16rpx; }
.card-img { width: 160rpx; height: 160rpx; border-radius: 12rpx; margin-right: 12rpx; }
.fab {
  position: fixed; bottom: 40rpx; right: 40rpx;
  width: 100rpx; height: 100rpx;
  background: var(--pink); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(248,165,194,0.5);
}
.fab-text { font-size: 50rpx; color: #fff; }

.empty { display: flex; flex-direction: column; align-items: center; padding-top: 200rpx; color: var(--muted); font-size: 28rpx; }
.empty-icon { font-size: 80rpx; margin-bottom: 20rpx; }
</style>
