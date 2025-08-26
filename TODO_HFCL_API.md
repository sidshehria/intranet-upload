# HFCL API Integration Implementation Plan

## Phase 1: Backend Implementation ✅ COMPLETED
- [x] Add HTTP client dependency to backend
- [x] Create mapping function to convert extracted data to HFCL API format
- [x] Add new endpoint `/api/push-to-hfcl` in main.py
- [x] Implement error handling for external API calls

## Phase 2: Frontend Implementation ✅ COMPLETED
- [x] Add "Push to HFCL API" button to file upload component
- [x] Implement API call method in component
- [x] Add UI feedback for API operations
- [x] Update HTML template with new button

## Phase 3: Testing & Validation
- [ ] Test data mapping with sample extracted data
- [ ] Test API integration with mock responses
- [ ] Verify error handling works correctly
- [ ] Test complete workflow from upload to API push

## Phase 4: Documentation
- [ ] Update README with new API integration details
- [ ] Add comments for new functionality

## Data Mapping Strategy:
- cableID: Auto-generated or from filename
- cableDescription: Filename + extracted product info
- fiberCount: From detected fiber counts
- typeofCable: From cable construction details  
- span: Default or from specifications
- tube: From number of loose tubes
- tubeColorCoding: From color coding extraction
- fiberType: From fiber characteristics
- diameter: Cable diameter from physical specs
- tensile: Max tensile strength
- nescCondition: Default or from standards
- crush: Max crush resistance
- blowingLength: Default or from packaging
- datasheetURL: File URL or placeholder
- isActive: Default "Y"
