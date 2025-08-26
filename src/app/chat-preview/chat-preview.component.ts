import { Component, OnInit, HostListener } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SearchService } from '../services/search.service';

@Component({
  selector: 'app-chat-preview',
  templateUrl: './chat-preview.component.html',
  styleUrls: ['./chat-preview.component.scss']
})
export class ChatPreviewComponent implements OnInit {

  searchParams: any = {
    fiberCount: '',
    typeOfCable: '',
    fiberType: '',
    nescConditions: '',
    incoterms: '',
    thirdParty: '',
    cprApprovals: '',
    diameter: '',
    tensileStrength: '',
    tubeColourCoding: '',
    currency: ''
  };

  // New properties for PDF link and accuracy
  pdfLink: string = '';
  accuracyPercentage: number = 0;
  isCalculating: boolean = false;
  accuracyDetails: any[] = [];

  cableData: any[] = []; // To hold the cable data
  selectedCables: boolean[] = []; // To track selected checkboxes
  allChecked: boolean = false; // To manage select all checkbox state

  // API response data
  apiResponse: any = null;
  isLoading: boolean = false;
  errorMessage: string = '';

  // Parameter data for autocomplete
  fiberCountOptions: string[] = [];
  allFiberCounts: string[] = [];
  isLoadingFiberCount: boolean = false;
  
  typeOfCableOptions: string[] = [];
  allTypeOfCables: string[] = [];
  isLoadingTypeOfCable: boolean = false;
  
  fiberTypeOptions: string[] = [];
  allFiberTypes: string[] = [];
  isLoadingFiberType: boolean = false;
  
  nescConditionsOptions: string[] = [];
  allNESCConditions: string[] = [];
  isLoadingNESCConditions: boolean = false;
  
  incotermsOptions: string[] = [];
  allIncoterms: string[] = [];
  isLoadingIncoterms: boolean = false;
  
  thirdPartyOptions: string[] = [];
  allThirdParty: string[] = [];
  isLoadingThirdParty: boolean = false;
  
  cprApprovalsOptions: string[] = [];
  allCPRApprovals: string[] = [];
  isLoadingCPRApprovals: boolean = false;
  
  diameterOptions: string[] = [];
  allDiameters: string[] = [];
  isLoadingDiameter: boolean = false;
  
  tensileStrengthOptions: string[] = [];
  allTensileStrengths: string[] = [];
  isLoadingTensileStrength: boolean = false;
  
  tubeColourCodingOptions: string[] = [];
  allTubeColourCodings: string[] = [];
  isLoadingTubeColourCoding: boolean = false;

  dropdownOpen: string | null = null;
  filteredOptions: { [key: string]: string[] } = {};
  
  // Collapsible search section state
  isSearchSectionCollapsed: boolean = false;
  expandedCableIndex: number | null = null;

  // Toggle search section collapse/expand
  toggleSearchSection(): void {
    this.isSearchSectionCollapsed = !this.isSearchSectionCollapsed;
  }

  // Toggle individual cable details
  toggleCableDetails(index: number): void {
    this.expandedCableIndex = this.expandedCableIndex === index ? null : index;
  }

  allOptions: { [key: string]: string[] } = {
    fiberCount: ['2', '4', '6', '8', '12', '24', '48', '96', '144', '288'],
    typeOfCable: ['UT', 'MT', 'UTA', 'MTA', 'D', 'A1'],
    fiberType: ['SM', 'MM', 'OM1', 'OM2', 'OM3', 'OM4'],
    nescConditions: ['Light', 'Medium', 'Heavy'],
    incoterms: ['EXW', 'FCA', 'FAS', 'FOB', 'CFR', 'CIF', 'CPT', 'CIP', 'DAP', 'DPU', 'DDP'],
    thirdParty: ['Yes', 'No'],
    cprApprovals: ['Yes', 'No'],
    diameter: ['1.5mm', '2.5mm', '3.0mm', '4.0mm', '5.0mm', '6.0mm', '8.0mm', '10.0mm'],
    tensileStrength: ['1000N', '2000N', '3000N', '4000N', '5000N', '6000N', '8000N', '10000N'],
    tubeColourCoding: ['Standard', 'Custom', 'Blue', 'Orange', 'Green', 'Brown', 'Slate', 'White', 'Red', 'Black', 'Yellow', 'Violet', 'Rose', 'Aqua'],
    currency: ['INR', 'USD', 'GBP', 'JPY', 'EUR', 'CNY', 'AUD', 'CAD', 'CHF', 'SEK', 'NOK', 'DKK']
  };

