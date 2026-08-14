<template>
  <view class="page" :style="cssVars">
    <!-- 夜景背景 -->
    <view class="bg-img"></view>
    <view class="bg-cover"></view>
    <view class="bg-vignette"></view>

    <!-- Canvas 粒子特效层 -->
    <canvas class="fx-canvas" canvas-id="fxCanvas" id="fxCanvas"></canvas>

    <!-- 标题 -->
    <view class="title-box">
      <text class="title-en">OMIKUJI · DAILY FORTUNE</text>
      <text class="title">每日一签</text>
      <text class="sub">摇一摇签筒，看看今天的好运气</text>
    </view>

    <!-- 摇签桶 -->
    <view class="stage" v-if="!result">
      <view class="bucket-wrap" id="bucketWrap">
        <view class="bucket-glow"></view>
        <view class="sticks" id="fxSticks">
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
        <view class="tassel"></view>
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
      <view class="drawn-stick" v-if="drawn" id="drawnStick" @click="openStick">
        <view class="ds-inner" id="dsInner">
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
    <view class="fortune-card" v-if="result" id="fortuneCard" :style="cardStyle">
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
import gsap from '../../common/gsap.js'

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
      opening: false,
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
  onShow() {
    applyTheme()
    this.initFx()
    this.init()
  },
  onHide() {
    this.stopFx()
  },
  onUnload() {
    this.stopFx()
  },
  methods: {
    todayKey() {
      const t = new Date()
      return `fortune_${t.getFullYear()}-${t.getMonth() + 1}-${t.getDate()}`
    },
    el(id) {
      return typeof document !== 'undefined' ? document.getElementById(id) : null
    },
    async init() {
      this.sticks = Array.from({ length: 7 }, (_, i) => ({
        left: 14 + i * 11,
        h: 44 + Math.random() * 16,
        rot: -7 + Math.random() * 14,
      }))

      const { ok, data } = await api.getTodayFortune()
      if (ok && data) {
        this.result = data
        this.picked = data
        this.drawn = true
        uni.setStorageSync(this.todayKey(), JSON.stringify(data))
        this.$nextTick(() => this.cardIn())
      } else if (!ok) {
        const saved = uni.getStorageSync(this.todayKey())
        if (saved) {
          this.result = JSON.parse(saved)
          this.picked = this.result
          this.drawn = true
          this.$nextTick(() => this.cardIn())
        }
      }
    },

    /* ---------- GSAP 动效 ---------- */
    shake() {
      if (this.shaking) return
      this.shaking = true
      const bw = this.el('bucketWrap')
      const st = this.el('fxSticks')

      if (bw) {
        gsap.to(bw, {
          rotate: 0,
          duration: 0.96,
          keyframes: [
            { rotate: -14, duration: 0.13, ease: 'power2.in' },
            { rotate: 11, duration: 0.14, ease: 'power1.out' },
            { rotate: -9, duration: 0.15, ease: 'power1.out' },
            { rotate: 7, duration: 0.16, ease: 'power1.out' },
            { rotate: -5, duration: 0.16, ease: 'power1.out' },
            { rotate: 0, duration: 0.22, ease: 'elastic.out(1, 0.4)' },
          ],
        })
      }
      if (st) {
        gsap.to(st, {
          x: 0,
          duration: 0.96,
          keyframes: [
            { x: 6, duration: 0.13, ease: 'power1.out' },
            { x: -5, duration: 0.14, ease: 'power1.out' },
            { x: 4, duration: 0.15, ease: 'power1.out' },
            { x: -3, duration: 0.16, ease: 'power1.out' },
            { x: 2, duration: 0.16, ease: 'power1.out' },
            { x: 0, duration: 0.22, ease: 'elastic.out(1, 0.4)' },
          ],
        })
      }
      this.burst(0.5, 0.32, 18)

      setTimeout(() => {
        this.shaking = false
        this.drawn = true
        this.picked = {}
        this.$nextTick(() => {
          const ds = this.el('drawnStick')
          if (ds) {
            gsap.fromTo(ds, { y: -170, rotate: -18, opacity: 0 }, {
              y: 0,
              rotate: 0,
              opacity: 1,
              duration: 0.8,
              ease: 'elastic.out(1, 0.45)',
            })
          }
          this.burst(0.5, 0.55, 26)
        })
      }, 980)
    },

    async openStick() {
      if (this.shaking || this.opening) return
      const { ok, data, msg } = await api.drawFortune()
      if (!ok) {
        uni.showToast({ title: msg || '抽签失败，请重试', icon: 'none' })
        return
      }
      this.opening = true
      this.picked = data
      uni.setStorageSync(this.todayKey(), JSON.stringify(data))

      this.$nextTick(() => {
        const inner = this.el('dsInner')
        if (!inner) { this.opening = false; this.result = data; return }
        gsap.to(inner, {
          rotateY: 180,
          duration: 0.9,
          ease: 'power3.inOut',
          onComplete: () => {
            this.result = data
            this.opening = false
            this.$nextTick(() => {
              this.cardIn()
              this.burst(0.5, 0.42, 40)
            })
          },
        })
      })
    },

    cardIn() {
      const card = this.el('fortuneCard')
      if (!card) return
      gsap.from(card, {
        y: 80,
        scale: 0.88,
        opacity: 0,
        duration: 0.9,
        ease: 'elastic.out(1, 0.5)',
      })
    },

    /* ---------- Canvas 粒子 ---------- */
    findCanvas() {
      // uni-app H5 会把 <canvas> 包一层 uni-canvas，真实画布在内部
      const wrapper = document.getElementById('fxCanvas')
      if (wrapper) return wrapper.tagName === 'CANVAS' ? wrapper : wrapper.querySelector('canvas')
      return document.querySelector('canvas')
    },
    initFx() {
      if (this.running || this.fxInitPending) return
      const canvas = this.findCanvas()
      if (!canvas || typeof canvas.getContext !== 'function') {
        // 内层画布可能还没渲染出来，稍后重试
        this.fxInitPending = true
        setTimeout(() => { this.fxInitPending = false; this.initFx() }, 200)
        return
      }
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      this.fxW = window.innerWidth
      this.fxH = window.innerHeight
      canvas.width = this.fxW * dpr
      canvas.height = this.fxH * dpr
      canvas.style.width = this.fxW + 'px'
      canvas.style.height = this.fxH + 'px'
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      this.fxCtx = ctx

      this.petals = Array.from({ length: 16 }, () => this.newPetal(true))
      this.sparkles = Array.from({ length: 14 }, () => this.newSparkle(true))
      this.bursts = []
      this.running = true
      const loop = () => {
        if (!this.running) return
        this.drawFx()
        this.raf = requestAnimationFrame(loop)
      }
      this.raf = requestAnimationFrame(loop)
    },
    stopFx() {
      this.running = false
      this.fxInitPending = false
      if (this.raf) cancelAnimationFrame(this.raf)
      this.raf = null
    },
    newPetal(anywhere) {
      return {
        x: Math.random() * this.fxW,
        y: anywhere ? Math.random() * this.fxH : -20,
        size: 4 + Math.random() * 5,
        vy: 0.35 + Math.random() * 0.55,
        sway: Math.random() * 0.02 + 0.01,
        phase: Math.random() * Math.PI * 2,
        rot: Math.random() * Math.PI * 2,
        vr: (Math.random() - 0.5) * 0.05,
      }
    },
    newSparkle(anywhere) {
      return {
        x: Math.random() * this.fxW,
        y: anywhere ? Math.random() * this.fxH : this.fxH + 10,
        size: 0.8 + Math.random() * 1.6,
        vy: 0.15 + Math.random() * 0.35,
        phase: Math.random() * Math.PI * 2,
      }
    },
    burst(nx, ny, count) {
      const ctx = this.fxCtx
      if (!ctx) return
      const x = this.fxW * nx
      const y = this.fxH * ny
      for (let i = 0; i < count; i++) {
        const ang = Math.random() * Math.PI * 2
        const spd = 1.2 + Math.random() * 3.2
        this.bursts.push({
          x, y,
          vx: Math.cos(ang) * spd,
          vy: Math.sin(ang) * spd - 1.2,
          life: 60 + Math.random() * 30,
          max: 90,
          size: 1 + Math.random() * 2,
          gold: Math.random() > 0.35,
        })
      }
    },
    drawFx() {
      const ctx = this.fxCtx
      if (!ctx) return
      ctx.clearRect(0, 0, this.fxW, this.fxH)
      const t = Date.now() / 1000

      // 花瓣
      this.petals.forEach(p => {
        p.y += p.vy
        p.x += Math.sin(t * 1.2 + p.phase) * p.sway * 8
        p.rot += p.vr
        if (p.y > this.fxH + 24) Object.assign(p, this.newPetal(false))
        ctx.save()
        ctx.translate(p.x, p.y)
        ctx.rotate(p.rot)
        ctx.globalAlpha = 0.55
        ctx.fillStyle = '#f9a8d4'
        ctx.beginPath()
        ctx.ellipse(0, 0, p.size, p.size * 0.55, 0, 0, Math.PI * 2)
        ctx.fill()
        ctx.restore()
      })

      // 星光
      this.sparkles.forEach(s => {
        s.y -= s.vy
        s.phase += 0.04
        if (s.y < -12) Object.assign(s, this.newSparkle(false))
        const a = 0.25 + 0.55 * Math.abs(Math.sin(s.phase))
        ctx.globalAlpha = a
        ctx.fillStyle = '#f5d78a'
        ctx.beginPath()
        ctx.arc(s.x, s.y, s.size, 0, Math.PI * 2)
        ctx.fill()
      })

      // 爆发粒子
      this.bursts = this.bursts.filter(b => b.life > 0)
      this.bursts.forEach(b => {
        b.life -= 1
        b.x += b.vx
        b.y += b.vy
        b.vy += 0.06
        const a = Math.max(0, b.life / b.max)
        ctx.globalAlpha = a
        ctx.fillStyle = b.gold ? '#f5d78a' : '#f9a8d4'
        ctx.beginPath()
        ctx.arc(b.x, b.y, b.size, 0, Math.PI * 2)
        ctx.fill()
      })
      ctx.globalAlpha = 1
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

/* ---------- 粒子画布 ---------- */
.fx-canvas {
  position: fixed; top: 0; left: 0;
  z-index: 4;
  pointer-events: none;
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

.bucket-wrap { position: relative; width: 340rpx; height: 330rpx; transform-origin: 50% 90%; will-change: transform; }

.bucket-glow {
  position: absolute; left: 50%; bottom: -14rpx; transform: translateX(-50%);
  width: 280rpx; height: 56rpx; border-radius: 50%;
  background: radial-gradient(closest-side, rgba(255, 214, 140, 0.34), transparent);
  filter: blur(6rpx);
}

.sticks { position: absolute; top: 0; left: 0; width: 100%; height: 240rpx; z-index: 5; will-change: transform; }
.stick {
  position: absolute; bottom: 0; width: 14rpx;
  border-radius: 7rpx 7rpx 3rpx 3rpx;
  background: linear-gradient(180deg, #d94f4f 0%, #d94f4f 22rpx, #f7e6bd 22rpx, #edcf96 100%);
  box-shadow: 0 4rpx 8rpx rgba(0, 0, 0, 0.35);
  transform-origin: bottom center;
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
.tassel {
  position: absolute; left: 50%; bottom: -26rpx; transform: translateX(-50%);
  width: 12rpx; height: 56rpx;
  background: linear-gradient(180deg, #d84f4f, #b83a3a);
  border-radius: 0 0 8rpx 8rpx;
}
.tassel::after {
  content: '';
  position: absolute; top: 100%; left: 50%; transform: translateX(-50%);
  width: 26rpx; height: 34rpx;
  background: radial-gradient(closest-side, #d84f4f, transparent);
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
.drawn-stick { margin-top: 48rpx; perspective: 800rpx; will-change: transform; }
.ds-inner {
  position: relative; width: 150rpx; height: 380rpx; transform-style: preserve-3d;
  will-change: transform;
}
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
  will-change: transform, opacity;
  overflow: hidden;
}
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
