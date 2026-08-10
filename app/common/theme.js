// ========== 主题：白色 / 暗色 / 浅粉 / 香芋紫 ==========

const THEMES = {
  light: {
    '--bg': '#f5f5f5', '--card': '#ffffff', '--pink': '#f8a5c2', '--hot': '#ff6b9d',
    '--text': '#333333', '--muted': '#999999', '--border': '#f0f0f0', '--input-bg': '#f5f5f5',
    '--pink-soft': '#fff0f5', '--purple-soft': '#f3ecff',
    navBg: '#ffffff', navFront: '#000000',
  },
  dark: {
    '--bg': '#12121f', '--card': '#1d1d2e', '--pink': '#f8a5c2', '--hot': '#ff6b9d',
    '--text': '#e8e8f0', '--muted': '#8a8aa0', '--border': '#2a2a3e', '--input-bg': '#26263a',
    '--pink-soft': '#33222e', '--purple-soft': '#2a2238',
    navBg: '#1d1d2e', navFront: '#ffffff',
  },
  pink: {
    '--bg': '#fff5f7', '--card': '#ffffff', '--pink': '#f8a5c2', '--hot': '#ff6b9d',
    '--text': '#4a3a40', '--muted': '#b08f9a', '--border': '#ffe4ec', '--input-bg': '#fff0f4',
    '--pink-soft': '#ffeef4', '--purple-soft': '#f7efff',
    navBg: '#fff5f7', navFront: '#000000',
  },
  purple: {
    '--bg': '#f7f5fc', '--card': '#ffffff', '--pink': '#a98fe8', '--hot': '#8b6fd8',
    '--text': '#3c3650', '--muted': '#948fb0', '--border': '#e9e4f5', '--input-bg': '#f2effa',
    '--pink-soft': '#efe9fb', '--purple-soft': '#e7e0f8',
    navBg: '#f7f5fc', navFront: '#000000',
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

/** 把主题色应用到当前页面（每个页面 onShow 时调用一次） */
export function applyTheme(name) {
  const t = THEMES[name] || THEMES.light
  const root = (typeof document !== 'undefined')
    ? (document.querySelector('page') || document.documentElement)
    : null
  if (root) {
    Object.keys(t).forEach(k => {
      if (k !== 'navBg' && k !== 'navFront') root.style.setProperty(k, t[k])
    })
  }
  try {
    uni.setNavigationBarColor({
      frontColor: t.navFront,
      backgroundColor: t.navBg,
      animation: { duration: 200, timingFunc: 'easeInOut' },
    })
  } catch (e) { /* 个别平台不支持时忽略 */ }
}

export default { THEMES, THEME_NAMES, getThemeName, setThemeName, applyTheme }
