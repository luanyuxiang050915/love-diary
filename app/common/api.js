// ========== API 请求封装：统一发请求、带 token、401 跳登录 ==========
import store from './store.js'

// ---------- 服务器地址 ----------
// 开发期：手机和服务器不在同一网络，所以填公网 IP
const BASE_URL = 'http://47.93.241.64:8000'

/**
 * 通用请求函数。
 * @param {string} path   - 接口路径（如 /api/auth/login）
 * @param {string} method - GET / POST / PUT / DELETE
 * @param {object} data   - 请求体（POST/PUT 时用）
 * @param {boolean} auth  - 是否需要登录令牌（默认 true）
 * @returns {Promise<object>} - { ok, data, msg }
 */
function request(path, method = 'GET', data = null, auth = true) {
  return new Promise((resolve) => {
    const headers = { 'Content-Type': 'application/json' }
    if (auth) {
      const token = store.getToken()
      if (!token) {
        uni.reLaunch({ url: '/pages/login/login' })
        resolve({ ok: false, msg: '未登录' })
        return
      }
      headers['Authorization'] = `Bearer ${token}`
    }

    uni.request({
      url: BASE_URL + path,
      method,
      header: headers,
      data,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve({ ok: true, data: res.data })
        } else if (res.statusCode === 401) {
          store.logout()
          uni.reLaunch({ url: '/pages/login/login' })
          resolve({ ok: false, msg: '登录过期，请重新登录' })
        } else {
          let msg = res.data?.detail || '请求失败'
          // FastAPI 参数校验错误的 detail 是数组，转成可读文案
          if (Array.isArray(msg)) {
            msg = msg.map(d => (d && d.msg) || '参数有误').filter(Boolean).join('；')
          }
          resolve({ ok: false, msg })
        }
      },
      fail(err) {
        resolve({ ok: false, msg: `网络错误：${err.errMsg}` })
      },
    })
  })
}

// ---------- 导出每个接口为一个函数，页面直接调 ----------

// 用户
export const register = (data) => request('/api/auth/register', 'POST', data, false)
export const login = (data) => request('/api/auth/login', 'POST', data, false)
export const getMe = () => request('/api/me')
export const updateMe = (data) => request('/api/me', 'PUT', data)
export const changePassword = (data) => request('/api/auth/password', 'PUT', data)
export const getLoginLogs = () => request('/api/login-logs')

// 日记
export const createDiary = (data) => request('/api/diaries', 'POST', data)
export const listDiaries = (params) => {
  let url = '/api/diaries?'
  if (params?.date) url += `date=${params.date}&`
  if (params?.page) url += `page=${params.page}`
  return request(url)
}
export const getDiary = (id) => request(`/api/diaries/${id}`)
export const updateDiary = (id, data) => request(`/api/diaries/${id}`, 'PUT', data)
export const deleteDiary = (id) => request(`/api/diaries/${id}`, 'DELETE')

// 纪念日
export const createAnniversary = (data) => request('/api/anniversaries', 'POST', data)
export const listAnniversaries = () => request('/api/anniversaries')
export const updateAnniversary = (id, data) => request(`/api/anniversaries/${id}`, 'PUT', data)
export const deleteAnniversary = (id) => request(`/api/anniversaries/${id}`, 'DELETE')

// 图片上传（uni.uploadFile 不走 request，单独封装）
export function uploadImage(filePath) {
  return new Promise((resolve) => {
    const token = store.getToken()
    uni.uploadFile({
      url: BASE_URL + '/api/upload',
      filePath,
      name: 'file',
      header: { Authorization: `Bearer ${token}` },
      success(res) {
        try {
          const d = JSON.parse(res.data)
          resolve({ ok: true, url: d.url })
        } catch {
          resolve({ ok: false, msg: '上传解析失败' })
        }
      },
      fail(err) {
        resolve({ ok: false, msg: `上传失败：${err.errMsg}` })
      },
    })
  })
}

// 绑定
export const getBindCode = () => request('/api/bind/code', 'POST')
export const acceptBind = (code) => request('/api/bind/accept', 'POST', { code })
export const getPartnerDiaries = () => request('/api/partner/diaries')

// 戳一戳
export const sendPoke = () => request('/api/pokes', 'POST')
export const getPokes = () => request('/api/pokes')
export const getPokeUnread = () => request('/api/pokes/unread')
export const readPokes = () => request('/api/pokes/read', 'POST')

// 心愿清单
export const listWishes = () => request('/api/wishes')
export const createWish = (content) => request('/api/wishes', 'POST', { content })
export const toggleWish = (id) => request(`/api/wishes/${id}/done`, 'PUT')
export const deleteWish = (id) => request(`/api/wishes/${id}`, 'DELETE')

// 爱的打卡
export const doCheckin = () => request('/api/checkins', 'POST')
export const getCheckin = (params) => {
  let url = '/api/checkins'
  if (params?.month) url += `?month=${params.month}`
  return request(url)
}
export const getPartnerCheckin = (params) => {
  let url = '/api/checkins/partner'
  if (params?.month) url += `?month=${params.month}`
  return request(url)
}

// 悄悄话
export const listWhispers = () => request('/api/whispers')
export const sendWhisper = (content) => request('/api/whispers', 'POST', { content })

// 心情月报
export const getMoodReport = (month) => request(`/api/stats/moods${month ? '?month=' + month : ''}`)

// 每日一签（每人每天只能抽一次）
export const getTodayFortune = () => request('/api/fortunes/today')
export const drawFortune = () => request('/api/fortunes/draw', 'POST')

// 双人聊天
export const sendMessage = (data) => request('/api/messages', 'POST', data)
export const listMessages = (afterId = 0) => request(`/api/messages?after_id=${afterId}&limit=200`)

// 共享相册
export const addAlbumPhoto = (data) => request('/api/album', 'POST', data)
export const listAlbum = () => request('/api/album')
export const updateAlbumPhoto = (id, data) => request(`/api/album/${id}`, 'PUT', data)
export const deleteAlbumPhoto = (id) => request(`/api/album/${id}`, 'DELETE')

// 自定义表情包
export const addSticker = (url) => request('/api/stickers', 'POST', { url })
export const listStickers = () => request('/api/stickers')
export const deleteSticker = (id) => request(`/api/stickers/${id}`, 'DELETE')