  private apiUrl = 'https://www.hfcl.com/testapiforsap/api/datasheet/fetchMasterDataAll';
  private parameterApiUrl = 'https://www.hfcl.com/testapiforsap/api/datasheet/fetchParameterData';

  constructor(private http: HttpClient, private searchService: SearchService) { }

  ngOnInit(): void {
    // Initialize filtered options with all options
    for (const key in this.allOptions) {
      this.filteredOptions[key] = [...this.allOptions[key]];
    }
    
    // Fetch all master data on component initialization
    this.fetchAllMasterData();
    
    // Fetch fiber count options for autocomplete
    this.fetchFiberCountOptions();
    
    // Fetch type of cable options for autocomplete
    this.fetchTypeOfCableOptions();
    
    // Fetch all other parameter options for autocomplete
    this.fetchFiberTypeOptions();
    this.fetchNESCConditionsOptions();
    this.fetchIncotermsOptions();
    this.fetchThirdPartyOptions();
    this.fetchCPRApprovalsOptions();
    this.fetchDiameterOptions();
    this.fetchTensileStrengthOptions();
    this.fetchTubeColourCodingOptions();
  }

  private fetchAllMasterData(): void {
    this.isLoading = true;
    this.errorMessage = '';
    
    // Call API without any parameters to get all data
    this.http.get(this.apiUrl).subscribe({
      next: (response: any) => {
        console.log('Initial API Response:', response);
        this.apiResponse = response;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Initial API Error:', error);
        this.errorMessage = 'Failed to load initial data. Please try again.';
        this.isLoading = false;
      }
    });
  }

  private fetchFiberCountOptions(): void {
    this.isLoadingFiberCount = true;
    
    // Call parameter API for fiber count
    this.http.get(`${this.parameterApiUrl}?parameterType=fiberCount`).subscribe({
      next: (response: any) => {
        console.log('Fiber Count Options:', response);
        if (response && response.parameterNames) {
          this.allFiberCounts = response.parameterNames.map((item: any) => item.parameterName);
          this.fiberCountOptions = [...this.allFiberCounts];
        }
        this.isLoadingFiberCount = false;
      },
      error: (error) => {
        console.error('Fiber Count API Error:', error);
        this.allFiberCounts = ['2F', '4F', '6F', '8F', '12F', '24F', '48F', '96F', '144F', '288F'];
        this.fiberCountOptions = [...this.allFiberCounts];
        this.isLoadingFiberCount = false;
      }
    });
  }

  private fetchTypeOfCableOptions(): void {
    this.isLoadingTypeOfCable = true;
    
    // Call parameter API for type of cable using correct parameter type
    this.http.get(`${this.parameterApiUrl}?parameterType=TypeofCable`).subscribe({
      next: (response: any) => {
        console.log('Type of Cable Options:', response);
        if (response && response.parameterNames) {
          this.allTypeOfCables = response.parameterNames
            .filter((item: any) => item.parameterName !== null)
            .map((item: any) => item.parameterName);
          this.typeOfCableOptions = [...this.allTypeOfCables];
        }
        this.isLoadingTypeOfCable = false;
      },
      error: (error) => {
        console.error('Type of Cable API Error:', error);
        // Fallback to actual cable types from the API response
        this.allTypeOfCables = [
          'Armoured LSZH loose-tube cable',
          'Armoured Polyethylene loose-tube cable',
          'Indoor LSZH loose-tube cable',
          'Micro LSZH loose-tube cable',
          'Micro Polyethylene loose-tube cable',
          'Unarmoured HDPE loose-tube cable'
        ];
        this.typeOfCableOptions = [...this.allTypeOfCables];
        this.isLoadingTypeOfCable = false;
      }
    });
  }

