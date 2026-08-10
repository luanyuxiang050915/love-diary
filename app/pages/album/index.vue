<template>
  <view class="page">
    <!-- 顶部操作 -->
    <view class="topbar">
      <text class="count">两个人的回忆 · {{ photos.length }} 张</text>
      <button class="upload-btn" size="mini" @click="chooseAndUpload">＋ 上传照片</button>
    </view>

    <!-- 按月份分组 -->
    <block v-if="groups.length > 0">
      <view class="month" v-for="g in groups" :key="g.month">
        <text class="month-title">{{ g.month }}</text>
        <view class="grid">
          <view class="photo" v-for="p in g.items" :key="p.id" @longpress="delPhoto(p)">
            <image class="p-img" :src="imgUrl(p.url)" mode="aspectFill" />
            <text class="p-tag" :class="{ mine: p.user_id === myId }">{{ p.user_id === myId ? '我' : 'TA' }}</text>
          </view>
        </view>
      </view>
    </block>

    <view class="empty" v-else>
      <text class="empty-icon">📷</text>
      <text>还没有照片，上传第一张吧</text>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'
import store from '../../common/store.js'

export default {
  data() {
    return { photos: [], myId: 0 }
  },
  computed: {
    groups() {
      const map = {}
      this.photos.forEach(p => {
        const m = p.created_at ? p.created_at.slice(0, 7) : ''
        if (!map[m]) map[m] = { month: m.replace('-', ' 年 ') + ' 月', items: [] }
        map[m].items.push(p)
      })
      return Object.values(map)
    },
  },
  onShow() {
    applyTheme()
    const u = store.getUser()
    this.myId = u ? u.id : 0
    this.load()
  },
  methods: {
    async load() {
      const { ok, data } = await api.listAlbum()
      if (ok) this.photos = data
    },
    imgUrl(url) {
      if (!url) return ''
      if (url.startsWith('http')) return url
      return 'http://47.93.241.64:8000' + url
    },
    chooseAndUpload() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        success: async (res) => {
          uni.showLoading({ title: '上传中…' })
          const r = await api.uploadImage(res.tempFilePaths[0])
          if (!r.ok) { uni.hideLoading(); uni.showToast({ title: r.msg, icon: 'none' }); return }
          const a = await api.addAlbumPhoto({ url: r.url, caption: '' })
          uni.hideLoading()
          if (a.ok) { uni.showToast({ title: '已加入相册', icon: 'success' }); this.load() }
          else uni.showToast({ title: a.msg, icon: 'none' })
        },
      })
    },
    async delPhoto(p) {
      if (p.user_id !== this.myId) {
        uni.showToast({ title: '只能删除自己上传的照片', icon: 'none' })
        return
      }
      const { confirm } = await uni.showModal({ title: '删除照片', content: '确定删除这张照片吗？' })
      if (!confirm) return
      const { ok } = await api.deleteAlbumPhoto(p.id)
      if (ok) { uni.showToast({ title: '已删除', icon: 'success' }); this.load() }
    },
  },
}
</script>

<style scoped>
.page { padding: 20rpx 30rpx 80rpx; }

.topbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24rpx; }
.count { font-size: 26rpx; color: var(--muted); }
.upload-btn { background: linear-gradient(135deg, #f8a5c2, #ff6b9d); color: #fff; }

.month { margin-bottom: 30rpx; }
.month-title { display: block; font-size: 28rpx; font-weight: bold; color: var(--text); margin-bottom: 16rpx; }

.grid { display: flex; flex-wrap: wrap; gap: 12rpx; }
.photo {
  position: relative; width: calc((100% - 24rpx) / 3); aspect-ratio: 1;
  border-radius: 16rpx; overflow: hidden;
}
.p-img { width: 100%; height: 100%; }
.p-tag {
  position: absolute; top: 10rpx; left: 10rpx;
  background: rgba(0, 0, 0, 0.45); color: #fff; font-size: 20rpx;
  padding: 2rpx 12rpx; border-radius: 12rpx;
}
.p-tag.mine { background: rgba(255, 107, 157, 0.75); }

.empty { display: flex; flex-direction: column; align-items: center; padding-top: 220rpx; color: var(--muted); font-size: 28rpx; }
.empty-icon { font-size: 90rpx; margin-bottom: 20rpx; }
</style>
