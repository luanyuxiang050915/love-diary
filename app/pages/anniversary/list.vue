<template>
  <view class="page">
    <view class="item" v-for="a in list" :key="a.id" @longpress="delItem(a.id)">
      <view class="left">
        <text class="name">{{ a.name }}</text>
        <text class="date">{{ a.date }}</text>
      </view>
      <view class="right">
        <text class="days" :class="{ today: a.days_left === 0, past: a.days_left < 0 }">{{ daysText(a) }}</text>
      </view>
    </view>

    <view class="empty" v-if="list.length === 0">
      <text>还没有纪念日，添加一个吧</text>
    </view>

    <!-- 添加按钮 -->
    <view class="fab" @click="showForm = true">+</view>

    <!-- 添加/编辑弹窗 -->
    <view class="mask" v-if="showForm" @click="showForm = false">
      <view class="popup" @click.stop>
        <text class="pop-title">{{ editingId ? '编辑纪念日' : '添加纪念日' }}</text>
        <input class="pop-input" v-model="form.name" placeholder="名称（如：在一起）" />
        <picker mode="date" :value="form.date" @change="e => form.date = e.detail.value">
          <view class="pop-input">{{ form.date || '选择日期' }}</view>
        </picker>
        <view class="pop-btns">
          <button class="pop-btn cancel" @click="closeForm">取消</button>
          <button class="pop-btn ok" @click="doSave">{{ editingId ? '保存' : '添加' }}</button>
        </view>
        <text class="pop-del" v-if="editingId" @click="doDelete">删除这个纪念日</text>
      </view>
    </view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { formatDate, daysLeftText } from '../../common/util.js'

export default {
  data() {
    return {
      list: [],
      showForm: false,
      editingId: null,
      form: { name: '', date: formatDate() },
    }
  },
  onShow() { this.loadList() },
  methods: {
    async loadList() {
      const { ok, data } = await api.listAnniversaries()
      if (ok) this.list = data
    },
    daysText(a) {
      if (a.days_left == null) return ''
      if (a.days_left === 0) return '就是今天 🎉'
      if (a.days_left > 0) return `还有 ${a.days_left} 天`
      return `已过 ${Math.abs(a.days_left)} 天`
    },
    openAdd() { this.editingId = null; this.form = { name: '', date: formatDate() }; this.showForm = true },
    openEdit(a) { this.editingId = a.id; this.form = { name: a.name, date: a.date }; this.showForm = true },
    closeForm() { this.showForm = false; this.editingId = null },
    async doSave() {
      if (!this.form.name) { uni.showToast({ title: '请输入名称', icon: 'none' }); return }
      const { ok, msg } = this.editingId
        ? await api.updateAnniversary(this.editingId, this.form)
        : await api.createAnniversary(this.form)
      if (ok) { uni.showToast({ title: '已保存', icon: 'success' }); this.closeForm(); this.loadList() }
      else { uni.showToast({ title: msg, icon: 'none' }) }
    },
    async delItem(id) {
      const { confirm } = await uni.showModal({ title: '删除', content: '确定要删除这个纪念日吗？' })
      if (!confirm) return
      await api.deleteAnniversary(id)
      uni.showToast({ title: '已删除', icon: 'success' })
      this.loadList()
    },
    async doDelete() {
      if (!this.editingId) return
      await api.deleteAnniversary(this.editingId)
      uni.showToast({ title: '已删除', icon: 'success' })
      this.closeForm(); this.loadList()
    },
  },
}
</script>

<style scoped>
.page { padding-bottom: 140rpx; }
.item {
  display: flex; align-items: center; justify-content: space-between;
  background: #fff; border-radius: 16rpx; padding: 28rpx;
  margin: 20rpx 30rpx;
}
.left { display: flex; flex-direction: column; }
.name { font-size: 30rpx; font-weight: bold; }
.date { font-size: 24rpx; color: #999; margin-top: 6rpx; }
.days { font-size: 28rpx; color: #f8a5c2; }
.days.today { color: #e74c3c; font-weight: bold; }
.days.past { color: #999; }
.fab {
  position: fixed; bottom: 40rpx; right: 40rpx;
  width: 100rpx; height: 100rpx;
  background: #f8a5c2; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 50rpx;
  box-shadow: 0 4rpx 12rpx rgba(248,165,194,0.5);
}
.mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 999;
}
.popup {
  width: 600rpx; background: #fff; border-radius: 24rpx; padding: 40rpx;
}
.pop-title { font-size: 32rpx; font-weight: bold; display: block; margin-bottom: 30rpx; }
.pop-input {
  width: 100%; height: 80rpx; background: #f5f5f5;
  border-radius: 12rpx; padding: 0 20rpx; margin-bottom: 20rpx;
  font-size: 28rpx; line-height: 80rpx;
}
.pop-btns { display: flex; gap: 20rpx; margin-top: 20rpx; }
.pop-btn { flex: 1; height: 80rpx; line-height: 80rpx; border-radius: 12rpx; font-size: 28rpx; text-align: center; }
.pop-btn.cancel { background: #f0f0f0; color: #666; }
.pop-btn.ok { background: #f8a5c2; color: #fff; }
.pop-del { display: block; text-align: center; color: #e74c3c; font-size: 26rpx; margin-top: 26rpx; }
.empty { text-align: center; color: #999; font-size: 28rpx; padding-top: 200rpx; }
</style>
