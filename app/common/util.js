// ========== 工具函数 ==========

import { getFestivals } from './lunar.js'

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

/** 纪念日类型 → 颜色 / 文案（label 自带 emoji，用于类型选择器与日历图例） */
export const ANNIV_KINDS = [
  { key: 'love', label: '❤️ 恋爱', color: '#f8a5c2' },
  { key: 'birthday', label: '🎂 生日', color: '#f59e0b' },
  { key: 'trip', label: '✈️ 旅行', color: '#10b981' },
  { key: 'memory', label: '📸 纪念', color: '#8b5cf6' },
  { key: 'other', label: '📌 其他', color: '#64748b' },
]

export function annivKindMeta(kind) {
  return ANNIV_KINDS.find(k => k.key === kind) || ANNIV_KINDS[4]
}

/** 公历节日（月-日 → 名称） */
export const SOLAR_HOLIDAYS = {
  '1-1': '元旦',
  '2-14': '情人节',
  '3-8': '妇女节',
  '3-12': '植树节',
  '4-1': '愚人节',
  '5-1': '劳动节',
  '5-4': '青年节',
  '6-1': '儿童节',
  '7-1': '建党节',
  '8-1': '建军节',
  '9-10': '教师节',
  '10-1': '国庆节',
  '12-24': '平安夜',
  '12-25': '圣诞节',
}

/** 获取某天的节日名称：公历节日优先，其次农历节日（春节/端午/中秋等），无则返回 '' */
export function festivalOf(dateStr) {
  const parts = String(dateStr || '').split('-').map(Number)
  if (parts.length < 3 || parts.some(isNaN)) return ''
  const [y, m, d] = parts
  const solar = SOLAR_HOLIDAYS[`${m}-${d}`]
  if (solar) return solar
  const fs = getFestivals(y, m, d)
  return Array.isArray(fs) && fs.length ? fs[0] : ''
}

/** 某年某月的天数（m 为 1~12） */
export function daysInMonth(y, m) {
  return new Date(y, m, 0).getDate()
}
