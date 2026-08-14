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
  /* 主题变量（默认白色主题，theme.js 会按主题覆盖） */
  --bg: #f5f5f5; --card: #ffffff; --pink: #f8a5c2; --hot: #ff6b9d; --purple: #8b5cf6;
  --text: #333333; --muted: #999999; --border: #f0f0f0; --input-bg: #f5f5f5;
  --pink-soft: #fff0f5; --purple-soft: #f3ecff;
  background-color: var(--bg);
  font-size: 15px;
  color: var(--text);
}
</style>
