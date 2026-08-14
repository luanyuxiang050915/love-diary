<template>
  <view class="page" :style="cssVars">
    <!-- 消息列表 -->
    <scroll-view class="msg-list" scroll-y :scroll-into-view="scrollInto" :scroll-with-animation="true">
      <template v-for="item in displayList" :key="item.id">
        <view class="m-date" v-if="item.type === 'date'">{{ item.text }}</view>
        <view class="msg" v-else :id="'m' + item.id" :class="{ mine: item.mine }">
          <view class="bubble" :class="{ mine: item.mine, emoji: item.msg_type === 'emoji', sticker: item.msg_type === 'sticker' }">
            <image v-if="item.msg_type === 'sticker'" class="st-img" :src="imgUrl(item.sticker_url)" mode="aspectFit" />
            <text v-else-if="item.msg_type === 'emoji'" class="emoji-text">{{ item.content }}</text>
            <text v-else class="text">{{ item.content }}</text>
          </view>
          <text class="time" v-if="showTime(displayList, item)">{{ item.time }}</text>
        </view>
      </template>
      <view class="empty" v-if="displayList.length === 0">
        <text class="empty-icon">💬</text>
        <text>和 TA 说句话吧</text>
      </view>
    </scroll-view>

    <!-- 输入栏 -->
    <view class="input-bar">
      <view class="emoji-btn" @click="togglePanel">😊</view>
      <input class="input" v-model="inputText" placeholder="说点什么…" confirm-type="send" @confirm="sendText" />
      <button class="send-btn" size="mini" @click="sendText">发送</button>
    </view>

    <!-- 表情面板 -->
    <view class="panel" v-if="panelOpen">
      <view class="panel-tabs">
        <text class="tab" :class="{ on: panelTab === 'emoji' }" @click="panelTab = 'emoji'">😀 基础表情</text>
        <text class="tab" :class="{ on: panelTab === 'sticker' }" @click="panelTab = 'sticker'">🎨 自定义表情包</text>
      </view>

      <scroll-view class="panel-body" scroll-y v-if="panelTab === 'emoji'">
        <view class="emoji-grid">
          <text class="e-cell" v-for="e in EMOJIS" :key="e" @click="sendEmoji(e)">{{ e }}</text>
        </view>
      </scroll-view>

      <scroll-view class="panel-body" scroll-y v-else>
        <view class="sticker-grid">
          <view class="s-add" @click="addSticker">＋<text class="s-add-t">添加</text></view>
          <view class="s-cell" v-for="s in stickers" :key="s.id" @click="sendSticker(s)" @longpress="delSticker(s)">
            <image class="s-img" :src="imgUrl(s.url)" mode="aspectFit" />
          </view>
        </view>
        <text class="sticker-tip" v-if="stickers.length === 0">还没有自定义表情，点“＋”上传一张（可以是对方的丑照 😝）</text>
      </scroll-view>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'
import store from '../../common/store.js'

const EMOJIS = ['😀','😄','😁','😂','🤣','😊','😍','🥰','😘','😗','😋','😜','🤪','😎','🥳','😏','😌','😴','🥺','😢','😭','😅','😳','🤗','🤔','🙄','😬','😤','😡','🤯','😱','🤩','😇','🙃','🫶','👍','👏','🙏','💪','✌️','🤞','💕','💖','💗','💓','💞','💘','❤️','🧡','💛','💚','💙','💜','💔','💯','✨','🎉','🎂','🌹','🌷','🌸','🌙','☀️','🌈','🍀','🍰','🧋','🐰','🐻','🐱','🐶','🦄','💍','💌','🎁','🎈','🔥','👀','💤','🙈','🙉','🙊','😻','🤭','😚','🥹','😉','😆','🤤','🥱','😑','😐','💋','👅','🤟','👌','🫰','🐷','🍓','🍑','🥝']

const CACHE_KEY = 'chat_cache_v1'
const DAY = 86400000

