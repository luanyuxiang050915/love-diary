// ========== 主题：白色 / 暗色 / 浅粉 / 香芋紫 ==========

const THEMES = {
  light: {
    '--bg': '#f5f5f5', '--card': '#ffffff', '--pink': '#f8a5c2', '--hot': '#ff6b9d',
    '--purple': '#8b5cf6', '--text': '#333333', '--muted': '#999999', '--border': '#f0f0f0',
    '--input-bg': '#f5f5f5', '--pink-soft': '#fff0f5', '--purple-soft': '#f3ecff',
    navBg: '#ffffff', navFront: '#000000', tabBorder: 'black',
  },
  dark: {
    '--bg': '#12121f', '--card': '#1d1d2e', '--pink': '#f8a5c2', '--hot': '#ff6b9d',
    '--purple': '#a78bfa', '--text': '#e8e8f0', '--muted': '#8a8aa0', '--border': '#2a2a3e',
    '--input-bg': '#26263a', '--pink-soft': '#33222e', '--purple-soft': '#2a2238',
    navBg: '#1d1d2e', navFront: '#ffffff', tabBorder: 'white',
  },
  pink: {
    '--bg': '#fff5f7', '--card': '#ffffff', '--pink': '#f8a5c2', '--hot': '#ff6b9d',
    '--purple': '#c084fc', '--text': '#4a3a40', '--muted': '#b08f9a', '--border': '#ffe4ec',
    '--input-bg': '#fff0f4', '--pink-soft': '#ffeef4', '--purple-soft': '#f7efff',
    navBg: '#fff5f7', navFront: '#000000', tabBorder: 'black',
  },
  purple: {
    '--bg': '#f7f5fc', '--card': '#ffffff', '--pink': '#a98fe8', '--hot': '#8b6fd8',
    '--purple': '#8b5cf6', '--text': '#3c3650', '--muted': '#948fb0', '--border': '#e9e4f5',
    '--input-bg': '#f2effa', '--pink-soft': '#efe9fb', '--purple-soft': '#e7e0f8',
    navBg: '#f7f5fc', navFront: '#000000', tabBorder: 'black',
  },
}

export const THEME_NAMES = [
  { key: 'light', label: '白色', emoji: '☀️' },
  { key: 'dark', label: '暗色', emoji: '🌙' },
  { key: 'pink', label: '浅粉', emoji: '🌸' },
  { key: 'purple', label: '香芋紫', emoji: '🍠' },
]

export function getThemeName() {
  return uni.getStorageSync('theme') || 'light'
}

export function setThemeName(name) {
  uni.setStorageSync('theme', name)
}

/** 生成当前主题的 CSS 变量字符串，绑定到每个页面根 view 的 :style 上 */
export function themeCssVars(name) {
  const t = THEMES[name] || THEMES.light
  return Object.keys(t)
    .filter(k => k.startsWith('--'))
    .map(k => `${k}:${t[k]}`)
    .join(';')
}

/**
 * 应用主题到原生层：
 * 1. 导航栏颜色
 * 2. 底部 TabBar 颜色
 * 3. H5 环境同时把 CSS 变量写到 page 上（App 原生环境由各页面根 view 的 :style 接管）
 */
export function applyTheme(name) {
  const t = THEMES[name] || THEMES[getThemeName()] || THEMES.light

  if (typeof document !== 'undefined') {
    const root = document.querySelector('page') || document.documentElement
    if (root) {
      Object.keys(t).forEach(k => {
        if (!k.startsWith('--')) return
        root.style.setProperty(k, t[k])
      })
    }
  }

  try {
    uni.setNavigationBarColor({
      frontColor: t.navFront,
      backgroundColor: t.navBg,
      animation: { duration: 200, timingFunc: 'easeInOut' },
    })
  } catch (e) { /* 个别平台不支持时忽略 */ }

  try {
    uni.setTabBarStyle({
      color: t['--muted'],
      selectedColor: t['--pink'],
      backgroundColor: t['--card'],
      borderStyle: t.tabBorder || 'black',
    })
  } catch (e) { /* 非 TabBar 页面调用无副作用 */ }
}

/** 全局 mixin：让每个页面根 view 都能拿到主题 CSS 变量，并在 onShow 时同步 */
export const themeMixin = {
  data() {
    return { cssVars: themeCssVars(getThemeName()) }
  },
  onShow() {
    this.cssVars = themeCssVars(getThemeName())
    applyTheme(getThemeName())
  },
}

export default { THEMES, THEME_NAMES, getThemeName, setThemeName, themeCssVars, applyTheme, themeMixin }
