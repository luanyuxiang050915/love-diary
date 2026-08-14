<template>
  <view class="page" :style="cssVars">
    <!-- 摇签桶 -->
    <view class="stage" v-if="!result">
      <view class="bucket-wrap" :class="{ shaking: shaking }">
        <view class="sticks">
          <view class="stick" v-for="(s, i) in sticks" :key="i" :style="{ left: s.left + '%', height: s.h + 'rpx', background: s.color }"></view>
        </view>
        <view class="bucket">
          <view class="bucket-top"></view>
          <view class="bucket-body">🪄</view>
        </view>
      </view>

      <text class="hint" v-if="!shaking && !drawn">摇一摇签筒，看看今天的缘分签</text>
      <text class="hint" v-if="drawn && !result">签掉出来啦，点一点打开它</text>

      <button class="btn" v-if="!shaking && !drawn" @click="shake">🎋 摇一签</button>

      <!-- 掉出来的签 -->
      <view class="drawn-stick" v-if="drawn" @click="openStick">
        <view class="ds-inner" :class="{ open: result }">
          <view class="ds-front"><text>?</text></view>
          <view class="ds-back"><text class="ds-level">{{ picked.level }}</text><text class="ds-emoji">{{ picked.emoji }}</text></view>
        </view>
      </view>
    </view>

    <!-- 签文 -->
    <view class="fortune-card" v-if="result">
      <view class="fc-head">
        <text class="fc-emoji">{{ result.emoji }}</text>
        <text class="fc-level">{{ result.level }}</text>
        <text class="fc-sub">今日缘分签</text>
      </view>
      <view class="fc-lines">
        <view class="fc-line"><text class="fc-k">愿望</text><text class="fc-v">{{ result.wish }}</text></view>
        <view class="fc-line"><text class="fc-k">健康</text><text class="fc-v">{{ result.health }}</text></view>
        <view class="fc-line"><text class="fc-k">爱情</text><text class="fc-v">{{ result.love }}</text></view>
        <view class="fc-line"><text class="fc-k">学业</text><text class="fc-v">{{ result.study }}</text></view>
      </view>
      <view class="fc-hint">✨ {{ result.hint }}</view>
      <view class="btn again disabled">今日已抽 · 明天再来 ✨</view>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'

const STICK_COLORS = ['#f8a5c2', '#ff6b9d', '#c44dff', '#f59e0b', '#10b981', '#3b82f6']

