<template>
  <view class="page" :style="cssVars">
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
          <view class="photo" v-for="p in g.items" :key="p.id" @click="showPhoto(p)" @longpress="delPhoto(p)">
            <image class="p-img" :src="imgUrl(p.url)" mode="aspectFill" />
            <text class="p-tag" :class="{ mine: p.user_id === myId }">{{ p.user_id === myId ? '我' : 'TA' }}</text>
            <view class="p-caption" v-if="p.caption">{{ p.caption }}</view>
          </view>
        </view>
      </view>
    </block>

    <view class="empty" v-else>
      <text class="empty-icon">📷</text>
      <text>还没有照片，上传第一张吧</text>
    </view>

    <!-- 照片详情 -->
    <view class="mask" v-if="detail" @click="detail = null">
      <view class="viewer" @click.stop>
        <image class="v-img" :src="imgUrl(detail.url)" mode="aspectFit" />
        <view class="v-info">
          <text class="v-caption">{{ detail.caption || '这张照片还没有备注' }}</text>
          <text class="v-meta">{{ detail.nickname }} · {{ fmtTime(detail.created_at) }}</text>
        </view>
        <text class="v-close" @click="detail = null">✕</text>
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
    return { photos: [], myId: 0, detail: null }
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
    fmtTime(iso) {
      if (!iso) return ''
      return iso.slice(0, 16).replace('T', ' ')
    },
    chooseAndUpload() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        success: async (res) => {
          const filePath = res.tempFilePaths[0]
          let caption = ''
          try {
            const m = await uni.showModal({
              title: '照片备注',
              editable: true,
              placeholderText: '给这张照片写句备注（可不填）',
            })
            if (!m.confirm) return
            caption = (m.content || '').trim()
          } catch (e) {
            caption = ''
          }
          uni.showLoading({ title: '上传中…' })
          const r = await api.uploadImage(filePath)
          if (!r.ok) { uni.hideLoading(); uni.showToast({ title: r.msg, icon: 'none' }); return }
          const a = await api.addAlbumPhoto({ url: r.url, caption })
          uni.hideLoading()
          if (a.ok) { uni.showToast({ title: '已加入相册', icon: 'success' }); this.load() }
          else uni.showToast({ title: a.msg, icon: 'none' })
        },
      })
    },
    showPhoto(p) {
      this.detail = p
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
.upload-btn { background: linear-gradient(135deg, var(--pink), var(--hot)); color: #fff; }

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
.p-caption {
  position: absolute; left: 0; right: 0; bottom: 0;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.55));
  color: #fff; font-size: 20rpx;
  padding: 24rpx 10rpx 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ---------- 照片详情 ---------- */
.mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.78);
  display: flex; align-items: center; justify-content: center;
  z-index: 999;
}
.viewer {
  width: 86%;
  max-height: 82vh;
  background: var(--card);
  border-radius: 24rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  position: relative;
}
.v-img {
  width: 100%;
  height: 62vh;
  background: #000;
  border-radius: 16rpx;
}
.v-info {
  padding: 22rpx 6rpx 6rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.v-caption { font-size: 30rpx; color: var(--text); line-height: 1.6; text-align: center; }
.v-meta { font-size: 24rpx; color: var(--muted); margin-top: 10rpx; }
.v-close {
  position: absolute; top: 18rpx; right: 18rpx;
  width: 56rpx; height: 56rpx; border-radius: 50%;
  background: rgba(0, 0, 0, 0.45); color: #fff;
  font-size: 32rpx; line-height: 56rpx; text-align: center;
}

.empty { display: flex; flex-direction: column; align-items: center; padding-top: 220rpx; color: var(--muted); font-size: 28rpx; }
.empty-icon { font-size: 90rpx; margin-bottom: 20rpx; }
</style>
