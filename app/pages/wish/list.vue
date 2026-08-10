<template>
  <view class="page">
    <!-- 进度 -->
    <view class="progress-card">
      <text class="p-emoji">✨</text>
      <view class="p-main">
        <text class="p-title">一起实现的心愿</text>
        <text class="p-sub">已完成 {{ doneCount }} / {{ wishes.length }} 个</text>
      </view>
      <view class="p-bar"><view class="p-fill" :style="{ width: percent + '%' }"></view></view>
    </view>

    <!-- 添加 -->
    <view class="add-row">
      <input class="add-input" v-model="content" placeholder="写下想一起做的事…" confirm-type="done" @confirm="add" />
      <button class="add-btn" size="mini" @click="add">添加</button>
    </view>

    <!-- 列表 -->
    <view class="section">
      <block v-if="wishes.length > 0">
        <view class="wish-item" v-for="w in wishes" :key="w.id" :class="{ done: w.done }">
          <view class="check" @click="toggle(w)">
            <text>{{ w.done ? '✓' : '' }}</text>
          </view>
          <view class="w-main" @click="toggle(w)">
            <text class="w-content">{{ w.content }}</text>
            <text class="w-owner">{{ w.nickname }} 的心愿</text>
          </view>
          <text class="w-del" @click="remove(w)">✕</text>
        </view>
      </block>
      <view class="empty" v-else>还没有心愿，先写一个吧 🌟</view>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'

export default {
  data() {
    return { wishes: [], content: '' }
  },
  computed: {
    doneCount() { return this.wishes.filter(w => w.done).length },
    percent() { return this.wishes.length ? Math.round(this.doneCount / this.wishes.length * 100) : 0 },
  },
  onShow() { applyTheme(); this.load() },
  methods: {
    async load() {
      const { ok, data } = await api.listWishes()
      if (ok) this.wishes = data
    },
    async add() {
      const content = this.content.trim()
      if (!content) return uni.showToast({ title: '先写个心愿吧', icon: 'none' })
      const { ok, msg } = await api.createWish(content)
      if (ok) { this.content = ''; this.load() }
      else uni.showToast({ title: msg, icon: 'none' })
    },
    async toggle(w) {
      const { ok } = await api.toggleWish(w.id)
      if (ok) this.load()
    },
    async remove(w) {
      const { confirm } = await uni.showModal({ title: '删除心愿', content: '确定要删除这个心愿吗？' })
      if (!confirm) return
      const { ok } = await api.deleteWish(w.id)
      if (ok) this.load()
    },
  },
}
</script>

<style scoped>
.page { padding-bottom: 80rpx; }
.progress-card {
  background: linear-gradient(135deg, var(--pink-soft), var(--purple-soft));
  border-radius: 24rpx; margin: 30rpx; padding: 30rpx;
  display: flex; align-items: center; flex-wrap: wrap;
}
.p-emoji { font-size: 60rpx; margin-right: 20rpx; }
.p-main { flex: 1; }
.p-title { display: block; font-size: 32rpx; font-weight: bold; color: var(--text); }
.p-sub { display: block; font-size: 24rpx; color: var(--muted); margin-top: 6rpx; }
.p-bar { width: 100%; height: 14rpx; background: rgba(255,255,255,.8); border-radius: 8rpx; margin-top: 20rpx; overflow: hidden; }
.p-fill { height: 100%; background: linear-gradient(90deg, #f8a5c2, #c44dff); border-radius: 8rpx; transition: width .4s; }
.add-row { display: flex; align-items: center; margin: 0 30rpx 24rpx; background: var(--card); border-radius: 16rpx; padding: 12rpx 20rpx; }
.add-input { flex: 1; font-size: 28rpx; }
.add-btn { background: linear-gradient(135deg, #f8a5c2, #ff6b9d); color: #fff; }
.section { background: var(--card); border-radius: 24rpx; margin: 0 30rpx; padding: 10rpx 30rpx; }
.wish-item { display: flex; align-items: center; padding: 24rpx 0; border-bottom: 1rpx solid var(--border); }
.wish-item:last-child { border-bottom: none; }
.wish-item.done .w-content { text-decoration: line-through; color: var(--muted); }
.check {
  width: 44rpx; height: 44rpx; border-radius: 50%; border: 3rpx solid var(--border);
  display: flex; align-items: center; justify-content: center; margin-right: 20rpx;
  color: #fff; font-size: 26rpx; flex-shrink: 0;
}
.wish-item.done .check { background: linear-gradient(135deg, #4ade80, #22c55e); border-color: transparent; }
.w-main { flex: 1; }
.w-content { display: block; font-size: 30rpx; color: var(--text); }
.w-owner { display: block; font-size: 22rpx; color: var(--muted); margin-top: 4rpx; }
.w-del { color: var(--muted); font-size: 28rpx; padding: 8rpx; }
.empty { text-align: center; color: var(--muted); font-size: 26rpx; padding: 50rpx 0; }
</style>
