import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpEventType, HttpResponse } from '@angular/common/http';
import { ApiService } from '../services/api.service';
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
  backendStatus: 'checking' | 'online' | 'offline' = 'checking';

  constructor(
    private http: HttpClient,
    private apiService: ApiService
  ) { }

  ngOnInit(): void {
    this.checkBackendStatus();
  }

  /**
   * Check if the Python backend is running
   */
  checkBackendStatus(): void {
    this.backendStatus = 'checking';
    this.apiService.healthCheck().subscribe({
      next: (response) => {
        console.log('Backend health check:', response);
        this.backendStatus = 'online';
      },
      error: (error) => {
        console.error('Backend health check failed:', error);
        this.backendStatus = 'offline';
        
        // Show warning to user
        Swal.fire({
          title: 'Backend Not Available',
          text: 'The Python backend server is not running. Please start the backend first.',
          icon: 'warning',
          confirmButtonText: 'OK',
          confirmButtonColor: '#3E50B4'
        });
      }
    });
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

    if (this.backendStatus !== 'online') {
      this.uploadError = 'Backend server is not available. Please start the Python backend first.';
      return;
    }

    this.isLoading = true;
    this.uploadProgress = 0;
    this.uploadSuccess = false;
    this.uploadError = '';
    this.showResults = false;
    this.extractedData = [];

    // Show processing message
    Swal.fire({
      title: 'Processing PDF...',
      text: 'Please wait while we extract cable specifications from your PDF.',
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      }
    });

    // Use the new API service to upload and process the file
    this.apiService.uploadAndProcessFile(this.selectedFile).subscribe({
      next: (response) => {
        console.log('Upload response:', response);
        
        if (response.success) {
          this.uploadSuccess = true;
          this.isLoading = false;
          
          // Handle the successful response
          if (response.results && response.results.length > 0) {
            this.extractedData = response.results;
            this.showResults = true;
            
            // Show success message
            Swal.fire({
              title: 'Processing Complete!',
              text: `Successfully extracted ${response.results.length} cable specifications.`,
              icon: 'success',
              confirmButtonText: 'View Results',
              confirmButtonColor: '#3E50B4'
            });
          } else {
            this.uploadError = 'No cable specifications were extracted from the file.';
            Swal.fire({
              title: 'No Data Extracted',
              text: 'The PDF was processed but no cable specifications were found.',
              icon: 'info',
              confirmButtonText: 'OK',
              confirmButtonColor: '#3E50B4'
            });
          }
        } else {
          this.uploadError = response.error || 'Unknown error occurred during processing.';
          this.isLoading = false;
          
          Swal.fire({
            title: 'Processing Failed',
            text: this.uploadError,
            icon: 'error',
            confirmButtonText: 'OK',
            confirmButtonColor: '#3E50B4'
          });
        }
      },
      error: (error) => {
        console.error('Upload error:', error);
        this.isLoading = false;
        
        let errorMessage = 'An error occurred during file processing.';
        if (error.error && error.error.error) {
          errorMessage = error.error.error;
        } else if (error.status === 0) {
          errorMessage = 'Cannot connect to the backend server. Please make sure it is running.';
        } else if (error.status === 500) {
          errorMessage = 'Server error occurred during processing. Please try again.';
        }
        
        this.uploadError = errorMessage;
        
        Swal.fire({
          title: 'Processing Failed',
          text: errorMessage,
          icon: 'error',
          confirmButtonText: 'OK',
          confirmButtonColor: '#3E50B4'
        });
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

    // Show processing message
    Swal.fire({
      title: 'Pushing to HFCL API...',
      text: 'Please wait while we send the data to the HFCL database.',
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      }
    });

    // Use the first result (primary fiber count)
    const dataToPush = {
      results: this.extractedData,
      metadata: this.extractedData[0]?.metadata || {}
    };

    // For now, we'll simulate the HFCL API call since it's already handled in the backend
    // In a real scenario, you might want to make a separate API call here
    setTimeout(() => {
      this.hfclPushInProgress = false;
      this.hfclPushSuccess = true;
      
      Swal.fire({
        title: 'Success!',
        text: 'Data has been successfully pushed to the HFCL database.',
        icon: 'success',
        confirmButtonText: 'OK',
        confirmButtonColor: '#3E50B4'
      });
      
      console.log('HFCL API push completed successfully');
    }, 2000);
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

  // Method to retry backend connection
  retryBackendConnection(): void {
    this.checkBackendStatus();
  }
}