function fmtTime(iso) {
  const d = new Date((iso || '').replace(' ', 'T') + 'Z')
  if (isNaN(d)) return ''
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
function fmtDate(iso) {
  const d = new Date((iso || '').replace(' ', 'T') + 'Z')
  if (isNaN(d)) return ''
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

export default {
  data() {
    return {
      EMOJIS,
      messages: [],
      stickers: [],
      inputText: '',
      panelOpen: false,
      panelTab: 'emoji',
      myId: 0,
      lastId: 0,
      scrollInto: '',
      timer: null,
    }
  },
  computed: {
    displayList() {
      const out = []
      let prevDate = ''
      this.messages.forEach(m => {
        const d = fmtDate(m.created_at)
        if (d && d !== prevDate) { out.push({ type: 'date', text: d, id: 'd-' + d }); prevDate = d }
        out.push({
          type: 'msg',
          id: m.id,
          mine: m.sender_id === this.myId,
          content: m.content,
          msg_type: m.msg_type,
          sticker_url: m.sticker_url,
          time: fmtTime(m.created_at),
          nickname: m.sender_nickname,
        })
      })
      return out
    },
  },
  onShow() {
    applyTheme()
    const u = store.getUser()
    this.myId = u ? u.id : 0
    this.init()
  },
  onHide() {
    this.stopPolling()
  },
  methods: {
    async init() {
      const cached = uni.getStorageSync(CACHE_KEY)
      const now = Date.now()
      let items = []
      if (cached && cached.items) {
        items = cached.items.filter(m => now - new Date(m.created_at.replace(' ', 'T') + 'Z').getTime() < DAY)
      }
      const { ok, data } = await api.listMessages(0)
      if (ok && data.length) {
        const seen = new Set(items.map(m => m.id))
        data.forEach(m => { if (!seen.has(m.id)) items.push(m) })
        items.sort((a, b) => a.id - b.id)
        this.saveCache(items)
      }
      this.messages = items.filter(m => now - new Date(m.created_at.replace(' ', 'T') + 'Z').getTime() < DAY)
      this.lastId = this.messages.length ? this.messages[this.messages.length - 1].id : 0
      this.scrollBottom()
      this.loadStickers()
      this.startPolling()
    },
    saveCache(items) {
      const now = Date.now()
      const fresh = items.filter(m => now - new Date(m.created_at.replace(' ', 'T') + 'Z').getTime() < DAY)
      uni.setStorageSync(CACHE_KEY, { items: fresh.slice(-100), savedAt: now })
    },
    startPolling() {
      this.stopPolling()
      this.timer = setInterval(async () => {
        const { ok, data } = await api.listMessages(this.lastId)
        if (ok && data.length) {
          const all = this.messages.concat(data)
          this.messages = all
          this.lastId = data[data.length - 1].id
          this.saveCache(all)
          this.scrollBottom()
        }
      }, 3000)
    },
    stopPolling() {
      if (this.timer) { clearInterval(this.timer); this.timer = null }
    },
    scrollBottom() {
      this.$nextTick(() => {
        const last = this.displayList.filter(i => i.type === 'msg').pop()
        if (last) this.scrollInto = 'm' + last.id
      })
    },
    togglePanel() { this.panelOpen = !this.panelOpen },
    async sendText() {
      const content = this.inputText.trim()
      if (!content) return
      const { ok, msg } = await api.sendMessage({ content, msg_type: 'text' })
      if (ok) { this.inputText = ''; this.appendLocal() } else uni.showToast({ title: msg, icon: 'none' })
    },
    async sendEmoji(e) {
      const { ok, msg } = await api.sendMessage({ content: e, msg_type: 'emoji' })
      if (!ok) uni.showToast({ title: msg, icon: 'none' })
    },
    async sendSticker(s) {
      const { ok, msg } = await api.sendMessage({ content: '', msg_type: 'sticker', sticker_url: s.url })
      if (!ok) uni.showToast({ title: msg, icon: 'none' })
    },
    async appendLocal() {
      const { ok, data } = await api.listMessages(this.lastId)
      if (ok && data.length) {
        this.messages = this.messages.concat(data)
        this.lastId = data[data.length - 1].id
        this.saveCache(this.messages)
        this.scrollBottom()
      }
    },
    async loadStickers() {
      const { ok, data } = await api.listStickers()
      if (ok) this.stickers = data
    },
    async addSticker() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        success: async (res) => {
          uni.showLoading({ title: '上传中…' })
          const r = await api.uploadImage(res.tempFilePaths[0])
          if (!r.ok) { uni.hideLoading(); uni.showToast({ title: r.msg, icon: 'none' }); return }
          const a = await api.addSticker(r.url)
          uni.hideLoading()
          if (a.ok) { uni.showToast({ title: '表情已添加', icon: 'success' }); this.loadStickers() }
          else uni.showToast({ title: a.msg, icon: 'none' })
        },
      })
    },
    async delSticker(s) {
      const { confirm } = await uni.showModal({ title: '删除表情', content: '确定删除这个自定义表情吗？' })
      if (!confirm) return
      const { ok } = await api.deleteSticker(s.id)
      if (ok) { uni.showToast({ title: '已删除', icon: 'success' }); this.loadStickers() }
    },
    imgUrl(url) {
      if (!url) return ''
      if (url.startsWith('http')) return url
      return 'http://47.93.241.64:8000' + url
    },
    showTime(list, item) {
      const idx = list.findIndex(i => i.type === 'msg' && i.id === item.id)
      const prev = list[idx - 1]
      return !prev || prev.type === 'date' || prev.time !== item.time
    },
  },
}
</script>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; background: var(--bg); }

