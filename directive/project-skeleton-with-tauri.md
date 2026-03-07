# Building the skeleton

**IMPORTANT: This is a Tauri v2 desktop application with Angular 20.**

Tech stack:
- Tauri v2.10 (desktop app framework)
- Angular 20 (frontend)
- Standalone components
- Signals for state management
- Language: Dutch

Project structure:
- Angular code is in `src/` directory
- Tauri Rust backend is in `src-tauri/` (already set up - don't modify)

Reference wireframe: https://datable.be/MODAL/wireframe3.html

## Requirements:

- Build an `archive-browser` component. This component will show created archives as a list of 'cards'.
  The archive browser has a create button with text: 'Nieuw Archief'.

- Clicking 'Nieuw Archief' opens a modal window as shown in `create-archive-modal.png` picture.

- **CRITICAL - Folder Selection:**
  When pressing the 'Selecteer Map' button, use Tauri's native dialog API:
```typescript
  import { open } from '@tauri-apps/api/dialog';
  
  async selectFolder() {
    const selected = await open({
      directory: true,
      multiple: false,
      title: 'Selecteer een map'
    });
    
    if (selected && typeof selected === 'string') {
      this.folderPath.set(selected); // Full file system path
    }
  }
```
Do NOT use browser's File System Access API (showDirectoryPicker).

- The selected folder path should be displayed in the input field next to the 'Selecteer Map' button.

- Modal buttons:
    - 'Annuleren' - closes the modal without any action
    - 'Archief Ingesten' - does nothing yet (just console.log for now)

- Setup routing to the archive-browser component at root path ('/')

- Use Angular signals for reactive state management

- All UI text should be in Dutch

## Implementation notes:
- This is a DESKTOP app, so you have access to full file system paths
- Tauri provides the dialog API - it's already available in the project
- Don't create any backend/Rust code - that's already configured
- Focus only on the Angular frontend components