# QUANT AI LAB — Build & Packaging Documentation

## Overview

The final deliverable is a Windows desktop application installer (.EXE) that bundles:
- Electron frontend (React + Next.js)
- Python backend (FastAPI) as a standalone executable
- All configuration and resource files

---

## Build Architecture

```
┌─────────────────────────────────────────────────┐
│         Quant AI Lab Setup.exe (Installer)       │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │  Electron App Shell                         │  │
│  │  ├── main.js (Electron main process)       │  │
│  │  ├── renderer/ (React/Next.js bundle)      │  │
│  │  └── resources/                            │  │
│  │       └── backend/ (PyInstaller bundle)    │  │
│  │            ├── quant-lab-backend.exe        │  │
│  │            ├── configs/                     │  │
│  │            └── database/                   │  │
│  └────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Step 1: Bundle Python Backend (PyInstaller)

### Command
```bash
cd d:\quant-lab\backend
pyinstaller --onedir \
  --name quant-lab-backend \
  --add-data "../configs;configs" \
  --add-data "../database;database" \
  --hidden-import uvicorn.logging \
  --hidden-import uvicorn.loops.auto \
  --hidden-import uvicorn.protocols.http.auto \
  --hidden-import uvicorn.protocols.websockets.auto \
  --hidden-import uvicorn.lifespan.on \
  api_server/main.py
```

### Output
```
dist/
└── quant-lab-backend/
    ├── quant-lab-backend.exe
    ├── _internal/
    │   ├── python3.11 runtime
    │   ├── all pip packages
    │   └── stdlib
    ├── configs/
    └── database/
```

### Notes
- `--onedir` bundles into a directory (faster startup than `--onefile`)
- All Python dependencies are bundled (no Python installation needed)
- Hidden imports ensure uvicorn/FastAPI workers are included
- ML model files (.pkl, .pt) are included via `--add-data`

---

## Step 2: Build React/Next.js Frontend

### Commands
```bash
cd d:\quant-lab\desktop_app\renderer
npm run build
# Output: .next/ or out/ directory
```

### Build Configuration (`next.config.js`)
```javascript
module.exports = {
  output: 'export',    // Static export for Electron
  distDir: 'build',
  images: { unoptimized: true },
  trailingSlash: true,
}
```

---

## Step 3: Configure Electron Builder

### `electron-builder.yml`
```yaml
appId: "com.quantailab.desktop"
productName: "Quant AI Lab"
copyright: "Copyright © 2025 Quant AI Lab"

directories:
  output: "dist"
  buildResources: "build-resources"

files:
  - "electron_main/**/*"
  - "renderer/build/**/*"
  - "node_modules/**/*"
  - "package.json"

extraResources:
  - from: "../backend/dist/quant-lab-backend"
    to: "backend"
    filter:
      - "**/*"

win:
  target:
    - target: "nsis"
      arch: ["x64"]
  icon: "build-resources/icon.ico"
  artifactName: "Quant-AI-Lab-Setup-${version}.exe"

nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
  installerIcon: "build-resources/icon.ico"
  uninstallerIcon: "build-resources/icon.ico"
  installerHeaderIcon: "build-resources/icon.ico"
  createDesktopShortcut: true
  createStartMenuShortcut: true
  shortcutName: "Quant AI Lab"
  license: "LICENSE"
```

### Build Command
```bash
cd d:\quant-lab\desktop_app
npm run package
# Or directly:
npx electron-builder build --win --x64
```

### Output
```
dist/
├── Quant-AI-Lab-Setup-1.0.0.exe    # NSIS installer
└── win-unpacked/                    # Portable version
    ├── Quant AI Lab.exe
    ├── resources/
    │   ├── app.asar
    │   └── backend/
    │       └── quant-lab-backend.exe
    └── ...
```

---

## Step 4: Electron Main Process — Backend Lifecycle

The Electron main process manages the Python backend as a child process:

```
App Start
    │
    ├─ Spawn quant-lab-backend.exe
    │   └─ FastAPI starts on port 8000
    │
    ├─ Wait for health check (GET /health)
    │
    ├─ Create BrowserWindow
    │   └─ Load React app
    │
    ├─ App Running...
    │
    └─ App Close
        └─ Kill backend process
        └─ Cleanup
```

---

## Runtime Flow

```
User double-clicks "Quant AI Lab.exe"
    │
    ▼
Electron starts → spawns Python backend
    │
    ▼
Backend initializes: DB, agents, connections
    │
    ▼
Frontend loads in Electron window
    │
    ▼
Frontend connects to backend via HTTP + WebSocket
    │
    ▼
User interacts with the application
    │
    ▼
On close: Electron kills backend process, saves state
```

---

## Build Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Frontend build, Electron |
| Python | 3.11+ | Backend runtime |
| PyInstaller | 6.x | Python bundling |
| Electron Builder | 24+ | Electron packaging |
| NSIS | 3.x | Windows installer (auto-downloaded) |

---

## File Sizes (Approximate)

| Component | Size |
|-----------|------|
| Python backend bundle | ~500 MB |
| Electron + React app | ~200 MB |
| ML models (pre-trained) | ~50 MB |
| Total installer | ~300 MB (compressed) |
| Installed size | ~800 MB |

---

## Auto-Update (Optional)

For future releases, Electron's auto-update system can be configured:

```yaml
# electron-builder.yml
publish:
  provider: "github"
  owner: "your-org"
  repo: "quant-ai-lab"
```

Users receive update notifications within the app and can update with one click.

---

## Signing (Production)

For production distribution:
1. Obtain Windows Code Signing certificate
2. Configure in `electron-builder.yml`:
```yaml
win:
  signingHashAlgorithms: ["sha256"]
  certificateFile: "path/to/cert.pfx"
  certificatePassword: "env:CERT_PASSWORD"
```
3. Signed installer avoids Windows SmartScreen warnings