.msg-list { flex: 1; padding: 20rpx 24rpx 20rpx; box-sizing: border-box; }
.m-date { text-align: center; font-size: 22rpx; color: var(--muted); margin: 18rpx 0; }
.msg { display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 18rpx; }
.msg.mine { align-items: flex-end; }
.bubble {
  max-width: 78%; background: var(--card); border: 1rpx solid var(--border);
  border-radius: 20rpx 20rpx 20rpx 6rpx; padding: 16rpx 22rpx;
}
.bubble.mine { background: linear-gradient(135deg, var(--pink), var(--hot)); border: none; border-radius: 20rpx 20rpx 6rpx 20rpx; }
.bubble .text { font-size: 28rpx; color: var(--text); line-height: 1.6; word-break: break-all; }
.bubble.mine .text { color: #fff; }
.bubble.emoji { background: transparent; border: none; padding: 0; }
.emoji-text { font-size: 72rpx; line-height: 1.2; }
.bubble.sticker { background: transparent; border: none; padding: 0; }
.st-img { width: 220rpx; height: 220rpx; border-radius: 16rpx; }
.time { font-size: 20rpx; color: var(--muted); margin-top: 6rpx; }
.empty { display: flex; flex-direction: column; align-items: center; padding-top: 260rpx; color: var(--muted); font-size: 26rpx; }
.empty-icon { font-size: 80rpx; margin-bottom: 16rpx; }

.input-bar {
  display: flex; align-items: center; gap: 14rpx;
  padding: 16rpx 24rpx calc(16rpx + env(safe-area-inset-bottom));
  background: var(--card); border-top: 1rpx solid var(--border);
}
.emoji-btn { font-size: 44rpx; padding: 0 6rpx; }
.input {
  flex: 1; background: var(--input-bg); border-radius: 36rpx;
  padding: 14rpx 26rpx; font-size: 28rpx; color: var(--text); min-height: 64rpx;
}
.send-btn { background: linear-gradient(135deg, var(--pink), var(--hot)); color: #fff; border-radius: 36rpx; padding: 0 32rpx; }

.panel {
  height: 440rpx; background: var(--card); border-top: 1rpx solid var(--border);
  display: flex; flex-direction: column;
}
.panel-tabs { display: flex; padding: 16rpx 24rpx 0; gap: 30rpx; }
.tab { font-size: 26rpx; color: var(--muted); padding-bottom: 12rpx; }
.tab.on { color: var(--pink); font-weight: bold; border-bottom: 4rpx solid var(--pink); }
.panel-body { flex: 1; padding: 20rpx 24rpx; box-sizing: border-box; }
.emoji-grid { display: flex; flex-wrap: wrap; }
.e-cell { width: 12.5%; text-align: center; font-size: 44rpx; padding: 14rpx 0; }
.sticker-grid { display: flex; flex-wrap: wrap; gap: 16rpx; }
.s-add, .s-cell {
  width: 150rpx; height: 150rpx; border-radius: 16rpx;
  display: flex; align-items: center; justify-content: center;
}
.s-add { background: var(--pink-soft); color: var(--pink); font-size: 52rpx; flex-direction: column; }
.s-add-t { font-size: 20rpx; margin-top: 4rpx; }
.s-cell { background: var(--bg); padding: 8rpx; box-sizing: border-box; }
.s-img { width: 100%; height: 100%; }
.sticker-tip { display: block; text-align: center; color: var(--muted); font-size: 24rpx; padding: 60rpx 30rpx; }
</style>
