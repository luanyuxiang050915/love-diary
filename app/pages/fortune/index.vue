<template>
  <view class="page" :style="cssVars">
    <!-- 夜景大图背景 -->
    <view class="bg-img"></view>
    <view class="bg-cover"></view>
    <view class="bg-vignette"></view>

    <!-- 漂浮星光 -->
    <view class="deco">
      <text class="deco-item d1">✦</text>
      <text class="deco-item d2">✧</text>
      <text class="deco-item d3">✦</text>
      <text class="deco-item d4">✧</text>
      <text class="deco-item d5">✦</text>
    </view>

    <!-- 标题 -->
    <view class="title-box">
      <text class="title-en">OMIKUJI · DAILY FORTUNE</text>
      <text class="title">每日一签</text>
      <text class="sub">摇一摇签筒，看看今天的好运气</text>
    </view>

    <!-- 摇签桶 -->
    <view class="stage" v-if="!result">
      <view class="bucket-wrap" :class="{ shaking: shaking }">
        <view class="bucket-glow"></view>
        <view class="sticks">
          <view
            class="stick"
            v-for="(s, i) in sticks"
            :key="i"
            :style="{ left: s.left + '%', height: s.h + 'rpx', transform: 'rotate(' + s.rot + 'deg)' }"
          ></view>
        </view>
        <view class="bucket">
          <view class="bucket-top"></view>
          <view class="bucket-band"></view>
          <view class="bucket-body">🏮</view>
        </view>
      </view>

      <view class="hint" v-if="!shaking && !drawn">
        <text class="hint-dot"></text>
        摇一摇签筒，看看今天的缘分签
      </view>
      <view class="hint" v-else-if="drawn && !result">
        <text class="hint-dot"></text>
        签掉出来啦，点一点打开它
      </view>

      <button class="btn" v-if="!shaking && !drawn" hover-class="btn-hover" @click="shake">🎋 摇一签</button>

      <!-- 掉出来的签 -->
      <view class="drawn-stick" v-if="drawn" @click="openStick">
        <view class="ds-inner" :class="{ open: result }">
          <view class="ds-front">
            <text class="ds-q">?</text>
            <text class="ds-tip">点开</text>
          </view>
          <view class="ds-back">
            <text class="ds-level">{{ picked.level || '' }}</text>
            <text class="ds-emoji">{{ picked.emoji || '' }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 签文卡片 -->
    <view class="fortune-card" v-if="result" :style="cardStyle">
      <view class="fc-deco fc-d1"></view>
      <view class="fc-deco fc-d2"></view>
      <view class="fc-seal">
        <text class="fc-emoji">{{ result.emoji }}</text>
      </view>
      <text class="fc-level">{{ result.level }}</text>
      <text class="fc-sub">今 日 缘 分 签</text>
      <view class="fc-lines">
        <view class="fc-line"><text class="fc-k">愿望</text><text class="fc-v">{{ result.wish }}</text></view>
        <view class="fc-line"><text class="fc-k">健康</text><text class="fc-v">{{ result.health }}</text></view>
        <view class="fc-line"><text class="fc-k">爱情</text><text class="fc-v">{{ result.love }}</text></view>
        <view class="fc-line"><text class="fc-k">学业</text><text class="fc-v">{{ result.study }}</text></view>
      </view>
      <view class="fc-quote" v-if="result.quote">「{{ result.quote }}」</view>
      <view class="fc-hint">✨ {{ result.hint }}</view>
      <view class="btn again disabled">今日已抽 · 明天再来 ✨</view>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'

// 深色夜景背景下的签级配色（亮色系）
const LEVEL_COLORS = {
  '大吉': { main: '#f3c96b', soft: 'rgba(243, 201, 107, 0.16)', glow: 'rgba(243, 201, 107, 0.38)' },
  '中吉': { main: '#f9a8d4', soft: 'rgba(249, 168, 212, 0.16)', glow: 'rgba(249, 168, 212, 0.32)' },
  '小吉': { main: '#5eead4', soft: 'rgba(94, 234, 212, 0.16)', glow: 'rgba(94, 234, 212, 0.3)' },
  '吉': { main: '#c4b5fd', soft: 'rgba(196, 181, 253, 0.16)', glow: 'rgba(196, 181, 253, 0.3)' },
  '半吉': { main: '#fcd34d', soft: 'rgba(252, 211, 77, 0.16)', glow: 'rgba(252, 211, 77, 0.3)' },
  '末吉': { main: '#94a3b8', soft: 'rgba(148, 163, 184, 0.16)', glow: 'rgba(148, 163, 184, 0.28)' },
  '末小吉': { main: '#93c5fd', soft: 'rgba(147, 197, 253, 0.16)', glow: 'rgba(147, 197, 253, 0.3)' },
  '凶': { main: '#cbd5e1', soft: 'rgba(203, 213, 225, 0.14)', glow: 'rgba(203, 213, 225, 0.25)' },
  '大凶': { main: '#94a3b8', soft: 'rgba(148, 163, 184, 0.14)', glow: 'rgba(148, 163, 184, 0.28)' },
}

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
  computed: {
    cardStyle() {
      const c = LEVEL_COLORS[(this.result && this.result.level) || '吉'] || LEVEL_COLORS['吉']
      return `--lv:${c.main};--lv-soft:${c.soft};--lv-glow:${c.glow};`
    },
  },
  onShow() { applyTheme(); this.init() },
  methods: {
    todayKey() {
      const t = new Date()
      return `fortune_${t.getFullYear()}-${t.getMonth() + 1}-${t.getDate()}`
    },
    async init() {
      // 随机摆几根签在桶里：红头竹签，角度微微错开
      this.sticks = Array.from({ length: 7 }, (_, i) => ({
        left: 14 + i * 11,
        h: 44 + Math.random() * 16,
        rot: -7 + Math.random() * 14,
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
  padding: 60rpx 30rpx 80rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow: hidden;
}

/* ---------- 背景图层 ---------- */
.bg-img {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background-image: url('/static/fortune-night.jpg');
  background-size: cover;
  background-position: 50% 14%;
  background-repeat: no-repeat;
  z-index: 0;
}
.bg-cover {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(180deg, rgba(8, 6, 18, 0.30) 0%, rgba(8, 6, 18, 0.18) 45%, rgba(8, 6, 18, 0.62) 100%);
  z-index: 1;
}
.bg-vignette {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(ellipse at 50% 36%, rgba(255, 214, 150, 0.14) 0%, transparent 40%, rgba(6, 5, 14, 0.5) 100%);
  z-index: 1;
}

/* ---------- 漂浮星光 ---------- */
.deco { position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 2; pointer-events: none; overflow: hidden; }
.deco-item { position: absolute; color: rgba(255, 236, 190, 0.55); animation: floatUp 8s ease-in-out infinite; }
.d1 { left: 8%; top: 20%; font-size: 34rpx; }
.d2 { left: 84%; top: 15%; font-size: 28rpx; animation-delay: 1.4s; }
.d3 { left: 14%; top: 64%; font-size: 26rpx; animation-delay: 2.6s; }
.d4 { left: 76%; top: 66%; font-size: 32rpx; animation-delay: 3.8s; }
.d5 { left: 46%; top: 9%; font-size: 24rpx; animation-delay: 0.8s; }
@keyframes floatUp {
  0%, 100% { transform: translateY(0) rotate(0); opacity: 0.45; }
  50% { transform: translateY(-26rpx) rotate(12deg); opacity: 0.9; }
}

/* ---------- 标题 ---------- */
.title-box { position: relative; z-index: 3; text-align: center; margin-top: 6rpx; }
.title-en {
  display: block;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 20rpx;
  letter-spacing: 6rpx;
  color: rgba(236, 214, 168, 0.7);
}
.title {
  display: block;
  margin-top: 12rpx;
  font-size: 52rpx;
  font-weight: bold;
  letter-spacing: 12rpx;
  color: #f6ecd8;
  text-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.45);
}
.sub {
  display: block;
  margin-top: 14rpx;
  font-size: 24rpx;
  letter-spacing: 3rpx;
  color: rgba(246, 236, 216, 0.66);
}

/* ---------- 签筒 ---------- */
.stage { position: relative; z-index: 3; width: 100%; display: flex; flex-direction: column; align-items: center; margin-top: 56rpx; }

.bucket-wrap { position: relative; width: 340rpx; height: 330rpx; }
.bucket-wrap.shaking { animation: bucketShake 0.95s ease-in-out; }
@keyframes bucketShake {
  0%, 100% { transform: rotate(0); }
  20% { transform: rotate(-12deg); }
  40% { transform: rotate(10deg); }
  60% { transform: rotate(-8deg); }
  80% { transform: rotate(6deg); }
}

.bucket-glow {
  position: absolute; left: 50%; bottom: -14rpx; transform: translateX(-50%);
  width: 280rpx; height: 56rpx; border-radius: 50%;
  background: radial-gradient(closest-side, rgba(255, 214, 140, 0.34), transparent);
  filter: blur(6rpx);
}

.sticks { position: absolute; top: 0; left: 0; width: 100%; height: 240rpx; z-index: 5; }
.stick {
  position: absolute; bottom: 0; width: 14rpx;
  border-radius: 7rpx 7rpx 3rpx 3rpx;
  background: linear-gradient(180deg, #d94f4f 0%, #d94f4f 22rpx, #f7e6bd 22rpx, #edcf96 100%);
  box-shadow: 0 4rpx 8rpx rgba(0, 0, 0, 0.35);
  transform-origin: bottom center;
}
.bucket-wrap.shaking .stick { animation: stickWobble 0.95s ease-in-out; }
@keyframes stickWobble {
  0%, 100% { margin-left: 0; }
  25% { margin-left: -8rpx; }
  50% { margin-left: 6rpx; }
  75% { margin-left: -4rpx; }
}

.bucket { position: absolute; left: 50%; bottom: 0; transform: translateX(-50%); width: 260rpx; z-index: 4; }
.bucket-top {
  width: 260rpx; height: 48rpx;
  background: linear-gradient(180deg, #d5a269, #b07a4b);
  border: 4rpx solid #e3bd7d;
  box-sizing: border-box;
  border-radius: 50%;
  box-shadow: inset 0 4rpx 8rpx rgba(0, 0, 0, 0.25), 0 6rpx 18rpx rgba(0, 0, 0, 0.4);
}
.bucket-band {
  width: 268rpx; height: 26rpx; margin: -6rpx auto 0;
  background: linear-gradient(180deg, #d84f4f, #b83a3a);
  border-radius: 8rpx;
  box-shadow: 0 4rpx 10rpx rgba(0, 0, 0, 0.3);
}
.bucket-body {
  width: 216rpx; height: 150rpx; margin: -6rpx auto 0;
  background: linear-gradient(160deg, #c08a5e, #96613a);
  border-radius: 10rpx 10rpx 70rpx 70rpx;
  display: flex; align-items: flex-end; justify-content: center;
  font-size: 40rpx; padding-bottom: 16rpx;
  box-shadow: inset -14rpx 0 24rpx rgba(0, 0, 0, 0.25), 0 14rpx 34rpx rgba(0, 0, 0, 0.4);
}

/* ---------- 提示与按钮 ---------- */
.hint {
  display: flex; align-items: center; margin-top: 30rpx;
  font-size: 26rpx; color: rgba(246, 236, 216, 0.8);
  text-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.5);
}
.hint-dot {
  width: 12rpx; height: 12rpx; border-radius: 50%;
  background: #f3c96b; margin-right: 12rpx;
  box-shadow: 0 0 14rpx #f3c96b;
}
.btn {
  margin-top: 34rpx;
  background: linear-gradient(135deg, #f0cf8f, #d3a654);
  color: #2e2410;
  border-radius: 44rpx;
  font-size: 30rpx;
  font-weight: bold;
  letter-spacing: 4rpx;
  padding: 0 66rpx;
  line-height: 90rpx; height: 90rpx;
  box-shadow: 0 12rpx 36rpx rgba(240, 207, 143, 0.32);
}
.btn-hover { transform: scale(0.96); opacity: 0.92; }
.btn.again {
  margin-top: 40rpx; font-size: 26rpx; line-height: 72rpx; height: 72rpx; padding: 0 40rpx;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(246, 236, 216, 0.55);
  box-shadow: none;
  border: 1rpx solid rgba(255, 255, 255, 0.14);
}

/* ---------- 掉出来的签 ---------- */
.drawn-stick { margin-top: 48rpx; perspective: 800rpx; }
.ds-inner {
  position: relative; width: 150rpx; height: 380rpx; transform-style: preserve-3d;
  transition: transform 0.7s cubic-bezier(0.25, 0.8, 0.25, 1.2);
  animation: stickDrop 0.7s cubic-bezier(0.2, 0.9, 0.3, 1.2);
}
@keyframes stickDrop {
  0% { transform: translateY(-180rpx) rotate(-12deg); opacity: 0; }
  60% { transform: translateY(14rpx) rotate(4deg); opacity: 1; }
  100% { transform: translateY(0) rotate(0); }
}
.ds-inner.open { transform: rotateY(180deg); }
.ds-front, .ds-back {
  position: absolute; inset: 0; backface-visibility: hidden; border-radius: 26rpx;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.ds-front {
  background: linear-gradient(160deg, #d94f4f 0%, #b83939 26%, #f7e6bd 26%, #e8c88d 100%);
  box-shadow: 0 16rpx 44rpx rgba(0, 0, 0, 0.45);
}
.ds-q { font-size: 76rpx; font-weight: bold; color: #fff; text-shadow: 0 4rpx 14rpx rgba(0, 0, 0, 0.35); }
.ds-tip {
  position: absolute; bottom: 26rpx;
  font-size: 22rpx; color: #9c3131; background: #f7e6bd;
  padding: 2rpx 18rpx; border-radius: 16rpx;
}
.ds-back {
  background: rgba(24, 19, 40, 0.92);
  border: 2rpx solid rgba(255, 255, 255, 0.22);
  transform: rotateY(180deg);
  box-shadow: 0 16rpx 44rpx rgba(0, 0, 0, 0.4);
}
.ds-level { font-size: 60rpx; font-weight: bold; color: #f3c96b; letter-spacing: 4rpx; }
.ds-emoji { font-size: 44rpx; margin-top: 12rpx; }

/* ---------- 签文卡片（玻璃拟态） ---------- */
.fortune-card {
  position: relative;
  z-index: 3;
  width: 100%;
  background: rgba(18, 14, 32, 0.82);
  backdrop-filter: blur(18rpx);
  -webkit-backdrop-filter: blur(18rpx);
  border: 1rpx solid rgba(255, 255, 255, 0.14);
  border-radius: 32rpx;
  padding: 52rpx 36rpx 42rpx;
  margin-top: 52rpx;
  text-align: center;
  box-shadow: 0 24rpx 70rpx rgba(0, 0, 0, 0.45), 0 0 0 10rpx var(--lv-soft);
  animation: cardIn 0.6s ease;
  overflow: hidden;
}
@keyframes cardIn { from { transform: translateY(30rpx) scale(0.94); opacity: 0; } to { transform: none; opacity: 1; } }
.fc-deco {
  position: absolute; width: 190rpx; height: 190rpx; border-radius: 50%;
  background: var(--lv-soft); pointer-events: none;
}
.fc-d1 { top: -80rpx; right: -70rpx; }
.fc-d2 { bottom: -90rpx; left: -70rpx; }
.fc-seal {
  position: relative;
  width: 136rpx; height: 136rpx; margin: 0 auto 22rpx;
  border-radius: 50%;
  background: linear-gradient(160deg, var(--lv), rgba(255, 255, 255, 0.18));
  border: 5rpx solid rgba(255, 255, 255, 0.85);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 12rpx 34rpx var(--lv-glow);
}
.fc-emoji { font-size: 66rpx; }
.fc-level { display: block; font-size: 58rpx; font-weight: bold; color: var(--lv); letter-spacing: 8rpx; text-shadow: 0 0 24rpx var(--lv-glow); }
.fc-sub { display: block; font-size: 24rpx; color: rgba(246, 236, 216, 0.55); margin-top: 10rpx; letter-spacing: 8rpx; }
.fc-lines { margin-top: 36rpx; }
.fc-line { display: flex; align-items: center; padding: 18rpx 0; border-bottom: 1rpx solid rgba(255, 255, 255, 0.08); }
.fc-line:last-child { border-bottom: none; }
.fc-k { width: 110rpx; font-size: 26rpx; color: rgba(246, 236, 216, 0.55); text-align: left; letter-spacing: 2rpx; }
.fc-v { flex: 1; font-size: 28rpx; color: #f6ecd8; text-align: right; }
.fc-quote {
  margin-top: 30rpx;
  padding: 24rpx 26rpx;
  background: var(--lv-soft);
  border-left: 6rpx solid var(--lv);
  border-radius: 12rpx;
  font-size: 27rpx;
  color: #f0e7d2;
  line-height: 1.9;
  text-align: left;
}
.fc-hint { margin-top: 30rpx; font-size: 26rpx; color: var(--lv); line-height: 1.7; text-shadow: 0 0 18rpx var(--lv-glow); }
</style>
