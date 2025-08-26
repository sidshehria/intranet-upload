import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-json-preview',
  templateUrl: './json-preview.component.html',
  styleUrls: ['./json-preview.component.scss']
})
export class JsonPreviewComponent implements OnInit {

  jsonFiles: { filename: string; content: any }[] = [];
  error: string = '';

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.loadJsonFiles();
  }

  loadJsonFiles(): void {
    this.http.get<{ filename: string; content: any }[]>('/api/json-files').subscribe({
      next: (data) => {
        this.jsonFiles = data;
      },
      error: (err) => {
        this.error = 'Failed to load JSON files';
        console.error(err);
      }
    });
  }

  downloadJson(filename: string, content: any): void {
    const jsonStr = JSON.stringify(content, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  }
}
