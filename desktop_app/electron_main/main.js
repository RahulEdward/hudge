const { app, BrowserWindow, ipcMain, Tray, Menu } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const http = require('http')

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged
const BACKEND_PORT = 8000
const FRONTEND_PORT = 3000

let mainWindow = null
let backendProcess = null
let tray = null

// ─── Backend Management ───────────────────────────────────────────────────────

function startBackend() {
  if (isDev) {
    console.log('[Main] Development mode — expecting backend at localhost:8000')
    return
  }

  const backendPath = path.join(process.resourcesPath, 'backend', 'quant-lab-backend.exe')
  console.log(`[Main] Starting backend: ${backendPath}`)

  backendProcess = spawn(backendPath, [], {
    cwd: path.dirname(backendPath),
    stdio: 'pipe',
  })

  backendProcess.stdout.on('data', (data) => console.log(`[Backend] ${data}`))
  backendProcess.stderr.on('data', (data) => console.error(`[Backend ERR] ${data}`))
  backendProcess.on('exit', (code) => console.log(`[Backend] Exited with code ${code}`))
}

function waitForBackend(retries = 30) {
  return new Promise((resolve, reject) => {
    const check = (remaining) => {
      const req = http.get(`http://localhost:${BACKEND_PORT}/health`, (res) => {
        if (res.statusCode === 200) resolve()
        else if (remaining > 0) setTimeout(() => check(remaining - 1), 1000)
        else reject(new Error('Backend did not start'))
      })
      req.on('error', () => {
        if (remaining > 0) setTimeout(() => check(remaining - 1), 1000)
        else reject(new Error('Backend health check failed'))
      })
    }
    check(retries)
  })
}

// ─── Window Management ────────────────────────────────────────────────────────

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    backgroundColor: '#0a0a0f',
    frame: true,
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    icon: path.join(__dirname, '../public/icon.png'),
  })

  const url = isDev
    ? `http://localhost:${FRONTEND_PORT}`
    : `file://${path.join(__dirname, '../build/index.html')}`

  mainWindow.loadURL(url)

  if (isDev) {
    mainWindow.webContents.openDevTools()
  }

  mainWindow.on('closed', () => { mainWindow = null })

  mainWindow.on('minimize', (e) => {
    e.preventDefault()
    mainWindow.hide()
  })
}

// ─── Tray ─────────────────────────────────────────────────────────────────────

function createTray() {
  const iconPath = path.join(__dirname, '../public/icon.png')
  try {
    tray = new Tray(iconPath)
    tray.setToolTip('Quant AI Lab')
    tray.setContextMenu(Menu.buildFromTemplate([
      { label: 'Open', click: () => { if (mainWindow) mainWindow.show() } },
      { type: 'separator' },
      { label: 'Quit', click: () => app.quit() },
    ]))
    tray.on('click', () => { if (mainWindow) mainWindow.show() })
  } catch (e) {
    console.warn('[Tray] Could not create tray icon:', e.message)
  }
}

// ─── App Lifecycle ────────────────────────────────────────────────────────────

app.whenReady().then(async () => {
  startBackend()

  console.log('[Main] Waiting for backend...')
  try {
    await waitForBackend()
    console.log('[Main] Backend ready')
  } catch (e) {
    console.warn('[Main] Backend not available:', e.message)
  }

  createMainWindow()
  createTray()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (!mainWindow) createMainWindow()
})

app.on('before-quit', () => {
  if (backendProcess) {
    console.log('[Main] Stopping backend process')
    backendProcess.kill()
  }
})

// ─── IPC Handlers ─────────────────────────────────────────────────────────────

ipcMain.handle('get-backend-url', () => `http://localhost:${BACKEND_PORT}`)
ipcMain.handle('get-app-version', () => app.getVersion())

ipcMain.handle('minimize-to-tray', () => {
  if (mainWindow) mainWindow.hide()
})
