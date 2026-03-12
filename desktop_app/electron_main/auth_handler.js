/**
 * Auth Handler — Google OAuth 2.0 flow with PKCE for Electron desktop app.
 */
const { BrowserWindow } = require('electron')
const http = require('http')
const crypto = require('crypto')
const url = require('url')

const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID || ''
const REDIRECT_PORT = 5789
const REDIRECT_URI = `http://localhost:${REDIRECT_PORT}/callback`

let authWindow = null

/**
 * Generate PKCE code verifier and challenge.
 */
function generatePKCE() {
  const verifier = crypto.randomBytes(32).toString('base64url')
  const challenge = crypto.createHash('sha256').update(verifier).digest('base64url')
  return { verifier, challenge }
}

/**
 * Start the Google OAuth flow.
 */
function startGoogleAuth() {
  return new Promise((resolve, reject) => {
    const { verifier, challenge } = generatePKCE()

    // Start local HTTP server for OAuth callback
    const server = http.createServer((req, res) => {
      const parsed = url.parse(req.url, true)
      if (parsed.pathname === '/callback') {
        const code = parsed.query.code
        const error = parsed.query.error

        res.writeHead(200, { 'Content-Type': 'text/html' })
        res.end(`
          <html>
            <body style="background:#0a0a0f;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif">
              <div style="text-align:center">
                <h2>${error ? '❌ Auth Failed' : '✅ Authenticated'}</h2>
                <p>You can close this window</p>
              </div>
            </body>
          </html>
        `)

        server.close()
        if (authWindow) {
          authWindow.close()
          authWindow = null
        }

        if (error) {
          reject(new Error(error))
        } else {
          resolve({ code, verifier })
        }
      }
    })

    server.listen(REDIRECT_PORT, () => {
      const authUrl =
        `https://accounts.google.com/o/oauth2/v2/auth?` +
        `client_id=${GOOGLE_CLIENT_ID}&` +
        `redirect_uri=${encodeURIComponent(REDIRECT_URI)}&` +
        `response_type=code&` +
        `scope=${encodeURIComponent('openid email profile')}&` +
        `code_challenge=${challenge}&` +
        `code_challenge_method=S256`

      // Open auth window
      authWindow = new BrowserWindow({
        width: 500,
        height: 700,
        show: true,
        frame: true,
        webPreferences: { nodeIntegration: false },
      })

      authWindow.loadURL(authUrl)
      authWindow.on('closed', () => {
        authWindow = null
        server.close()
      })
    })

    server.on('error', (err) => {
      console.error('[Auth] Server error:', err)
      reject(err)
    })
  })
}

/**
 * Exchange auth code for tokens via backend.
 */
async function exchangeToken(code, verifier) {
  const { apiRequest } = require('./ipc_router')
  try {
    const result = await apiRequest('POST', '/api/v1/auth/google', {
      id_token: code,
    })
    return result.data
  } catch (err) {
    console.error('[Auth] Token exchange failed:', err)
    return null
  }
}

/**
 * Store token securely using Electron safe storage.
 */
function storeToken(token) {
  try {
    const { safeStorage } = require('electron')
    if (safeStorage.isEncryptionAvailable()) {
      const encrypted = safeStorage.encryptString(JSON.stringify(token))
      const fs = require('fs')
      const path = require('path')
      const tokenPath = path.join(require('electron').app.getPath('userData'), '.auth_token')
      fs.writeFileSync(tokenPath, encrypted)
      return true
    }
  } catch (err) {
    console.error('[Auth] Token storage failed:', err)
  }
  return false
}

/**
 * Load stored token.
 */
function loadToken() {
  try {
    const { safeStorage } = require('electron')
    const fs = require('fs')
    const path = require('path')
    const tokenPath = path.join(require('electron').app.getPath('userData'), '.auth_token')
    if (fs.existsSync(tokenPath)) {
      const encrypted = fs.readFileSync(tokenPath)
      const decrypted = safeStorage.decryptString(encrypted)
      return JSON.parse(decrypted)
    }
  } catch {}
  return null
}

module.exports = { startGoogleAuth, exchangeToken, storeToken, loadToken }
