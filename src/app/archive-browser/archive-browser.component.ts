import { Component, signal, OnInit } from '@angular/core';
import { invoke } from '@tauri-apps/api/core';
import { open } from '@tauri-apps/plugin-dialog';

export interface Archive {
  id: number;
  name: string;
  created_at: string;
  analysis_status: string;
  file_count: number;
}

@Component({
  selector: 'app-archive-browser',
  standalone: true,
  templateUrl: './archive-browser.component.html',
  styleUrl: './archive-browser.component.css',
})
export class ArchiveBrowserComponent implements OnInit {
  archives = signal<Archive[]>([]);
  showModal = signal(false);
  archiveName = signal('');
  folderPath = signal('');
  isLoading = signal(false);
  errorMessage = signal('');

  async ngOnInit(): Promise<void> {
    await this.loadArchives();
  }

  async loadArchives(): Promise<void> {
    try {
      const json = await invoke<string>('get_archives');
      this.archives.set(JSON.parse(json));
    } catch (error) {
      console.error('Kon archieven niet laden:', error);
    }
  }

  openModal(): void {
    this.archiveName.set('');
    this.folderPath.set('');
    this.errorMessage.set('');
    this.showModal.set(true);
  }

  closeModal(): void {
    if (this.isLoading()) return;
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

  async ingestArchive(): Promise<void> {
    this.errorMessage.set('');
    this.isLoading.set(true);

    try {
      await invoke('create_archive', {
        name: this.archiveName(),
        path: this.folderPath(),
      });
      this.showModal.set(false);
      await this.loadArchives();
    } catch (error) {
      this.errorMessage.set(error as string);
    } finally {
      this.isLoading.set(false);
    }
  }

  formatDate(isoString: string): string {
    return isoString.split('T')[0];
  }

  statusLabel(status: string): string {
    const map: Record<string, string> = {
      completed: 'ANALYSED',
      in_progress: 'IN BEHANDELING',
      pending: 'INGESTED',
      failed: 'MISLUKT',
    };
    return map[status] ?? status.toUpperCase();
  }
}
