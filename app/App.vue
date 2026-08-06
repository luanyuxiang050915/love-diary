<script>
import store from './common/store.js'

export default {
  onLaunch() {
    // 已登录 → 直接进主页；未登录 → 留在登录页（pages.json 首页）
    if (store.hasLogin()) {
      uni.reLaunch({ url: '/pages/diary/list' })
    }
  },
}
</script>

<style>
/* 全局基础样式 */
page {
  background-color: #f5f5f5;
  font-size: 15px;
  color: #333;
}
</style>
