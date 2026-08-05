// ========== 工具函数 ==========

/** 格式化日期为 yyyy-MM-dd */
export function formatDate(d) {
  const date = d ? new Date(d) : new Date()
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/** 计算倒计时天数：正数=还有几天，0=今天，负数=已过 */
export function daysLeft(dateStr) {
  const target = new Date(dateStr)
  const today = new Date(formatDate()) // 不带时分的今天
  return Math.ceil((target.getTime() - today.getTime()) / 86400000)
}

/** 倒计时文案 */
export function daysLeftText(dateStr) {
  const d = daysLeft(dateStr)
  if (d === 0) return '就是今天 🎉'
  if (d > 0) return `还有 ${d} 天`
  return `已过 ${Math.abs(d)} 天`
}

/** 心情标签的 emoji+文字映射 */
export const MOODS = ['开心 😊', '难过 😢', '想你 💕', '幸福 🥰', '生气 😤', '平淡 ☁️']
