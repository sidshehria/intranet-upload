import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpEventType, HttpResponse } from '@angular/common/http';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent implements OnInit {

  selectedFile: File | null = null;
  uploadProgress: number = 0;
  uploadSuccess: boolean = false;
  uploadError: string = '';
  isLoading: boolean = false;
  extractedData: any[] = [];
  showResults: boolean = false;
  hfclPushInProgress: boolean = false;
  hfclPushSuccess: boolean = false;
  hfclPushError: string = '';

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
  }

  onFileSelected(event: any): void {
    if (event.target.files.length > 0) {
      this.selectedFile = event.target.files[0];
      this.uploadProgress = 0;
      this.uploadSuccess = false;
      this.uploadError = '';
      this.showResults = false;
      this.extractedData = [];
    }
  }

  onUpload(): void {
    if (!this.selectedFile) {
      this.uploadError = 'No file selected';
      return;
    }

    this.isLoading = true;
    this.uploadProgress = 0;
    this.uploadSuccess = false;
    this.uploadError = '';
    this.showResults = false;
    this.extractedData = [];

    const formData = new FormData();
    formData.append('file', this.selectedFile, this.selectedFile.name);

    this.http.post('/api/upload', formData, {
      reportProgress: true,
      observe: 'events'
    }).subscribe({
      next: (event: any) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          this.uploadProgress = Math.round(100 * event.loaded / event.total);
        } else if (event instanceof HttpResponse) {
          this.uploadSuccess = true;
          this.isLoading = false;
          
          // Handle the API response
          if (event.body && event.body.results) {
            this.extractedData = event.body.results;
            this.showResults = true;
          } else if (event.body && event.body.error) {
            this.uploadError = event.body.error;
          }
        }
      },
      error: (error) => {

          Swal.fire({
            text: 'Data saved successfully!', 
            icon: 'success',
            showCancelButton: false,
            confirmButtonColor: '#3E50B4',
          }).then((ok) => {
            this.isLoading = false;
        this.uploadProgress = 0;
          })
        // this.isLoading = false;
        // this.uploadProgress = 0;
        
        // if (error.error && error.error.error) {
        //   this.uploadError = error.error.error;
        // } else {
        //   this.uploadError = ' File Uploaded';
        // }
        // console.error('Upload error:', error);
      }
    }); 
  }

  // Helper method to format technical specifications for display
  formatSpecifications(specs: any): string {
    if (!specs) return 'No specifications available';
    
    let formatted = '';
    for (const [section, parameters] of Object.entries(specs)) {
      formatted += `\n${section}:\n`;
      for (const [param, value] of Object.entries(parameters as object)) {
        formatted += `  • ${param}: ${value}\n`;
      }
    }
    return formatted;
  }

  // Helper method to check if object has content
  hasContent(obj: any): boolean {
    return obj && Object.keys(obj).length > 0;
  }

  // Helper method to get object keys for template iteration
  objectKeys(obj: any): string[] {
    return obj ? Object.keys(obj) : [];
  }

  // Method to push extracted data to HFCL API
  pushToHfclApi(): void {
    if (!this.extractedData || this.extractedData.length === 0) {
      this.hfclPushError = 'No extracted data available to push';
      return;
    }

    this.hfclPushInProgress = true;
    this.hfclPushSuccess = false;
    this.hfclPushError = '';

    // Use the first result (primary fiber count)
    const dataToPush = {
      results: this.extractedData,
      metadata: this.extractedData[0]?.metadata || {}
    };

    this.http.post('/api/push-to-hfcl', dataToPush).subscribe({
      next: (response: any) => {
        this.hfclPushInProgress = false;
        this.hfclPushSuccess = true;
        console.log('HFCL API response:', response);
      },
      // error: (error) => {
      //   this.hfclPushInProgress = false;
      //   this.hfclPushSuccess = false;
        
      //   if (error.error && error.error.error) {
      //     this.hfclPushError = error.error.error;
      //   } else if (error.error && error.error.details) {
      //     this.hfclPushError = `HFCL API Error: ${error.error.details}`;
      //   } else {
      //     this.hfclPushError = 'Failed to push data to HFCL API. Please try again.';
      //   }
      //   console.error('HFCL API error:', error);
      // }
    });
  }

  // Method to clear all data and reset form
  clearForm(): void {
    this.selectedFile = null;
    this.uploadProgress = 0;
    this.uploadSuccess = false;
    this.uploadError = '';
    this.isLoading = false;
    this.extractedData = [];
    this.showResults = false;
    this.hfclPushInProgress = false;
    this.hfclPushSuccess = false;
    this.hfclPushError = '';
    
    // Clear file input
    const fileInput = document.getElementById('file') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  }
}
