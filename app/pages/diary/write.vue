<template>
  <view class="page">
    <!-- 内容 -->
    <textarea
      class="textarea"
      v-model="form.content"
      placeholder="今天发生了什么..."
      :maxlength="5000"
    />

    <!-- 心情选择器 -->
    <view class="row">
      <text class="label">心情</text>
      <picker mode="selector" :range="MOODS" :value="moodIndex" @change="onMoodChange">
        <view class="picker">{{ form.mood || '点击选择' }}</view>
      </picker>
    </view>

    <!-- 图片 -->
    <view class="row">
      <text class="label">图片</text>
      <view class="img-list">
        <image
          v-for="(img, i) in form.images"
          :key="i"
          :src="imgThumb(img)"
          mode="aspectFill"
          class="img-item"
          @click="delImg(i)"
        />
        <view class="img-add" @click="chooseImg" v-if="form.images.length < 9">+</view>
      </view>
    </view>

    <!-- 日期 -->
    <view class="row">
      <text class="label">日期</text>
      <picker mode="date" :value="form.date" @change="onDateChange">
        <view class="picker">{{ form.date }}</view>
      </picker>
    </view>

    <!-- 是否让TA看到 -->
    <view class="row">
      <text class="label">让TA看到</text>
      <switch :checked="form.visible_to_partner" @change="e => form.visible_to_partner = e.detail.value" color="#f8a5c2" />
    </view>

    <!-- 保存 -->
    <button class="btn" @click="doSave">{{ isEdit ? '保存修改' : '保存日记' }}</button>
    <view class="danger" v-if="isEdit" @click="doDelete">删除这篇日记</view>
  </view>
</template>

<script>
import * as api from '../../common/api.js'
import { applyTheme } from '../../common/theme.js'
import { formatDate, MOODS } from '../../common/util.js'

export default {
  data() {
    return {
      MOODS,
      isEdit: false,
      editId: null,
      form: {
        content: '',
        mood: '',
        images: [],
        date: formatDate(),
        visible_to_partner: true,
      },
    }
  },

  computed: {
    moodIndex() {
      const i = MOODS.indexOf(this.form.mood)
      return i >= 0 ? i : 0
    },
  },

  onLoad(options) {
    if (options.diary_id) {
      this.isEdit = true
      this.editId = parseInt(options.diary_id)
      this.loadDiary()
    }
  },

  methods: {
    async loadDiary() {
      const { ok, data } = await api.getDiary(this.editId)
      if (ok) {
        this.form.content = data.content
        this.form.mood = data.mood
        this.form.images = data.images
        this.form.date = data.date
        this.form.visible_to_partner = data.visible_to_partner
      }
    },

    onMoodChange(e) { this.form.mood = MOODS[e.detail.value] },
    onDateChange(e) { this.form.date = e.detail.value },

    chooseImg() {
      uni.chooseImage({ count: 9 - this.form.images.length, sizeType: ['compressed'], success: (res) => {
        uni.showLoading({ title: '上传中' })
        const tasks = res.tempFilePaths.map(fp => api.uploadImage(fp))
        Promise.all(tasks).then(results => {
          uni.hideLoading()
          results.forEach(r => { if (r.ok) this.form.images.push(r.url) })
        })
      }})
    },
    delImg(i) { this.form.images.splice(i, 1) },

    imgThumb(u) {
      if (u && (u.startsWith('http://') || u.startsWith('https://'))) return u
      return 'http://47.93.241.64:8000' + u
    },

    async doSave() {
      if (!this.form.content.trim()) {
        uni.showToast({ title: '请输入日记内容', icon: 'none' })
        return
      }
      uni.showLoading({ title: '保存中' })
      const data = { ...this.form }
      const { ok, msg } = this.isEdit
        ? await api.updateDiary(this.editId, data)
        : await api.createDiary(data)
      uni.hideLoading()
      if (ok) {
        uni.showToast({ title: this.isEdit ? '已保存' : '日记已记录', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 800)
      } else {
        uni.showToast({ title: msg, icon: 'none' })
      }
    },

    async doDelete() {
      const { confirm } = await uni.showModal({ title: '删除日记', content: '确定要删除吗？' })
      if (!confirm) return
      const { ok } = await api.deleteDiary(this.editId)
      if (ok) { uni.showToast({ title: '已删除', icon: 'success' }); setTimeout(() => uni.navigateBack(), 800) }
    },
  },
}
</script>

<style scoped>
.page { padding: 30rpx; padding-bottom: 120rpx; }
.textarea {
  width: 100%; min-height: 320rpx;
  background: var(--card); border-radius: 16rpx;
  padding: 24rpx; font-size: 30rpx; line-height: 1.7;
}
.row { display: flex; align-items: center; justify-content: space-between; background: var(--card); border-radius: 16rpx; padding: 14rpx 24rpx; margin-top: 20rpx; }
.label { font-size: 28rpx; color: var(--muted); }
.picker { font-size: 28rpx; color: var(--text); }
.img-list { display: flex; flex-wrap: wrap; }
.img-item { width: 100rpx; height: 100rpx; border-radius: 12rpx; margin-left: 10rpx; }
.img-add {
  width: 100rpx; height: 100rpx;
  background: var(--input-bg); border-radius: 12rpx;
  margin-left: 10rpx;
  display: flex; align-items: center; justify-content: center;
  font-size: 44rpx; color: var(--muted);
}
.btn {
  width: 100%; height: 90rpx;
  background: var(--pink); color: #fff;
  border-radius: 16rpx; font-size: 32rpx;
  margin-top: 40rpx;
}
.danger { text-align: center; color: #e74c3c; font-size: 26rpx; margin-top: 30rpx; }
</style>
