<template>
  <view class="page" :style="cssVars">
    <!-- 我的位置 -->
    <view class="card">
      <view class="card-head">
        <text class="card-title">📍 我的位置</text>
        <text class="card-time" v-if="myLoc">更新于 {{ fmtTime(myLoc.updated_at) }}</text>
      </view>
      <view class="loc-body" v-if="myLoc">
        <text class="loc-coord">{{ myLoc.lat.toFixed(5) }}, {{ myLoc.lng.toFixed(5) }}</text>
        <text class="loc-remark" v-if="myLoc.remark">{{ myLoc.remark }}</text>
      </view>
      <view class="loc-body empty" v-else>还没有共享位置，点下面按钮更新</view>
      <view class="loc-actions">
        <input class="remark-input" v-model="remark" placeholder="备注（可选），如：在公司" />
        <button class="btn" size="mini" :disabled="locating" @click="updateMy">🔄 更新我的位置</button>
      </view>
    </view>

    <!-- TA 的位置 -->
    <view class="card">
      <view class="card-head">
        <text class="card-title">💞 TA 的位置</text>
        <text class="card-time" v-if="taLoc">更新于 {{ fmtTime(taLoc.updated_at) }}</text>
      </view>
      <view class="loc-body" v-if="taLoc">
        <text class="loc-coord">{{ taLoc.lat.toFixed(5) }}, {{ taLoc.lng.toFixed(5) }}</text>
        <text class="loc-remark" v-if="taLoc.remark">{{ taLoc.remark }}</text>
      </view>
      <view class="loc-body empty" v-else>{{ taEmptyText }}</view>
      <view class="loc-actions" v-if="taLoc">
        <button class="btn ghost" size="mini" @click="openMap(taLoc)">🗺 在地图查看</button>
      </view>
    </view>

    <!-- 距离 -->
    <view class="distance" v-if="myLoc && taLoc">
      <text class="dist-label">我们相距</text>
      <text class="dist-num">{{ distanceText }}</text>
    </view>

    <view class="tip">位置只在打开本页面、点击"更新"时共享，不会持续追踪你</view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'

function distanceKm(lat1, lng1, lat2, lng2) {
  const R = 6371
  const dLat = ((lat2 - lat1) * Math.PI) / 180
  const dLng = ((lng2 - lng1) * Math.PI) / 180
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLng / 2) ** 2
  return 2 * R * Math.asin(Math.sqrt(a))
}

