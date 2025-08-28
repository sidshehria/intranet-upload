import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private baseUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) { }

  /**
   * Upload and process a PDF file
   */
  uploadAndProcessFile(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    
    return this.http.post(`${this.baseUrl}/upload`, formData);
  }

  /**
   * Process all PDF files in the data directory
   */
  processAllFiles(): Observable<any> {
    return this.http.post(`${this.baseUrl}/process-all`, {});
  }

  /**
   * Health check for the backend
   */
  healthCheck(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health`);
  }

  /**
   * List all processed files
   */
  listProcessedFiles(): Observable<any> {
    return this.http.get(`${this.baseUrl}/files`);
  }
}
