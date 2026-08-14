<template>
  <view class="page" :style="cssVars">
    <!-- 漂浮装饰 -->
    <view class="deco">
      <text class="deco-item d1">✨</text>
      <text class="deco-item d2">💖</text>
      <text class="deco-item d3">🌙</text>
      <text class="deco-item d4">💫</text>
      <text class="deco-item d5">🌸</text>
    </view>

    <!-- 标题 -->
    <view class="title-box">
      <text class="title">🎋 每日一签</text>
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

// 每种签级的主色 / 浅色 / 光晕（用于签文卡片配色）
const LEVEL_COLORS = {
  '大吉': { main: '#e6a23c', soft: '#fdf3e2', glow: 'rgba(230, 162, 60, 0.35)' },
  '中吉': { main: '#f472b6', soft: '#fdf0f6', glow: 'rgba(244, 114, 182, 0.32)' },
  '小吉': { main: '#10b981', soft: '#e8faf2', glow: 'rgba(16, 185, 129, 0.3)' },
  '吉': { main: '#8b5cf6', soft: '#f3ecff', glow: 'rgba(139, 92, 246, 0.3)' },
  '半吉': { main: '#f59e0b', soft: '#fef3e2', glow: 'rgba(245, 158, 11, 0.3)' },
  '末吉': { main: '#64748b', soft: '#eef1f5', glow: 'rgba(100, 116, 139, 0.28)' },
  '末小吉': { main: '#3b82f6', soft: '#eaf2ff', glow: 'rgba(59, 130, 246, 0.3)' },
  '凶': { main: '#475569', soft: '#e8ecf1', glow: 'rgba(71, 85, 105, 0.28)' },
  '大凶': { main: '#334155', soft: '#e2e8f0', glow: 'rgba(51, 65, 85, 0.32)' },
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
  background: linear-gradient(180deg, var(--pink-soft) 0%, var(--purple-soft) 36%, var(--bg) 72%);
  padding: 50rpx 30rpx 80rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* ---------- 漂浮装饰 ---------- */
.deco { position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: -1; pointer-events: none; overflow: hidden; }
.deco-item { position: absolute; opacity: 0.35; animation: floatUp 8s ease-in-out infinite; }
.d1 { left: 8%; top: 20%; font-size: 40rpx; }
.d2 { left: 80%; top: 16%; font-size: 34rpx; animation-delay: 1.4s; }
.d3 { left: 14%; top: 60%; font-size: 32rpx; animation-delay: 2.6s; }
.d4 { left: 72%; top: 64%; font-size: 36rpx; animation-delay: 3.8s; }
.d5 { left: 46%; top: 10%; font-size: 30rpx; animation-delay: 0.8s; }
@keyframes floatUp {
  0%, 100% { transform: translateY(0) rotate(0); }
  50% { transform: translateY(-26rpx) rotate(12deg); }
}

/* ---------- 标题 ---------- */
.title-box { text-align: center; margin-top: 8rpx; }
.title { display: block; font-size: 46rpx; font-weight: bold; color: var(--text); letter-spacing: 6rpx; }
.sub { display: block; font-size: 24rpx; color: var(--muted); margin-top: 12rpx; letter-spacing: 2rpx; }

/* ---------- 签筒 ---------- */
.stage { width: 100%; display: flex; flex-direction: column; align-items: center; margin-top: 46rpx; }

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
  position: absolute; left: 50%; bottom: -8rpx; transform: translateX(-50%);
  width: 230rpx; height: 40rpx; border-radius: 50%;
  background: radial-gradient(closest-side, rgba(255, 107, 157, 0.26), transparent);
}

