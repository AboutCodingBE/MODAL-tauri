# CI/CD Pipeline Setup for MODAL

## Overview
Set up GitHub Actions workflows for the MODAL desktop application (Tauri + Angular + Python). The pipeline should handle testing on merge to main and building release artifacts when version tags are pushed.

## Project Structure
- **Frontend**: Angular
- **Desktop Framework**: Tauri (Rust)
- **Backend Scripts**: Python 3.12+
- **Database**: PostgreSQL (external, not needed for CI/CD yet)
- **Dependency Management**: pyproject.toml (not requirements.txt)

## Required Workflows

### 1. Test Pipeline (`test.yml`)
**Trigger**: Push or PR to `main` branch

**Jobs**:
- **Frontend tests** (placeholder for now - just build Angular)
- **Rust tests** (placeholder - just check compilation)
- **Python tests** (placeholder - just install dependencies)

**Platforms**: Run on `ubuntu-latest` only (fastest, cheapest)

**Steps**:
1. Checkout code
2. Setup Node.js (v20)
3. Setup Rust (stable)
4. Setup Python (3.12)
5. Install frontend dependencies: `npm ci`
6. Build Angular app: `npm run build`
7. Install Rust dependencies
8. Check Rust compilation: `cargo check`
9. Install Python dependencies from pyproject.toml
10. Run placeholder tests (echo statements for now)

**Notes**:
- No actual tests yet, but structure should be ready for when tests are added
- Should fail fast if dependencies can't be installed or code doesn't compile

---

### 2. Release Build Pipeline (`release.yml`)
**Trigger**: Push tags matching pattern `v*` (e.g., v1.0.0, v1.2.3-beta)

**Jobs**:
- **Test job** (run tests before building - reuse test workflow)
- **Build job** (build for all platforms, only if tests pass)
- **Release job** (create GitHub release with all artifacts)

**Build Matrix**:
```yaml
platform:
  - os: ubuntu-22.04
    target: x86_64-unknown-linux-gnu
    
  - os: macos-latest
    target: x86_64-apple-darwin
    
  - os: macos-latest
    target: aarch64-apple-darwin
    
  - os: windows-latest
    target: x86_64-pc-windows-msvc
```

**Per-platform Steps**:
1. Checkout code
2. Setup Node.js (v20)
3. Setup Rust (stable) with target platform
4. Setup Python (3.12)
5. Install system dependencies (Ubuntu only):
    - libgtk-3-dev
    - libwebkit2gtk-4.0-dev
    - libappindicator3-dev
    - librsvg2-dev
    - patchelf
6. Install frontend dependencies: `npm ci`
7. Install Python dependencies from pyproject.toml
8. **Bundle Python runtime** (see Python Bundling section below)
9. Build Tauri app using `tauri-apps/tauri-action@v0`
10. Upload artifacts to GitHub Release

**Release Configuration**:
- **Release name**: `MODAL ${{ github.ref_name }}`
- **Tag name**: Use the git tag (e.g., v1.0.0)
- **Draft**: false
- **Prerelease**: false (unless tag contains 'beta', 'alpha', 'rc')
- **Release body**: Include changelog, download instructions, setup requirements

**Artifacts**:
- Windows: `.exe` installer (NSIS) and `.msi`
- macOS Intel: `.dmg`
- macOS ARM: `.dmg`
- Linux: `.AppImage` and `.deb`

---

## Python Runtime Bundling

**Challenge**: Users don't have Python installed, app must be self-contained.

**Solution**: Bundle Python runtime with the Tauri app using one of these approaches:

### Option A: PyInstaller (Recommended)
Create standalone Python executables for each script that will be called by Tauri.

**Build step** (add to release workflow before Tauri build):
```bash
# Install PyInstaller
pip install pyinstaller

# Bundle each Python script
pyinstaller --onefile --name scanner scanner.py
pyinstaller --onefile --name ocr_worker ocr_worker.py
pyinstaller --onefile --name ner_worker ner_worker.py

# Executables will be in dist/
# These get bundled with Tauri app
```

**Tauri configuration** (`tauri.conf.json`):
```json
{
  "bundle": {
    "resources": [
      "dist/scanner*",
      "dist/ocr_worker*",
      "dist/ner_worker*"
    ]
  }
}
```

### Option B: Portable Python
Bundle a portable Python distribution.

**For Windows**:
- Download Python embeddable package
- Include in Tauri resources
- ~50MB size increase

**For macOS/Linux**:
- Use python-build-standalone
- Include in Tauri resources

### Recommended Approach for CI/CD:
Use **PyInstaller** because:
- Smaller final app size
- Faster startup
- Cleaner distribution
- Works identically on all platforms

