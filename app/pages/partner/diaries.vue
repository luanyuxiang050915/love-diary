<template>
  <view class="page" :style="cssVars">
    <block v-if="diaries.length > 0">
      <view class="card" v-for="d in diaries" :key="d.id">
        <view class="card-header">
          <text class="card-date">{{ d.date }}</text>
          <text class="card-mood">{{ d.mood || '无' }}</text>
        </view>
        <view class="card-body">{{ d.content }}</view>
        <view class="card-images" v-if="d.images.length">
          <image v-for="(img, i) in d.images" :key="i" :src="imgUrl(img)" mode="aspectFill" class="card-img" />
        </view>
      </view>
    </block>

    <view class="empty" v-else>
      <text class="empty-icon">❤️</text>
      <text>TA 还没有写可见日记，或者你还没有绑定另一半</text>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'

export default {
  data() {
    return { diaries: [] }
  },
  onShow() { applyTheme();
    this.loadList()
  },
  methods: {
    async loadList() {
      const { ok, data } = await api.getPartnerDiaries()
      if (ok) this.diaries = data
      else uni.showToast({ title: '加载失败', icon: 'none' })
    },
    imgUrl(u) {
      if (u && (u.startsWith('http://') || u.startsWith('https://'))) return u
      return 'http://47.93.241.64:8000' + u
    },
  },
}
</script>

<style scoped>
.page { padding-bottom: 60rpx; }
.card {
  background: var(--card); border-radius: 16rpx;
  padding: 28rpx; margin: 20rpx 30rpx;
}
.card-header { display: flex; align-items: center; margin-bottom: 14rpx; }
.card-date { font-size: 24rpx; color: var(--muted); margin-right: 16rpx; }
.card-mood { font-size: 24rpx; color: var(--pink); background: var(--pink-soft); padding: 4rpx 14rpx; border-radius: 8rpx; }
.card-body { font-size: 28rpx; color: var(--text); line-height: 1.7; display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden; }
.card-images { display: flex; flex-wrap: wrap; margin-top: 16rpx; }
.card-img { width: 160rpx; height: 160rpx; border-radius: 12rpx; margin-right: 12rpx; }
.empty { display: flex; flex-direction: column; align-items: center; padding-top: 200rpx; color: var(--muted); font-size: 28rpx; }
.empty-icon { font-size: 80rpx; margin-bottom: 20rpx; }
</style>