export default {
  data() {
    return {
      sticks: [],
      shaking: false,
      drawn: false,
      result: null,
      picked: {},
    }
  },
  onShow() { applyTheme(); this.init() },
  methods: {
    todayKey() {
      const t = new Date()
      return `fortune_${t.getFullYear()}-${t.getMonth() + 1}-${t.getDate()}`
    },
    async init() {
      // 随机摆几根签在桶里
      this.sticks = Array.from({ length: 6 }, (_, i) => ({
        left: 18 + i * 12,
        h: 42 + Math.random() * 14,
        color: STICK_COLORS[i % STICK_COLORS.length],
      }))

      // 先问服务器今天有没有抽过：抽过直接展示，没抽过才显示签筒
      const { ok, data } = await api.getTodayFortune()
      if (ok && data) {
        this.result = data
        this.picked = data
        this.drawn = true
        uni.setStorageSync(this.todayKey(), JSON.stringify(data))
      } else if (!ok) {
        // 网络异常时退回本地缓存（仅作展示兜底，是否可抽仍以服务器为准）
        const saved = uni.getStorageSync(this.todayKey())
        if (saved) {
          this.result = JSON.parse(saved)
          this.picked = this.result
          this.drawn = true
        }
      }
    },
    shake() {
      this.shaking = true
      setTimeout(() => {
        this.shaking = false
        this.drawn = true
        this.picked = {}
      }, 950)
    },
    async openStick() {
      if (this.shaking) return
      const { ok, data, msg } = await api.drawFortune()
      if (!ok) {
        uni.showToast({ title: msg || '抽签失败，请重试', icon: 'none' })
        return
      }
      this.picked = data
      this.result = data
      uni.setStorageSync(this.todayKey(), JSON.stringify(data))
    },
  },
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(180deg, var(--pink-soft) 0%, var(--bg) 300rpx);
  padding: 40rpx 30rpx 80rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stage { width: 100%; display: flex; flex-direction: column; align-items: center; margin-top: 30rpx; }

.bucket-wrap { position: relative; width: 320rpx; height: 300rpx; }
.bucket-wrap.shaking { animation: bucketShake .95s ease-in-out; }
@keyframes bucketShake {
  0%, 100% { transform: rotate(0); }
  20% { transform: rotate(-10deg); }
  40% { transform: rotate(9deg); }
  60% { transform: rotate(-7deg); }
  80% { transform: rotate(5deg); }
}

.sticks { position: absolute; top: 0; left: 0; width: 100%; height: 210rpx; }
.stick {
  position: absolute; bottom: 0; width: 12rpx; border-radius: 6rpx 6rpx 2rpx 2rpx;
  transform: rotate(8deg);
}

.bucket { position: absolute; left: 50%; bottom: 0; transform: translateX(-50%); width: 250rpx; height: 150rpx; }
.bucket-top {
  width: 250rpx; height: 40rpx; background: linear-gradient(135deg, var(--pink), var(--hot));
  border-radius: 50%; box-shadow: 0 6rpx 20rpx rgba(255, 107, 157, 0.35);
}
.bucket-body {
  width: 210rpx; height: 120rpx; margin: -8rpx auto 0;
  background: linear-gradient(160deg, var(--pink), var(--hot));
  border-radius: 8rpx 8rpx 60rpx 60rpx;
  display: flex; align-items: flex-end; justify-content: center;
  font-size: 34rpx; padding-bottom: 16rpx;
}

.hint { margin-top: 20rpx; font-size: 26rpx; color: var(--muted); }
.btn {
  margin-top: 30rpx; background: linear-gradient(135deg, var(--pink), var(--hot)); color: #fff;
  border-radius: 40rpx; font-size: 30rpx; padding: 0 60rpx; line-height: 84rpx; height: 84rpx;
  box-shadow: 0 10rpx 30rpx rgba(255, 107, 157, 0.35);
}
.btn.again {
  margin-top: 40rpx; font-size: 26rpx; line-height: 72rpx; height: 72rpx; padding: 0 40rpx;
  background: var(--input-bg); color: var(--muted);
  box-shadow: none;
}

/* 掉出来的签 */
.drawn-stick { margin-top: 40rpx; perspective: 800rpx; }
.ds-inner {
  position: relative; width: 150rpx; height: 360rpx; transform-style: preserve-3d;
  transition: transform .7s cubic-bezier(.25,.8,.25,1.2);
  animation: stickDrop .7s cubic-bezier(.2,.9,.3,1.2);
}
@keyframes stickDrop {
  0% { transform: translateY(-180rpx) rotate(-12deg); opacity: 0; }
  60% { transform: translateY(14rpx) rotate(4deg); opacity: 1; }
  100% { transform: translateY(0) rotate(0); }
}
.ds-inner.open { transform: rotateY(180deg); }
.ds-front, .ds-back {
  position: absolute; inset: 0; backface-visibility: hidden; border-radius: 24rpx;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.ds-front {
  background: linear-gradient(160deg, var(--pink), var(--hot)); color: #fff; font-size: 80rpx; font-weight: bold;
  box-shadow: 0 14rpx 40rpx rgba(255, 107, 157, 0.4);
}
.ds-back {
  background: var(--card); border: 3rpx solid var(--pink); transform: rotateY(180deg);
}
.ds-level { font-size: 60rpx; font-weight: bold; color: var(--pink); }
.ds-emoji { font-size: 44rpx; margin-top: 10rpx; }

/* 签文卡片 */
.fortune-card {
  width: 100%; background: var(--card); border-radius: 28rpx;
  padding: 50rpx 36rpx; margin-top: 40rpx; text-align: center;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.08);
  animation: cardIn .6s ease;
}
@keyframes cardIn { from { transform: translateY(30rpx) scale(.94); opacity: 0; } to { transform: none; opacity: 1; } }
.fc-emoji { font-size: 80rpx; display: block; }
.fc-level { display: block; font-size: 64rpx; font-weight: bold; color: var(--pink); margin-top: 12rpx; }
.fc-sub { display: block; font-size: 24rpx; color: var(--muted); margin-top: 8rpx; letter-spacing: 4rpx; }
.fc-lines { margin-top: 36rpx; }
.fc-line { display: flex; align-items: center; padding: 18rpx 0; border-bottom: 1rpx solid var(--border); }
.fc-line:last-child { border-bottom: none; }
.fc-k { width: 110rpx; font-size: 26rpx; color: var(--muted); text-align: left; }
.fc-v { flex: 1; font-size: 28rpx; color: var(--text); text-align: right; }
.fc-hint { margin-top: 28rpx; font-size: 26rpx; color: var(--pink); line-height: 1.7; }
</style>