**Implementation in workflow**:
1. Install PyInstaller in Python setup step
2. Bundle all Python scripts before Tauri build
3. Configure Tauri to include bundled executables
4. Tauri automatically includes them in platform-specific installers

---

## Python Dependencies Installation

Since the project uses `pyproject.toml` instead of `requirements.txt`:

```bash
# Install dependencies
pip install .

# Or for development
pip install -e .

# Or just install dependencies without the package
pip install sqlalchemy alembic psycopg2-binary pydantic pydantic-settings
```

**In CI/CD**:
```yaml
- name: Install Python dependencies
  run: |
    python -m pip install --upgrade pip
    pip install pyinstaller  # For bundling
    pip install .  # Install project dependencies
```

---

## Release Notes Template

```markdown
## MODAL $VERSION

### Downloads
- **Windows**: `MODAL_$VERSION_x64_en-US.msi` or `.exe`
- **macOS (Intel)**: `MODAL_$VERSION_x64.dmg`
- **macOS (Apple Silicon)**: `MODAL_$VERSION_aarch64.dmg`
- **Linux**: `MODAL_$VERSION_amd64.AppImage` or `.deb`

### Requirements
- **Database**: PostgreSQL 14+ running on localhost:5432
  - Run `docker-compose up -d` to start the database
  - See [DATABASE_SETUP.md](DATABASE_SETUP.md) for details

### What's New
See [CHANGELOG.md](CHANGELOG.md) for full release notes.

### Installation
1. Download the installer for your platform
2. Run the installer
3. Start PostgreSQL database (Docker Compose provided)
4. Launch MODAL

### First Time Setup
- The app will connect to PostgreSQL on localhost:5432
- Default database: `archive_db`
- Configure connection in Settings if using different host/port
```

---

## Code Signing & Notarization (Future)

Currently skipped (open source, not needed). When needed later:

**Windows**:
- Obtain code signing certificate
- Add to GitHub secrets: `WINDOWS_CERTIFICATE`, `WINDOWS_CERTIFICATE_PASSWORD`
- Configure in Tauri build

**macOS**:
- Obtain Apple Developer ID
- Add to GitHub secrets: `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_ID`, `APPLE_PASSWORD`
- Configure notarization in Tauri build

---

## File Locations

Create these workflow files:
- `.github/workflows/test.yml` - Test pipeline for main branch
- `.github/workflows/release.yml` - Release build for version tags

---

## Expected Behavior

### On merge to main:
1. Test workflow runs automatically
2. Checks pass/fail visible in PR
3. No artifacts created

### On tag push (e.g., `git tag v1.0.0 && git push origin v1.0.0`):
1. Test workflow runs first
2. If tests pass, build workflow starts
3. Builds for all platforms (Windows, macOS Intel, macOS ARM, Linux)
4. Creates GitHub Release with tag name
5. Uploads all installers as release assets
6. Users can download from: `https://github.com/YOURORG/YOURREPO/releases`

---

## Success Criteria

✅ Tests run on every push to main  
✅ Builds trigger only on version tags  
✅ Multi-platform builds (4 targets)  
✅ Python runtime bundled (no user Python installation needed)  
✅ Artifacts uploaded to GitHub Releases  
✅ Release notes auto-generated  
✅ All installers work without additional setup (except PostgreSQL)

---

## Notes for Implementation

1. **Python script locations**: Assume Python scripts are in project root or specify actual paths
2. **Tauri config**: May need to update `tauri.conf.json` to reference bundled Python executables
3. **Environment variables**: No secrets needed for now (open source, no signing)
4. **Build time**: Expect ~20-30 minutes for full multi-platform build
5. **Artifact size**: ~80-150 MB per platform (with bundled Python)

---

## Testing the Pipeline

### Test the test workflow:
```bash
git checkout -b test-pipeline
# Make a change
git commit -am "test: trigger pipeline"
git push origin test-pipeline
# Open PR to main - tests will run
```

### Test the release workflow:
```bash
git tag v0.1.0
git push origin v0.1.0
# Check GitHub Actions tab for build progress
# Check Releases tab for artifacts
```

---

## Future Enhancements (Not Now)

- Add actual unit tests (Python, TypeScript, Rust)
- Add integration tests
- Add E2E tests with Playwright
- Add code coverage reporting
- Add automatic changelog generation
- Add code signing for Windows/macOS
- Add update mechanism (Tauri updater)
- Add performance benchmarks
- Add security scanning (Dependabot, Snyk)

---

## Implementation Checklist for Claude Code

- [ ] Create `.github/workflows/test.yml`
- [ ] Create `.github/workflows/release.yml`
- [ ] Add PyInstaller bundling steps to release workflow
- [ ] Configure Tauri to include bundled Python executables
- [ ] Set up proper release notes template
- [ ] Test workflows with a trial tag (v0.0.1-test)
- [ ] Document usage in project README