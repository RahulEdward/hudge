/**
 * Window Manager — manages login, main, and popup windows for the Electron app.
 */
const { BrowserWindow, screen } = require('electron')
const path = require('path')

const isDev = process.env.NODE_ENV === 'development' || !require('electron').app.isPackaged

let loginWindow = null
let mainWindow = null
const windowState = { x: undefined, y: undefined, width: 1400, height: 900 }

/**
 * Create the login popup window.
 */
function createLoginWindow() {
  if (loginWindow) {
    loginWindow.focus()
    return loginWindow
  }

  loginWindow = new BrowserWindow({
    width: 450,
    height: 550,
    resizable: false,
    frame: false,
    center: true,
    backgroundColor: '#0a0a0f',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  })

  const loginUrl = isDev
    ? 'http://localhost:3000/login'
    : `file://${path.join(__dirname, '../build/login.html')}`

  loginWindow.loadURL(loginUrl)

  loginWindow.on('closed', () => {
    loginWindow = null
  })

  return loginWindow
}

/**
 * Create the main application window.
 */
function createMainWindow() {
  if (mainWindow) {
    mainWindow.focus()
    return mainWindow
  }

  // Restore saved state
  const { width, height } = screen.getPrimaryDisplay().workAreaSize

  mainWindow = new BrowserWindow({
    x: windowState.x,
    y: windowState.y,
    width: Math.min(windowState.width, width),
    height: Math.min(windowState.height, height),
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
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../build/index.html')}`

  mainWindow.loadURL(url)

  if (isDev) {
    mainWindow.webContents.openDevTools()
  }

  // Save window state on resize/move
  mainWindow.on('resize', () => saveWindowState())
  mainWindow.on('move', () => saveWindowState())

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  mainWindow.on('minimize', (e) => {
    e.preventDefault()
    mainWindow.hide()
  })

  return mainWindow
}

/**
 * Save window position and size.
 */
function saveWindowState() {
  if (!mainWindow) return
  const bounds = mainWindow.getBounds()
  windowState.x = bounds.x
  windowState.y = bounds.y
  windowState.width = bounds.width
  windowState.height = bounds.height
}

/**
 * Transition from login to main window.
 */
function transitionToMain() {
  if (loginWindow) {
    loginWindow.close()
  }
  return createMainWindow()
}

/**
 * Get the main window instance.
 */
function getMainWindow() {
  return mainWindow
}

/**
 * Get the login window instance.
 */
function getLoginWindow() {
  return loginWindow
}

module.exports = {
  createLoginWindow,
  createMainWindow,
  transitionToMain,
  getMainWindow,
  getLoginWindow,
}
