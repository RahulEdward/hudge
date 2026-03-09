# QUANT AI LAB — Security & Authentication Documentation

## Overview

Security is critical for a trading platform. The system uses Google OAuth for user authentication (like Claude desktop app), encrypts all sensitive data, protects broker credentials, and secures communication channels.

---

## User Authentication — Login with Google

The app uses **Google OAuth 2.0** as the primary authentication method. The experience mirrors Claude/Anthropic desktop app — a login popup opens inside the Electron window, and clicking "Login with Google" opens the system browser for Google sign-in, then redirects back into the app.

### Login Flow (Step by Step)

```
┌─────────────────────────────────────────────────────────┐
│                  ELECTRON APP LAUNCHES                   │
│                                                          │
│   ┌──────────────────────────────────────────────────┐  │
│   │              WELCOME POPUP WINDOW                 │  │
│   │                                                    │  │
│   │          ╔══════════════════════════╗              │  │
│   │          ║     QUANT AI LAB         ║              │  │
│   │          ║                          ║              │  │
│   │          ║   [🔵 Login with Google] ║              │  │
│   │          ║                          ║              │  │
│   │          ╚══════════════════════════╝              │  │
│   │                                                    │  │
│   └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

User clicks "Login with Google"
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│            SYSTEM BROWSER OPENS AUTOMATICALLY            │
│                                                          │
│   Google Sign-In Page:                                   │
│   ┌──────────────────────────────────────────────────┐  │
│   │  Sign in with Google                              │  │
│   │                                                    │  │
│   │  Choose an account:                               │  │
│   │    📧 user@gmail.com                              │  │
│   │    📧 another@gmail.com                           │  │
│   │                                                    │  │
│   │  "Quant AI Lab wants to access your account"      │  │
│   │                                                    │  │
│   │           [Allow]    [Cancel]                      │  │
│   └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

User clicks "Allow"
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│     BROWSER REDIRECTS TO: quant-ai-lab://auth/callback   │
│                                                          │
│     → Electron catches the deep link / localhost redirect │
│     → Auth code exchanged for tokens                     │
│     → User profile fetched from Google                   │
│     → Session created locally                            │
│     → Login popup closes                                 │
│     → Main app window loads with user logged in          │
└─────────────────────────────────────────────────────────┘

         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              MAIN APP — USER IS LOGGED IN                 │
│                                                          │
│   Welcome back, John! 👋                                 │
│   ┌─────────────────────────────────────────────────┐   │
│   │  Dashboard │ AI Chat │ Strategy Lab │ ...        │   │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

### Technical Implementation Details

#### 1. Google Cloud Console Setup

| Setting | Value |
|---------|-------|
| Application Type | Desktop App |
| OAuth Client Type | Web Application (for redirect) |
| Authorized Redirect URI | `http://localhost:5789/auth/callback` |
| Custom Protocol | `quant-ai-lab://auth/callback` (deep link) |
| Scopes | `openid`, `email`, `profile` |

#### 2. Electron Main Process — Auth Window

When the app starts:
1. Check for existing valid session (stored in Electron `safeStorage`)
2. If no session → show **Login Popup Window** (frameless, centered, 450×550px)
3. Login popup displays only one button: **"Login with Google"**
4. Main app window stays hidden until login succeeds

**Login Popup Properties:**
```
- Size: 450 × 550 px
- Frameless: true (no title bar — custom design)
- Resizable: false
- Center: true
- Background: dark gradient (#0a0a0a → #1a1a2e)
- Content: App logo + "Login with Google" button
- Always on top: true
```

#### 3. OAuth Flow — What Happens on "Login with Google" Click

```
Step 1: Generate OAuth URL
   ├── client_id from Google Cloud Console
   ├── redirect_uri = "http://localhost:5789/auth/callback"
   ├── scope = "openid email profile"
   ├── response_type = "code"
   ├── state = random_nonce (CSRF protection)
   ├── code_challenge = PKCE S256 hash
   └── access_type = "offline" (for refresh token)

Step 2: Start local HTTP server on port 5789
   └── Listens for the OAuth callback redirect

Step 3: Open system default browser
   └── URL: https://accounts.google.com/o/oauth2/v2/auth?...

Step 4: User signs in on Google's page → clicks "Allow"

Step 5: Google redirects to:
   └── http://localhost:5789/auth/callback?code=AUTH_CODE&state=NONCE

Step 6: Local server catches the redirect
   ├── Validate state matches (CSRF check)  
   ├── Exchange auth code for tokens:
   │     POST https://oauth2.googleapis.com/token
   │     Body: code, client_id, client_secret, redirect_uri, grant_type
   │     Response: { access_token, refresh_token, id_token, expires_in }
   ├── Decode id_token (JWT) to get user info:
   │     { sub, email, name, picture }
   └── Shut down local server

Step 7: Store session
   ├── Access token → Electron safeStorage (encrypted)
   ├── Refresh token → Electron safeStorage (encrypted)
   ├── User profile → local SQLite DB
   └── Session expiry timestamp

Step 8: Close login popup → Show main app window
   └── User lands on Dashboard, fully authenticated
```

