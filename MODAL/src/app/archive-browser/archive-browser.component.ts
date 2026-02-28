import { Component, signal } from '@angular/core';
import { open } from '@tauri-apps/plugin-dialog';

@Component({
  selector: 'app-archive-browser',
  standalone: true,
  templateUrl: './archive-browser.component.html',
  styleUrl: './archive-browser.component.css',
})
export class ArchiveBrowserComponent {
  showModal = signal(false);
  archiveName = signal('');
  folderPath = signal('');

  openModal(): void {
    this.archiveName.set('');
    this.folderPath.set('');
    this.showModal.set(true);
  }

  closeModal(): void {
    this.showModal.set(false);
  }

  async selectFolder(): Promise<void> {
    const selected = await open({
      directory: true,
      multiple: false,
      title: 'Selecteer een map',
    });

    if (selected && typeof selected === 'string') {
      this.folderPath.set(selected);
    }
  }

  ingestArchive(): void {
    console.log('Archief Ingesten:', {
      naam: this.archiveName(),
      pad: this.folderPath(),
    });
  }
}