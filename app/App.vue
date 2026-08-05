<script>
import store from './common/store.js'

export default {
  onLaunch() {
    // App 启动时检查是否已登录：有 token 免登录，直接进主页
    if (!store.hasLogin()) {
      uni.reLaunch({ url: '/pages/login/login' })
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