  onFiberCountInput(event: any): void {
    const value = event.target.value.toLowerCase();
    if (value) {
      this.fiberCountOptions = this.allFiberCounts.filter(option => 
        option.toLowerCase().includes(value)
      );
    } else {
      this.fiberCountOptions = [...this.allFiberCounts];
    }
  }

  // Generic method for handling dropdown selections
  selectOption(field: string, option: string): void {
    this.searchParams[field] = option;
    this.closeDropdown();
  }

  // Method to handle fiber count selection
  selectFiberCount(option: string): void {
    this.searchParams.fiberCount = option;
    this.fiberCountOptions = []; // Clear options after selection
  }

  // Generic method for handling input with dropdown
  onParameterInput(field: string, event: any): void {
    const value = event.target.value.toLowerCase();
    if (value) {
      this.filteredOptions[field] = this.allOptions[field].filter(option => 
        option.toLowerCase().includes(value)
      );
    } else {
      this.filteredOptions[field] = [...this.allOptions[field]];
    }
  }

  // Generic method for selecting from dropdown
  selectFromDropdown(field: string, option: string): void {
    this.searchParams[field] = option;
    this.filteredOptions[field] = []; // Clear dropdown
  }

  // Method to handle all parameter changes
  onParameterChange(field: string, value: string): void {
    this.searchParams[field] = value;
    console.log(`${field} changed:`, value);
  }

  // Method to toggle all checkboxes
  toggleAllCheckboxes(event: any): void {
    this.allChecked = event.target.checked;
    this.selectedCables = this.cableData.map(() => this.allChecked);
  }

  // Method to handle individual checkbox changes
  onCheckboxChange(index: number): void {
    this.selectedCables[index] = !this.selectedCables[index];
    this.allChecked = this.selectedCables.every(checked => checked);
  }

  // Method to fetch cable data (to be called after search)
  private fetchCableData(): void {
    // Use API response data instead of hardcoded data
    if (this.apiResponse && this.apiResponse.data && this.apiResponse.data.length > 0) {
      this.cableData = this.apiResponse.data;
      this.selectedCables = new Array(this.cableData.length).fill(false);
    } else {
      this.cableData = [];
      this.selectedCables = [];
    }
  }

  // Method to forward cable data to team
  forwardToTeam(cable: any): void {
    console.log('Forwarding cable to team:', cable);
    
    // Create a formatted message for team sharing
    const teamMessage = {
      cableId: cable.cableID,
      cableType: cable.typeofCable,
      fiberCount: cable.fiberCount,
      fiberType: cable.fiberType,
      diameter: cable.diameter,
      tensile: cable.tensile,
      crush: cable.crush,
      nescCondition: cable.nescCondition,
      description: cable.cableDescription,
      timestamp: new Date().toISOString()
    };
    
    // Here you would typically send this to your backend
    // For now, we'll show an alert and log to console
    alert(`Cable ${cable.cableID} - ${cable.typeofCable} has been forwarded to the team!`);
    
    // Example of how to send to backend:
    // this.http.post('https://your-api.com/forward-to-team', teamMessage).subscribe({
    //   next: (response) => console.log('Successfully forwarded', response),
    //   error: (error) => console.error('Error forwarding', error)
    // });
  }

  // Method to forward selected cables to team
  forwardSelectedCables(): void {
    const selectedCables = this.cableData.filter((_, index) => this.selectedCables[index]);
    if (selectedCables.length === 0) {
      alert('Please select at least one cable to forward');
      return;
    }
    
    selectedCables.forEach(cable => this.forwardToTeam(cable));
  }