export default {
  data() {
    return {
      myLoc: null,
      taLoc: null,
      partnerBound: false,
      remark: '',
      locating: false,
      timer: null,
    }
  },
  computed: {
    taEmptyText() {
      return this.partnerBound ? 'TA 还没有共享位置' : '还没有绑定另一半'
    },
    distanceText() {
      if (!this.myLoc || !this.taLoc) return ''
      const km = distanceKm(this.myLoc.lat, this.myLoc.lng, this.taLoc.lat, this.taLoc.lng)
      if (km < 1) return `${Math.max(1, Math.round(km * 1000))} 米`
      return `${km.toFixed(1)} 公里`
    },
  },
  onShow() {
    applyTheme()
    this.load()
    this.timer = setInterval(() => this.load(), 20000)
  },
  onHide() {
    if (this.timer) { clearInterval(this.timer); this.timer = null }
  },
  onUnload() {
    if (this.timer) { clearInterval(this.timer); this.timer = null }
  },
  methods: {
    async load() {
      const [me, ta] = await Promise.all([api.getMyLocation(), api.getPartnerLocation()])
      if (me.ok) this.myLoc = me.data
      if (ta.ok) {
        this.taLoc = ta.data
        this.partnerBound = true
      } else {
        this.taLoc = null
        this.partnerBound = false
      }
    },
    getPosition() {
      return new Promise((resolve) => {
        // #ifdef H5
        // H5 无地图服务商 key 时 gcj02 转换不可用，用默认 wgs84
        uni.getLocation({
          success: (r) => resolve({ lat: r.latitude, lng: r.longitude }),
          fail: () => resolve(null),
        })
        // #endif
        // #ifndef H5
        // App 原生定位模块直接返回 gcj02（和高德/腾讯地图坐标一致）
        uni.getLocation({
          type: 'gcj02',
          success: (r) => resolve({ lat: r.latitude, lng: r.longitude }),
          fail: () => resolve(null),
        })
        // #endif
      })
    },
    async updateMy() {
      if (this.locating) return
      this.locating = true
      uni.showLoading({ title: '定位中' })
      const loc = await this.getPosition()
      uni.hideLoading()
      if (loc) {
        await this.saveLoc(loc.lat, loc.lng)
        this.locating = false
        return
      }
      // 定位失败（权限被拒等）：允许手动输入经纬度测试
      this.locating = false
      uni.showModal({
        title: '定位失败',
        content: '无法获取位置，请检查定位权限。也可以手动输入经纬度（纬度,经度）测试。',
        editable: true,
        placeholderText: '如 31.2304,121.4737',
        success: async (r) => {
          if (!r.confirm) return
          const parts = (r.content || '').trim().split(',')
          const lat = parseFloat(parts[0])
          const lng = parseFloat(parts[1])
          if (parts.length === 2 && !isNaN(lat) && !isNaN(lng)) {
            await this.saveLoc(lat, lng)
          } else {
            uni.showToast({ title: '格式不对，应为 纬度,经度', icon: 'none' })
          }
        },
      })
    },
    async saveLoc(lat, lng) {
      const { ok, msg } = await api.updateMyLocation({ lat, lng, remark: this.remark.trim() })
      if (ok) {
        uni.showToast({ title: '位置已更新', icon: 'success' })
        this.load()
      } else {
        uni.showToast({ title: msg, icon: 'none' })
      }
    },
    openMap(loc) {
      // #ifdef H5
      const url = `https://uri.amap.com/marker?position=${loc.lng},${loc.lat}&name=${encodeURIComponent(loc.remark || 'TA 的位置')}&src=love_diary&coordinate=wgs84`
      window.open(url)
      // #endif
      // #ifndef H5
      uni.openLocation({
        latitude: loc.lat,
        longitude: loc.lng,
        name: loc.remark || 'TA 的位置',
      })
      // #endif
    },
    fmtTime(iso) {
      if (!iso) return ''
      const t = new Date((iso || '').replace(' ', 'T') + 'Z').getTime()
      if (isNaN(t)) return ''
      const diff = Math.max(0, Date.now() - t)
      const min = Math.floor(diff / 60000)
      if (min < 1) return '刚刚'
      if (min < 60) return `${min} 分钟前`
      const hr = Math.floor(min / 60)
      if (hr < 24) return `${hr} 小时前`
      const d = new Date(t)
      return `${d.getMonth() + 1}月${d.getDate()}日`
    },
  },
}
</script>

<style scoped>
.page { padding: 24rpx 30rpx 80rpx; }

.card {
  background: var(--card);
  border-radius: 24rpx;
  padding: 28rpx 30rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 22rpx rgba(0, 0, 0, 0.05);
}
.card-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18rpx; }
.card-title { font-size: 32rpx; font-weight: bold; color: var(--text); }
.card-time { font-size: 22rpx; color: var(--muted); }

.loc-body { padding: 20rpx; background: var(--bg); border-radius: 16rpx; }
.loc-body.empty { text-align: center; color: var(--muted); font-size: 26rpx; }
.loc-coord { display: block; font-size: 30rpx; color: var(--pink); font-weight: bold; letter-spacing: 1rpx; }
.loc-remark { display: block; margin-top: 10rpx; font-size: 26rpx; color: var(--text); }

.loc-actions { display: flex; align-items: center; gap: 18rpx; margin-top: 20rpx; }
.remark-input {
  flex: 1;
  height: 68rpx;
  background: var(--bg);
  border-radius: 14rpx;
  padding: 0 20rpx;
  font-size: 26rpx;
}
.btn {
  background: linear-gradient(135deg, var(--pink), var(--hot));
  color: #fff;
  border-radius: 34rpx;
  font-size: 24rpx;
  padding: 0 28rpx;
  line-height: 68rpx;
  height: 68rpx;
  margin: 0;
}
.btn.ghost { background: var(--pink-soft); color: var(--pink); }

.distance {
  background: linear-gradient(135deg, var(--pink-soft), var(--purple-soft));
  border-radius: 24rpx;
  padding: 36rpx 30rpx;
  text-align: center;
  margin-bottom: 24rpx;
}
.dist-label { display: block; font-size: 24rpx; color: var(--muted); }
.dist-num { display: block; margin-top: 10rpx; font-size: 48rpx; font-weight: bold; color: var(--hot); }

.tip { text-align: center; font-size: 22rpx; color: var(--muted); line-height: 1.7; }
</style>
