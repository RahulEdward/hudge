/**
 * IPC Router — Routes Electron IPC messages between renderer and backend.
 */
const { ipcMain, BrowserWindow } = require('electron')
const http = require('http')
const https = require('https')

const BACKEND_URL = 'http://localhost:8000'

/**
 * Make an HTTP request to the backend API.
 */
function apiRequest(method, path, body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BACKEND_URL)
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      method,
      headers: { 'Content-Type': 'application/json' },
    }

    const req = http.request(options, (res) => {
      let data = ''
      res.on('data', (chunk) => (data += chunk))
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(data) })
        } catch {
          resolve({ status: res.statusCode, data })
        }
      })
    })

    req.on('error', (err) => reject(err))
    if (body) req.write(JSON.stringify(body))
    req.end()
  })
}

/**
 * Register all IPC handlers.
 */
function registerIpcHandlers() {
  // System
  ipcMain.handle('api:health', () => apiRequest('GET', '/health'))
  ipcMain.handle('api:status', () => apiRequest('GET', '/api/v1/health'))

  // Agents
  ipcMain.handle('api:agent-chat', (_e, { message, session_id }) =>
    apiRequest('POST', '/api/v1/agents/chat', { message, session_id })
  )
  ipcMain.handle('api:agent-status', () => apiRequest('GET', '/api/v1/agents/status'))

  // Market Data
  ipcMain.handle('api:market-quote', (_e, { symbol }) =>
    apiRequest('GET', `/api/v1/market/quote/${symbol}`)
  )
  ipcMain.handle('api:market-ohlc', (_e, { symbol, timeframe }) =>
    apiRequest('GET', `/api/v1/market/ohlc/${symbol}?timeframe=${timeframe || '1D'}`)
  )

  // Trading
  ipcMain.handle('api:execute-trade', (_e, order) =>
    apiRequest('POST', '/api/v1/trading/execute', order)
  )
  ipcMain.handle('api:cancel-order', (_e, { order_id }) =>
    apiRequest('POST', '/api/v1/trading/cancel', { order_id })
  )

  // Portfolio
  ipcMain.handle('api:portfolio-summary', () =>
    apiRequest('GET', '/api/v1/portfolio/summary')
  )
  ipcMain.handle('api:portfolio-positions', () =>
    apiRequest('GET', '/api/v1/portfolio/positions')
  )

  // Broker
  ipcMain.handle('api:broker-status', () =>
    apiRequest('GET', '/api/v1/broker/status')
  )
  ipcMain.handle('api:broker-connect', (_e, data) =>
    apiRequest('POST', '/api/v1/broker/connect', data)
  )
  ipcMain.handle('api:broker-disconnect', (_e, data) =>
    apiRequest('POST', '/api/v1/broker/disconnect', data)
  )

  // Backtest
  ipcMain.handle('api:run-backtest', (_e, params) =>
    apiRequest('POST', '/api/v1/backtest/run', params)
  )

  // Strategies
  ipcMain.handle('api:strategies-list', () =>
    apiRequest('GET', '/api/v1/strategies')
  )

  // Settings
  ipcMain.handle('api:get-config', () =>
    apiRequest('GET', '/api/v1/health')
  )

  console.log('[IPC Router] All handlers registered')
}

module.exports = { registerIpcHandlers, apiRequest }