#### 4. Deep Link Alternative (Optional)

Instead of a localhost redirect, the app can register a custom protocol:

```
Protocol: quant-ai-lab://
Redirect: quant-ai-lab://auth/callback?code=AUTH_CODE&state=NONCE
```

Electron registers the protocol handler on app install. When Google redirects to `quant-ai-lab://...`, the OS opens Electron directly.

**Pros:** No local HTTP server needed, works even if port is busy
**Cons:** Requires protocol registration during install

---

### Session Management

| Feature | Details |
|---------|---------|
| Session Storage | Electron `safeStorage` API (OS-level encryption) |
| Access Token Expiry | 1 hour (Google default) |
| Refresh Token | Stored encrypted, used to get new access tokens silently |
| Auto-Refresh | Background refresh 5 minutes before expiry |
| Session Persist | User stays logged in across app restarts |
| Logout | Clears all tokens from safeStorage, shows login popup |
| Multi-Account | Not supported (single user desktop app) |

### Login Popup UI Design

```
┌─────────────────────────────────────┐
│                                     │
│           ◆ QUANT AI LAB            │
│      Autonomous Trading Platform     │
│                                     │
│     ┌───────────────────────────┐   │
│     │                           │   │
│     │    🧪  (App Logo/Icon)    │   │
│     │                           │   │
│     └───────────────────────────┘   │
│                                     │
│   ┌─────────────────────────────┐   │
│   │  🔵  Continue with Google   │   │
│   └─────────────────────────────┘   │
│                                     │
│        By continuing you agree       │
│        to our Terms of Service       │
│                                     │
│             v1.0.0                   │
└─────────────────────────────────────┘

 Style:
 - Dark background (#0a0a0a)
 - Glassmorphism card with blur
 - Google button: white bg, Google G icon, dark text
 - Subtle gradient glow behind logo
 - Micro-animation: logo pulse on load
```

---

### After Login — Backend Auth

Once the user logs in via Google:

1. **Frontend** stores the Google `id_token` and `access_token`
2. **Backend API** receives the Google `id_token` on first request:
   - Verifies token with Google's public keys
   - Extracts user email + profile
   - Creates local user record in SQLite (if first login)
   - Issues app-level JWT (access + refresh tokens)
3. **All subsequent API calls** use the app-level JWT
4. **Token refresh** happens automatically via refresh token

**API Flow:**
```
POST /api/v1/auth/google
Body: { "id_token": "eyJ..." }
Response: {
  "access_token": "app_jwt...",
  "refresh_token": "app_refresh...",
  "user": {
    "email": "user@gmail.com",
    "name": "John Doe",
    "picture": "https://lh3.googleusercontent.com/..."
  }
}
```

---

## Credential Encryption

### Fernet Symmetric Encryption

All API keys, passwords, and secrets (broker credentials, LLM keys) are encrypted at rest:

```python
from cryptography.fernet import Fernet

class CredentialManager:
    def __init__(self):
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        return self.cipher.decrypt(ciphertext.encode()).decode()
```

### Key Storage
- Encryption key stored in user's home directory: `~/.quant_lab/secret.key`
- Key file has restricted permissions (user-only read)
- Never committed to version control

---

## Session Security

### WhatsApp Sessions
- Session credentials stored encrypted in `configs/.whatsapp_session/`
- Auto-expire after 14 days of inactivity
- Re-authentication requires new QR scan

### Telegram Sessions
- Bot token stored encrypted
- Authorized user whitelist in config

### Broker Sessions
- Token refresh handled automatically
- Sessions invalidated on logout
- Multi-factor support (TOTP for Angel One)

---

## Data Protection

### At Rest
- SQLite database encrypted with SQLCipher (optional)
- Config files with credentials are encrypted via Fernet
- ML model files stored with checksums
- Google tokens encrypted via Electron `safeStorage`

### In Transit
- Backend API uses HTTPS in production
- WebSocket connections use WSS
- Broker API calls use TLS
- Google OAuth uses PKCE (Proof Key for Code Exchange)

---

## Access Control

- **Google OAuth** required to access the app (no anonymous usage)
- Single-user mode by default (desktop app)
- Broker access requires explicit login after app login
- Trade execution requires user approval (configurable)

---

## Audit Trail

All actions are logged:
- Google login events with timestamps
- API requests with user identity
- Trade executions with full details
- Agent activities and decisions
- Configuration changes

---

## Security Checklist

- [ ] Google OAuth Client ID configured in Google Cloud Console
- [ ] Redirect URI registered (`http://localhost:5789/auth/callback`)
- [ ] Electron `safeStorage` used for token storage
- [ ] Encryption key generated and secured
- [ ] Broker credentials encrypted
- [ ] LLM API keys encrypted
- [ ] WhatsApp session encrypted
- [ ] Telegram bot token encrypted
- [ ] CORS origins restricted to localhost
- [ ] Rate limiting enabled
- [ ] Audit logging active
