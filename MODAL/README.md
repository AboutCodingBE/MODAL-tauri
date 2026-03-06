# Tauri + Angular

## Prerequisites
Before starting, install these tools:
1. Node.js (v18 or higher)

Download: https://nodejs.org/
Verify installation:

```bash
bashnode --version
npm --version
```

2. Rust (Required for Tauri)

Windows: Download from https://rustup.rs/
macOS/Linux:

```bash
bashcurl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Verify installation:

```bash
bashrustc --version
cargo --version
```

3. Platform-specific dependencies
   Windows:

Install Microsoft C++ Build Tools:

Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
Install "Desktop development with C++" workload


Install WebView2: https://developer.microsoft.com/en-us/microsoft-edge/webview2/

macOS:

Install Xcode Command Line Tools:

```bash
xcode-select --install
```

Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install libwebkit2gtk-4.0-dev \
build-essential \
curl \
wget \
file \
libssl-dev \
libgtk-3-dev \
libayatana-appindicator3-dev \
librsvg2-dev
```

## Project Setup

### Step 1: Create Tauri + Angular Project

```bash
# Create a new Tauri app
npm create tauri-app@latest

# You'll be prompted with:
# ✔ Project name · my-archive-app
# ✔ Choose which language to use for your frontend · TypeScript / JavaScript
# ✔ Choose your package manager · npm
# ✔ Choose your UI template · Angular
# ✔ Choose your UI flavor · TypeScript

```


OR create Angular project first, then add Tauri:
```bash
# Create Angular 20 project
npm init @angular@latest my-archive-app
cd my-archive-app


# Add Tauri
npm install --save-dev @tauri-apps/cli
npm install @tauri-apps/api
npx tauri init

# Answer prompts:
# ✔ What is your app name? · My Archive App
# ✔ What should the window title be? · My Archive App
# ✔ Where are your web assets located? · dist/my-archive-app/browser
# ✔ What is the url of your dev server? · http://localhost:4200
# ✔ What is your frontend dev command? · npm run start
# ✔ What is your frontend build command? · npm run build

```

### Step 2: Navigate to Project

```bash
cd my-archive-app
```

### Step 3: Install Dependencies

```bash
npm install
```

# Database

I am using Alembic for automatic migrations of schemas. When a new schema is added, I need to run the following after
the docker database is running: 

```shell
.venv/bin/alembic upgrade head
```
This needs to be run in the python folder. 