.sticks { position: absolute; top: 0; left: 0; width: 100%; height: 240rpx; z-index: 3; }
.stick {
  position: absolute; bottom: 0; width: 14rpx;
  border-radius: 7rpx 7rpx 3rpx 3rpx;
  background: linear-gradient(180deg, #e74c3c 0%, #e74c3c 22rpx, #f8eccb 22rpx, #f1d9a4 100%);
  box-shadow: 0 4rpx 8rpx rgba(0, 0, 0, 0.12);
  transform-origin: bottom center;
}
.bucket-wrap.shaking .stick { animation: stickWobble 0.95s ease-in-out; }
@keyframes stickWobble {
  0%, 100% { margin-left: 0; }
  25% { margin-left: -8rpx; }
  50% { margin-left: 6rpx; }
  75% { margin-left: -4rpx; }
}

.bucket { position: absolute; left: 50%; bottom: 0; transform: translateX(-50%); width: 260rpx; z-index: 2; }
.bucket-top {
  width: 260rpx; height: 46rpx;
  background: linear-gradient(180deg, #cf9568, #a86f45);
  border-radius: 50%;
  box-shadow: inset 0 4rpx 8rpx rgba(0, 0, 0, 0.12), 0 6rpx 16rpx rgba(120, 70, 30, 0.25);
}
.bucket-band {
  width: 268rpx; height: 26rpx; margin: -6rpx auto 0;
  background: linear-gradient(180deg, #d84f4f, #b83a3a);
  border-radius: 8rpx;
  box-shadow: 0 4rpx 10rpx rgba(180, 50, 50, 0.22);
}
.bucket-body {
  width: 216rpx; height: 150rpx; margin: -6rpx auto 0;
  background: linear-gradient(160deg, #c08a5e, #96613a);
  border-radius: 10rpx 10rpx 70rpx 70rpx;
  display: flex; align-items: flex-end; justify-content: center;
  font-size: 40rpx; padding-bottom: 16rpx;
  box-shadow: inset -14rpx 0 24rpx rgba(0, 0, 0, 0.12), 0 12rpx 30rpx rgba(120, 70, 30, 0.22);
}

/* ---------- 提示与按钮 ---------- */
.hint {
  display: flex; align-items: center; margin-top: 26rpx;
  font-size: 26rpx; color: var(--muted);
}
.hint-dot {
  width: 12rpx; height: 12rpx; border-radius: 50%;
  background: var(--pink); margin-right: 12rpx;
  box-shadow: 0 0 10rpx var(--pink);
}
.btn {
  margin-top: 32rpx; background: linear-gradient(135deg, var(--pink), var(--hot)); color: #fff;
  border-radius: 44rpx; font-size: 30rpx; padding: 0 64rpx; line-height: 88rpx; height: 88rpx;
  box-shadow: 0 12rpx 34rpx rgba(255, 107, 157, 0.4);
}
.btn-hover { transform: scale(0.96); opacity: 0.9; }
.btn.again {
  margin-top: 40rpx; font-size: 26rpx; line-height: 72rpx; height: 72rpx; padding: 0 40rpx;
  background: var(--input-bg); color: var(--muted);
  box-shadow: none;
}

/* ---------- 掉出来的签 ---------- */
.drawn-stick { margin-top: 44rpx; perspective: 800rpx; }
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
  background: linear-gradient(160deg, #e74c3c 0%, #c0392b 26%, #f3d9a4 26%, #e8c98f 100%);
  color: #fff; box-shadow: 0 14rpx 40rpx rgba(180, 50, 50, 0.35);
}
.ds-q { font-size: 76rpx; font-weight: bold; text-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.25); }
.ds-tip {
  position: absolute; bottom: 26rpx;
  font-size: 22rpx; color: #a83232; background: #f8eccb;
  padding: 2rpx 18rpx; border-radius: 16rpx;
}
.ds-back {
  background: var(--card); border: 3rpx solid var(--pink); transform: rotateY(180deg);
}
.ds-level { font-size: 60rpx; font-weight: bold; color: var(--pink); letter-spacing: 4rpx; }
.ds-emoji { font-size: 44rpx; margin-top: 12rpx; }

/* ---------- 签文卡片 ---------- */
.fortune-card {
  position: relative;
  width: 100%;
  background: var(--card);
  border-radius: 32rpx;
  border: 2rpx solid var(--lv);
  padding: 48rpx 36rpx 40rpx;
  margin-top: 48rpx;
  text-align: center;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.08), 0 0 0 10rpx var(--lv-soft);
  animation: cardIn 0.6s ease;
  overflow: hidden;
}
@keyframes cardIn { from { transform: translateY(30rpx) scale(0.94); opacity: 0; } to { transform: none; opacity: 1; } }
.fc-deco {
  position: absolute; width: 180rpx; height: 180rpx; border-radius: 50%;
  background: var(--lv-soft); opacity: 0.9;
}
.fc-d1 { top: -80rpx; right: -70rpx; }
.fc-d2 { bottom: -90rpx; left: -70rpx; }
.fc-seal {
  position: relative;
  width: 132rpx; height: 132rpx; margin: 0 auto 20rpx;
  border-radius: 50%;
  background: linear-gradient(160deg, var(--lv), var(--hot));
  border: 6rpx solid var(--card);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 10rpx 30rpx var(--lv-glow);
}
.fc-emoji { font-size: 64rpx; }
.fc-level { display: block; font-size: 58rpx; font-weight: bold; color: var(--lv); letter-spacing: 6rpx; }
.fc-sub { display: block; font-size: 24rpx; color: var(--muted); margin-top: 10rpx; letter-spacing: 6rpx; }
.fc-lines { margin-top: 34rpx; }
.fc-line { display: flex; align-items: center; padding: 18rpx 0; border-bottom: 1rpx solid var(--border); }
.fc-line:last-child { border-bottom: none; }
.fc-k { width: 110rpx; font-size: 26rpx; color: var(--muted); text-align: left; }
.fc-v { flex: 1; font-size: 28rpx; color: var(--text); text-align: right; }
.fc-quote {
  margin-top: 30rpx;
  padding: 24rpx 26rpx;
  background: var(--lv-soft);
  border-left: 6rpx solid var(--lv);
  border-radius: 12rpx;
  font-size: 27rpx;
  color: var(--text);
  line-height: 1.9;
  text-align: left;
}
.fc-hint { margin-top: 28rpx; font-size: 26rpx; color: var(--lv); line-height: 1.7; }
</style>
