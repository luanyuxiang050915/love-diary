<template>
  <view class="page" :style="cssVars">
    <!-- 顶部 -->
    <view class="hero">
      <text class="hero-title">恋爱互动</text>
      <text class="hero-sub">属于我们俩的小天地</text>
    </view>

    <!-- 功能卡片 -->
    <view class="grid">
      <view class="card" v-for="c in cards" :key="c.key" :class="{ wide: c.wide }" @click="go(c.url)">
        <view class="card-emoji">{{ c.emoji }}</view>
        <view class="card-main">
          <view class="card-title-row">
            <text class="card-title">{{ c.title }}</text>
            <text class="badge" v-if="c.badge > 0">{{ c.badge > 99 ? '99+' : c.badge }}</text>
          </view>
          <text class="card-desc">{{ c.desc }}</text>
        </view>
        <text class="card-arrow">›</text>
      </view>
    </view>

    <view class="footer-tip">戳一戳对方，TA 会第一时间看到</view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'

export default {
  data() {
    return {
      pokeUnread: 0,
    }
  },
  computed: {
    cards() {
      return [
        { key: 'poke', emoji: '💓', title: '戳一戳', desc: '让对方知道你在想 TA', url: '/pages/poke/index', badge: this.pokeUnread },
        { key: 'wish', emoji: '✅', title: '心愿清单', desc: '写下想一起做的事', url: '/pages/wish/list' },
        { key: 'checkin', emoji: '🔥', title: '爱的打卡', desc: '记录我们的坚持', url: '/pages/checkin/index' },
        { key: 'whisper', emoji: '💌', title: '悄悄话', desc: '留言给 TA 的心里话', url: '/pages/whisper/list' },
        { key: 'mood', emoji: '📊', title: '心情月报', desc: '看看这个月的心情变化', url: '/pages/stats/mood', wide: true },
        { key: 'chat', emoji: '💬', title: '双人聊天', desc: '实时聊天 · 基础表情 + 自定义表情包', url: '/pages/chat/index' },
        { key: 'album', emoji: '📷', title: '共享相册', desc: '两个人的照片墙，按月归档', url: '/pages/album/index' },
        { key: 'calendar', emoji: '📅', title: '纪念日日历', desc: '不同纪念日用不同颜色标记', url: '/pages/calendar/index' },
        { key: 'fortune', emoji: '🎋', title: '每日一签', desc: '摇一摇签筒，看看今天的缘分签', url: '/pages/fortune/index', wide: true },
      ]
    },
  },
  onShow() { applyTheme();
    this.loadPokeUnread()
  },
  methods: {
    async loadPokeUnread() {
      const { ok, data } = await api.getPokeUnread()
      if (ok) this.pokeUnread = data.unread
    },
    go(url) {
      uni.navigateTo({ url })
    },
  },
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(180deg, var(--pink-soft) 0%, var(--bg) 280rpx);
  padding-bottom: 60rpx;
}

.hero {
  padding: 60rpx 40rpx 40rpx;
}

.hero-title {
  display: block;
  font-size: 46rpx;
  font-weight: bold;
  color: var(--text);
}

.hero-sub {
  display: block;
  font-size: 26rpx;
  color: var(--muted);
  margin-top: 10rpx;
}

.grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  padding: 0 30rpx;
}

.card {
  width: 330rpx;
  background: var(--card);
  border-radius: 24rpx;
  padding: 30rpx 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 28rpx rgba(248, 165, 194, 0.16);
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.card.wide {
  width: 100%;
}

.card-emoji {
  font-size: 52rpx;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.card-main {
  flex: 1;
  min-width: 0;
}

.card-title-row {
  display: flex;
  align-items: center;
}

.card-title {
  font-size: 30rpx;
  font-weight: bold;
  color: var(--text);
}

.card-desc {
  display: block;
  font-size: 22rpx;
  color: var(--muted);
  margin-top: 6rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-arrow {
  color: var(--muted);
  font-size: 36rpx;
  margin-left: 10rpx;
  flex-shrink: 0;
}

.badge {
  min-width: 32rpx;
  height: 32rpx;
  border-radius: 16rpx;
  text-align: center;
  line-height: 32rpx;
  background: var(--hot);
  color: #fff;
  font-size: 20rpx;
  padding: 0 8rpx;
  margin-left: 12rpx;
  box-sizing: border-box;
}

.footer-tip {
  text-align: center;
  font-size: 22rpx;
  color: var(--muted);
  margin-top: 20rpx;
}
</style>
