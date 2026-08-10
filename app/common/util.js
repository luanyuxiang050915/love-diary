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
export const MOODS = ['心动 💓', '得意 😎', '开心 😊', '平静 😌', '无聊 😑', '累了 😫', '孤独 🥺', '丧 😞', '伤心 😢', '烦躁 😣', '生气 😤']

/** 纪念日类型 → 颜色 / 文案（日历着色用） */
export const ANNIV_KINDS = [
  { key: 'love', label: '恋爱', color: '#f8a5c2' },
  { key: 'birthday', label: '生日', color: '#f59e0b' },
  { key: 'trip', label: '旅行', color: '#10b981' },
  { key: 'memory', label: '纪念', color: '#8b5cf6' },
  { key: 'other', label: '其他', color: '#64748b' },
]

export function annivKindMeta(kind) {
  return ANNIV_KINDS.find(k => k.key === kind) || ANNIV_KINDS[4]
}

/** 某年某月的天数（m 为 1~12） */
export function daysInMonth(y, m) {
  return new Date(y, m, 0).getDate()
}
