// ========== 全局状态管理（token / 用户信息）==========

const KEYS = { token: 'token', user: 'user' }

export default {
  // 检查已登录
  hasLogin() {
    return !!uni.getStorageSync(KEYS.token)
  },

  // 获取 token
  getToken() {
    return uni.getStorageSync(KEYS.token) || ''
  },

  // 获取缓存的用户信息
  getUser() {
    const raw = uni.getStorageSync(KEYS.user)
    return raw ? JSON.parse(raw) : null
  },

  // 登录成功：存 token + 用户信息
  login(token, user) {
    uni.setStorageSync(KEYS.token, token)
    uni.setStorageSync(KEYS.user, JSON.stringify(user))
  },

  // 更新用户信息（改昵称/头像后）
  updateUser(user) {
    uni.setStorageSync(KEYS.user, JSON.stringify(user))
  },

  // 退出登录
  logout() {
    uni.removeStorageSync(KEYS.token)
    uni.removeStorageSync(KEYS.user)
  },
}