  // Clear all dropdowns
  closeDropdown(): void {
    Object.keys(this.filteredOptions).forEach(key => {
      this.filteredOptions[key] = [];
    });
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.dropdown-parent-fix')) {
      this.closeDropdown();
    }
  }

  onSearch(): void {
      this.isSearchFormVisible = !this.isSearchFormVisible;
    console.log('Search parameters:', this.searchParams);
    
    const searchPayload = this.buildSearchPayload();
    
    // Perform search without changing form visibility
    this.performSearch(searchPayload);
    // Keep the form visible and maintain its size
    // The form will not collapse or become small when search is clicked
  }

  private buildSearchPayload(): any {
    return {
      cableID: 0,
      cableDescription: this.searchParams.cableDescription || "",
      fiberCount: this.searchParams.fiberCount || "",
      typeofCable: this.searchParams.typeOfCable || "",
      span: this.searchParams.span || "",
      tube: this.searchParams.tube || "",
      tubeColorCoding: this.searchParams.tubeColourCoding || "",
      fiberType: this.searchParams.fiberType || "",
      diameter: this.searchParams.diameter || "",
      tensile: this.searchParams.tensileStrength || "",
      nescCondition: this.searchParams.nescConditions || "",
      crush: this.searchParams.crush || "",
      blowingLength: this.searchParams.blowingLength || "",
      datasheetURL: this.searchParams.datasheetURL || "",
      isActive: "Y"
    };
  }

  private hasValidSearchParameters(payload: any): boolean {
    // Check if at least one parameter (other than cableID and isActive) has a value
    const { cableID, isActive, ...otherParams } = payload;
    return Object.values(otherParams).some(value => value && value !== "");
  }

  private performSearch(payload: any): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.apiResponse = null;
    this.cableData = []; // Clear previous data

    this.searchService.searchDatasheet(payload).subscribe({
      next: (response: any) => {
        console.log('POST API Response:', response);
        this.apiResponse = response;
        
        // Handle the API response structure with 'res' array
        if (response && response.res && Array.isArray(response.res)) {
          this.cableData = response.res;
          this.selectedCables = new Array(this.cableData.length).fill(false);
          
          // Calculate accuracy if response has data
          if (response.res.length > 0) {
            this.calculateAccuracy(response.res);
          }
        } else {
          this.cableData = [];
          this.selectedCables = [];
        }
        
        this.isLoading = false;
      },
      error: (error) => {
        console.error('POST API Error:', error);
        this.errorMessage = 'Failed to fetch search results. Please try again.';
        this.cableData = [];
        this.selectedCables = [];
        this.isLoading = false;
      }
    });
  }

  // Method to calculate accuracy based on search results
  private calculateAccuracy(data: any[]): void {
    this.isCalculating = true;
    
    // Calculate accuracy for each cable based on search parameters
    this.cableData = data.map(cable => {
      const accuracy = this.calculateCableAccuracy(cable);
      return {
        ...cable,
        accuracy: accuracy.overall,
        accuracyDetails: accuracy.details
      };
    });
    
    this.isCalculating = false;
  }

  // Calculate accuracy for individual cable
  private calculateCableAccuracy(cable: any): { overall: number, details: any } {
    const searchFields = [
      'fiberCount', 'typeOfCable', 'fiberType', 'nescConditions', 
      'diameter', 'tensileStrength', 'tubeColourCoding'
    ];
    
    let totalFields = 0;
    let matchedFields = 0;
    const details: any = {};

    searchFields.forEach(field => {
      const searchValue = this.searchParams[field];
      if (searchValue && searchValue.trim() !== '') {
        totalFields++;
        
        let cableValue = '';
        switch(field) {
          case 'fiberCount':
            cableValue = cable.fiberCount || '';
            break;
          case 'typeOfCable':
            cableValue = cable.typeofCable || '';
            break;
          case 'fiberType':
            cableValue = cable.fiberType || '';
            break;
          case 'nescConditions':
            cableValue = cable.nescCondition || '';
            break;
          case 'diameter':
            cableValue = cable.diameter || '';
            break;
          case 'tensileStrength':
            cableValue = cable.tensile || '';
            break;
          case 'tubeColourCoding':
            cableValue = cable.tubeColorCoding || '';
            break;
        }
        
        const isMatch = cableValue.toString().toLowerCase().includes(searchValue.toLowerCase());
        if (isMatch) {
          matchedFields++;
        }
        
        details[field] = {
          searchValue: searchValue,
          cableValue: cableValue,
          isMatch: isMatch,
          accuracy: isMatch ? 100 : 0
        };
      }
    });

    const overallAccuracy = totalFields > 0 ? Math.round((matchedFields / totalFields) * 100) : 0;
    
    return {
      overall: overallAccuracy,
      details: details
    };
  }

  // Check if a value matches search criteria and should be highlighted
  shouldHighlight(value: string, searchParam: string): boolean {
    return Boolean(searchParam && searchParam.trim() !== '' && 
           value && value.toString().toLowerCase().includes(searchParam.toLowerCase()));
  }

  // Get highlighting class for table cells
  getHighlightClass(value: string, searchParam: string): boolean {
    return this.shouldHighlight(value, searchParam);
  }

  // Get accuracy for specific field
  getFieldAccuracy(cable: any, field: string): number {
    if (cable.accuracyDetails && cable.accuracyDetails[field]) {
      return cable.accuracyDetails[field].accuracy;
    }
    return 0;
  }

  // Get color based on accuracy percentage
  getAccuracyColor(accuracy: number): string {
    if (accuracy >= 80) {
      return '#4CAF50'; // Green for high accuracy
    } else if (accuracy >= 60) {
      return '#FF9800'; // Orange for medium accuracy
    } else if (accuracy >= 40) {
      return '#FFC107'; // Yellow for low-medium accuracy
    } else {
      return '#F44336'; // Red for low accuracy
    }
  }

  // Method to clear all search parameters
  clearSearch(): void {
    this.searchParams = {
      fiberCount: '',
      typeOfCable: '',
      fiberType: '',
      nescConditions: '',
      incoterms: '',
      thirdParty: '',
      cprApprovals: '',
      diameter: '',
      tensileStrength: '',
      tubeColourCoding: '',
      currency: ''
    };
    this.apiResponse = null;
    this.errorMessage = '';
    this.accuracyPercentage = 0;
    this.accuracyDetails = [];
  }

  // Method to export results
  exportResults(): void {
    if (this.apiResponse && this.apiResponse.data) {
      const dataStr = JSON.stringify(this.apiResponse.data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = window.URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'search-results.json';
      link.click();
      window.URL.revokeObjectURL(url);
    }
  }

  onCurrencyChange(value: string): void {
    this.searchParams.currency = value;
    console.log('Currency changed:', value);
  }

  onTypeOfCableInput(event: any): void {
    const value = event.target.value.toLowerCase();
    if (value) {
      this.typeOfCableOptions = this.allTypeOfCables.filter(option => 
        option.toLowerCase().includes(value)
      );
    } else {
      this.typeOfCableOptions = [...this.allTypeOfCables];
    }
  }

  // Method to handle type of cable selection
  selectTypeOfCable(option: string): void {
    this.searchParams.typeOfCable = option;
    this.typeOfCableOptions = []; // Clear options after selection
  }

  // Fiber Type methods
  private fetchFiberTypeOptions(): void {
    this.isLoadingFiberType = true;
    
    this.http.get(`${this.parameterApiUrl}?parameterType=FiberType`).subscribe({
      next: (response: any) => {
        console.log('Fiber Type Options:', response);
        if (response && response.parameterNames) {
          this.allFiberTypes = response.parameterNames
            .filter((item: any) => item.parameterName !== null)
            .map((item: any) => item.parameterName);
          this.fiberTypeOptions = [...this.allFiberTypes];
        }
        this.isLoadingFiberType = false;
      },
      error: (error) => {
        console.error('Fiber Type API Error:', error);
        this.allFiberTypes = ['G.652D', 'G.657A1'];
        this.fiberTypeOptions = [...this.allFiberTypes];
        this.isLoadingFiberType = false;
      }
    });
  }

  onFiberTypeInput(event: any): void {
    const value = event.target.value.toLowerCase();
    if (value) {
      this.fiberTypeOptions = this.allFiberTypes.filter(option => 
        option.toLowerCase().includes(value)
      );
    } else {
      this.fiberTypeOptions = [...this.allFiberTypes];
    }
  }

  selectFiberType(option: string): void {
    this.searchParams.fiberType = option;
    this.fiberTypeOptions = [];
  }

  // NESC Conditions methods
  private fetchNESCConditionsOptions(): void {
    this.isLoadingNESCConditions = true;
    
    this.http.get(`${this.parameterApiUrl}?parameterType=NESCCondition`).subscribe({
      next: (response: any) => {
        console.log('NESC Conditions Options:', response);
        if (response && response.parameterNames) {
          this.allNESCConditions = response.parameterNames
            .filter((item: any) => item.parameterName !== null)
            .map((item: any) => item.parameterName);
          this.nescConditionsOptions = [...this.allNESCConditions];
        }
        this.isLoadingNESCConditions = false;
      },
      error: (error) => {
        console.error('NESC Conditions API Error:', error);
        this.allNESCConditions = [
          'Installation -15 °C to + 50 °C ,   Operation -40 °C to + 70 °C ,                   Storage -40 °C to + 70 °C',
          'Installation -20 °C to + 70 °C   Operation -20 °C to + 70 °C                    Storage -20 °C to + 70 °C',
          'Installation -20 °C to + 70 °C ,   Operation -30 °C to + 70 °C ,                   Storage -30 °C to + 70 °C',
          'Installation -5 °C to + 50 °C ,   Operation -20 °C to + 60 °C ,                   Storage -20 °C to + 70 °C',
          'Installation -5 °C to + 50 °C ,   Operation -30 °C to + 60 °C ,                   Storage -20 °C to + 70 °C',
          'Installation -5 °C to + 50 °C ,   Operation -40 °C to + 70 °C ,                   Storage -20 °C to + 70 °C'
        ];
        this.nescConditionsOptions = [...this.allNESCConditions];
        this.isLoadingNESCConditions = false;
      }
    });
  }

  onNESCConditionsInput(event: any): void {
    const value = event.target.value.toLowerCase();
    if (value) {
      this.nescConditionsOptions = this.allNESCConditions.filter(option => 
        option.toLowerCase().includes(value)
      );
    } else {
      this.nescConditionsOptions = [...this.allNESCConditions];
    }
  }

  selectNESCConditions(option: string): void {
    this.searchParams.nescConditions = option;
    this.nescConditionsOptions = [];
  }

  // Incoterms methods
  private fetchIncotermsOptions(): void {
    this.isLoadingIncoterms = true;
    
    this.http.get(`${this.parameterApiUrl}?parameterType=Incoterms`).subscribe({
      next: (response: any) => {
        console.log('Incoterms Options:', response);
        if (response && response.parameterNames) {
          this.allIncoterms = response.parameterNames
            .filter((item: any) => item.parameterName !== null)
            .map((item: any) => item.parameterName);
          this.incotermsOptions = [...this.allIncoterms];
        }
        this.isLoadingIncoterms = false;
      },
      error: (error) => {
        console.error('Incoterms API Error:', error);
        this.allIncoterms = ['EXW', 'FCA', 'FAS', 'FOB', 'CFR', 'CIF', 'CPT', 'CIP', 'DAP', 'DPU', 'DDP'];
        this.incotermsOptions = [...this.allIncoterms];
        this.isLoadingIncoterms = false;
      }
    });
  }

  onIncotermsInput(event: any): void {
    const value = event.target.value.toLowerCase();
    if (value) {
      this.incotermsOptions = this.allIncoterms.filter(option => 
        option.toLowerCase().includes(value)
      );
    } else {
      this.incotermsOptions = [...this.allIncoterms];
    }
  }

  selectIncoterms(option: string): void {
    this.searchParams.incoterms = option;
    this.incotermsOptions = [];
  }

  // Third Party methods
  private fetchThirdPartyOptions(): void {
    this.isLoadingThirdParty = true;
    
    this.http.get(`${this.parameterApiUrl}?parameterType=ThirdParty`).subscribe({
      next: (response: any) => {
        console.log('Third Party Options:', response);
        if (response && response.parameterNames) {
          this.allThirdParty = response.parameterNames
            .filter((item: any) => item.parameterName !== null)
            .map((item: any) => item.parameterName);
          this.thirdPartyOptions = [...this.allThirdParty];
        }
        this.isLoadingThirdParty = false;
      },
      error: (error) => {
        console.error('Third Party API Error:', error);
        this.allThirdParty = ['Yes', 'No'];
        this.thirdPartyOptions = [...this.allThirdParty];
        this.isLoadingThirdParty = false;
      }
    });
  }

  onThirdPartyInput(event: any): void {
    const value = event.target.value.toLowerCase();
    if (value) {
      this.thirdPartyOptions = this.allThirdParty.filter(option => 
        option.toLowerCase().includes(value)
      );
    } else {
      this.thirdPartyOptions = [...this.allThirdParty];
    }
  }

  selectThirdParty(option: string): void {
    this.searchParams.thirdParty = option;
    this.thirdPartyOptions = [];
  }

  // CPR Approvals methods
  private fetchCPRApprovalsOptions(): void {
    this.isLoadingCPRApprovals = true;
    
    this.http.get(`${this.parameterApiUrl}?parameterType=CPRApprovals`).subscribe({
      next: (response: any) => {
        console.log('CPR Approvals Options:', response);
        if (response && response.parameterNames) {
          this.allCPRApprovals = response.parameterNames
            .filter((item: any) => item.parameterName !== null)
            .map((item: any) => item.parameterName);
          this.cprApprovalsOptions = [...this.allCPRApprovals];
        }
        this.isLoadingCPRApprovals = false;
      },
      error: (error) => {
        console.error('CPR Approvals API Error:', error);
        this.allCPRApprovals = ['Yes', 'No'];
        this.cprApprovalsOptions = [...this.allCPRApprovals];
        this.isLoadingCPRApprovals = false;
      }
    });
  }

  onCPRApprovalsInput(event: any): void {
    const value = event.target.value.toLowerCase();
    if (value) {
      this.cprApprovalsOptions = this.allCPRApprovals.filter(option => 
        option.toLowerCase().includes(value)
      );
    } else {
      this.cprApprovalsOptions = [...this.allCPRApprovals];
    }
  }

  selectCPRApprovals(option: string): void {
    this.searchParams.cprApprovals = option;
    this.cprApprovalsOptions = [];
  }

  // Diameter methods
  private fetchDiameterOptions(): void {
    this.isLoadingDiameter = true;
    
    this.http.get(`${this.parameterApiUrl}?parameterType=Diameter`).subscribe({
      next: (response: any) => {
        console.log('Diameter Options:', response);
        if (response && response.parameterNames) {
          this.allDiameters = response.parameterNames
            .filter((item: any) => item.parameterName !== null)
            .map((item: any) => item.parameterName);
          this.diameterOptions = [...this.allDiameters];
        }
        this.isLoadingDiameter = false;
      },
      error: (error) => {
        console.error('Diameter API Error:', error);
        this.allDiameters = [
          '7.9 ± 0.3 mm',
          '8.0 ± 0.3 mm',
          '8.5 ± 0.5 mm',
          '10.5 ± 0.5 mm',
          '12.0 ± 0.5 mm',
          '13.2 ± 0.5 mm'
        ];
        this.diameterOptions = [...this.allDiameters];
        this.isLoadingDiameter = false;
      }
    });
  }

  onDiameterInput(event: any): void {
    const value = event.target.value.toLowerCase();
    if (value) {
      this.diameterOptions = this.allDiameters.filter(option => 
        option.toLowerCase().includes(value)
      );
    } else {
      this.diameterOptions = [...this.allDiameters];
    }
  }

  selectDiameter(option: string): void {
    this.searchParams.diameter = option;
    this.diameterOptions = [];
  } 

  // Tensile Strength methods
  private fetchTensileStrengthOptions(): void {
    this.isLoadingTensileStrength = true;
    
    this.http.get(`${this.parameterApiUrl}?parameterType=Tensile`).subscribe({
      next: (response: any) => {
        console.log('Tensile Strength Options:', response);
        if (response && response.parameterNames) {
          this.allTensileStrengths = response.parameterNames
            .filter((item: any) => item.parameterName !== null)
            .map((item: any) => item.parameterName);
          this.tensileStrengthOptions = [...this.allTensileStrengths];
        }
        this.isLoadingTensileStrength = false;
      },
      error: (error) => {
        console.error('Tensile Strength API Error:', error);
        this.allTensileStrengths = [
          '600 N',
          '1000N',
          '1500 N',
          '1500N',
          '2200 N',
          '3000N',
          '3500N',
          'Installation: 1800 N ,        Operation: 1000 N'
        ];
        this.tensileStrengthOptions = [...this.allTensileStrengths];
        this.isLoadingTensileStrength = false;
      }
    });
  }

  onTensileStrengthInput(event: any): void {
    const value = event.target.value.toLowerCase();
    if (value) {
      this.tensileStrengthOptions = this.allTensileStrengths.filter(option => 
        option.toLowerCase().includes(value)
      );
    } else {
      this.tensileStrengthOptions = [...this.allTensileStrengths];
    }
  }

  selectTensileStrength(option: string): void {
    this.searchParams.tensileStrength = option;
    this.tensileStrengthOptions = [];
  }

  // Tube Colour Coding methods
  private fetchTubeColourCodingOptions(): void {
    this.isLoadingTubeColourCoding = true;
    
    this.http.get(`${this.parameterApiUrl}?parameterType=TubeColorCoding`).subscribe({
      next: (response: any) => {
        console.log('Tube Colour Coding Options:', response);
        if (response && response.parameterNames) {
          this.allTubeColourCodings = response.parameterNames
            .filter((item: any) => item.parameterName !== null)
            .map((item: any) => item.parameterName);
          this.tubeColourCodingOptions = [...this.allTubeColourCodings];
        }
        this.isLoadingTubeColourCoding = false;
      },
      error: (error) => {
        console.error('Tube Colour Coding API Error:', error);
        this.allTubeColourCodings = [
          'Bl, Or, Gr, Br, Sl, Wh, Rd, Bk',
          'Bl, Or, Gr, Br, Sl, Wh, Rd, Bk, Yl, Vi, Pk, Aq',
          'Rd, Gr, Bl, Yl, Wh, Sl, Br, Vl, Aq, Bk, Or, Pk',
          'Nt',
          'Layer I - Rd, Gr, Bl, Yl, Wh, Sl, Br, Vi, Aq, Bk, Or, Pk  ;        Layer II - Bk, Or, Pk, Rd#, Gr#, Bl#, Yl#, Wh#, Sl#, Br#, Vi#, Aq#                                     Layer II RK - Bk#, Or#, Pk#'
        ];
        this.tubeColourCodingOptions = [...this.allTubeColourCodings];
        this.isLoadingTubeColourCoding = false;
      }
    });
  }

  onTubeColourCodingInput(event: any): void {
    const value = event.target.value.toLowerCase();
    if (value) {
      this.tubeColourCodingOptions = this.allTubeColourCodings.filter(option => 
        option.toLowerCase().includes(value)
      );
    } else {
      this.tubeColourCodingOptions = [...this.allTubeColourCodings];
    }
  }

  selectTubeColourCoding(option: string): void {
    this.searchParams.tubeColourCoding = option;
    this.tubeColourCodingOptions = [];
  } 

  // Toggle search section collapse/expand
  // toggleSearchSection(): void {
  //   this.isSearchSectionCollapsed = !this.isSearchSectionCollapsed;
  // }

  // New properties for sliding search form
  isSearchFormVisible: boolean = false;

  clearallfiters(){
    
    // Clear search results and reset form to initial state
    this.clearSearch();
    this.cableData = [];
    this.selectedCables = [];
    this.apiResponse = null;
    this.errorMessage = '';
    this.accuracyPercentage = 0;
    this.accuracyDetails = [];
    
    // Reset all dropdown options
    this.closeDropdown();
    
    // Clear all autocomplete options
    this.fiberCountOptions = [];
    this.typeOfCableOptions = [];
    this.fiberTypeOptions = [];
    this.nescConditionsOptions = [];
    this.diameterOptions = [];
    this.tensileStrengthOptions = [];
  }
  // Method to toggle the search form visibility and reset form
  toggleSearchForm(): void {
    this.isSearchFormVisible = !this.isSearchFormVisible;
    
    // Clear search results and reset form to initial state
    // this.clearSearch();
    // this.cableData = [];
    // this.selectedCables = [];
    // this.apiResponse = null;
    // this.errorMessage = '';
    // this.accuracyPercentage = 0;
    // this.accuracyDetails = [];
    
    // Reset all dropdown options
    // this.closeDropdown();
    
    // Clear all autocomplete options
    // this.fiberCountOptions = [];
    // this.typeOfCableOptions = [];
    // this.fiberTypeOptions = [];
    // this.nescConditionsOptions = [];
    // this.diameterOptions = [];
    // this.tensileStrengthOptions = [];
  }
}
