<template>
  <view class="page">
    <!-- 留言列表 -->
    <scroll-view class="list" scroll-y :scroll-into-view="scrollInto">
      <view class="tip" v-if="whispers.length === 0">留一句悄悄话，TA 打开就能看到 💌</view>
      <view class="w-item" v-for="w in whispers" :key="w.id" :id="'w' + w.id">
        <view class="w-head">
          <text class="w-name">{{ w.nickname }}</text>
          <text class="w-time">{{ fmtTime(w.created_at) }}</text>
        </view>
        <view class="w-content">{{ w.content }}</view>
      </view>
    </scroll-view>

    <!-- 输入栏 -->
    <view class="input-bar">
      <input class="w-input" v-model="content" placeholder="写一句悄悄话…" confirm-type="send" @confirm="send" />
      <button class="send-btn" size="mini" @click="send">发送</button>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'

export default {
  data() {
    return { whispers: [], content: '', scrollInto: '' }
  },
  onShow() { this.load() },
  methods: {
    async load() {
      const { ok, data } = await api.listWhispers()
      if (!ok) return
      this.whispers = data
      if (data.length) this.scrollInto = 'w' + data[0].id
    },
    async send() {
      const content = this.content.trim()
      if (!content) return uni.showToast({ title: '写点什么吧', icon: 'none' })
      const { ok, msg } = await api.sendWhisper(content)
      if (ok) { this.content = ''; this.load() }
      else uni.showToast({ title: msg, icon: 'none' })
    },
    fmtTime(s) { return s ? s.slice(5, 16) : '' },
  },
}
</script>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; }
.list { flex: 1; padding: 20rpx 30rpx 160rpx; box-sizing: border-box; }
.tip { text-align: center; color: #bbb; font-size: 26rpx; padding-top: 120rpx; }
.w-item { background: #fff; border-radius: 20rpx; padding: 24rpx; margin-bottom: 20rpx; }
.w-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10rpx; }
.w-name { font-size: 24rpx; color: #f8a5c2; font-weight: bold; }
.w-time { font-size: 20rpx; color: #bbb; }
.w-content { font-size: 30rpx; color: #333; line-height: 1.7; word-break: break-all; }
.input-bar {
  position: fixed; left: 0; right: 0; bottom: 0; z-index: 10;
  display: flex; align-items: center; padding: 16rpx 30rpx calc(16rpx + env(safe-area-inset-bottom));
  background: #fff; border-top: 1rpx solid #f0f0f0;
}
.w-input { flex: 1; background: #f5f5f5; border-radius: 36rpx; padding: 14rpx 26rpx; font-size: 28rpx; margin-right: 16rpx; }
.send-btn { background: linear-gradient(135deg, #f8a5c2, #ff6b9d); color: #fff; border-radius: 36rpx; padding: 0 34rpx; }
</style>
