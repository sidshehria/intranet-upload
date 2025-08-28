#!/usr/bin/env python3
"""
Combined HFCL Cable Data Scraper and API Poster
This file combines all functionality from the separate modules into one comprehensive script.
"""

import os
import json
import pdfplumber
import time
import threading
import requests
import urllib3
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

# Suppress SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================================================
# CONFIGURATION SECTION
# ============================================================================

# API Configuration
API_URL = "https://www.hfcl.com/testapiforsap/api/datasheet/configureDatasheet"
API_KEY = None  # Set your API key here if required

# File Paths
JSON_DIRECTORY = "output"  # Directory containing generated JSON files
DATA_DIRECTORY = "data"     # Directory containing PDF datasheets

# API Request Settings
DELAY_BETWEEN_REQUESTS = 1.0  # Delay in seconds between API calls
REQUEST_TIMEOUT = 30          # Timeout for API requests in seconds
VERIFY_SSL = False            # Set to False for self-signed certificates (like test APIs)

# Headers (customize as needed)
DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'HFCL-Cable-Data-Poster/1.0'
}

# Logging
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"

# ============================================================================
# SCRAPER FUNCTIONS
# ============================================================================

def _get_cable_description(text: str) -> str:
    """Extracts the main cable description from the text."""
    # Look for more detailed descriptions in the PDF
    detailed_patterns = [
        r"Indoor LSZH loose-tube cable",
        r"Outdoor loose-tube cable",
        r"Armoured loose-tube cable",
        r"Micro loose-tube cable",
        r"Unarmoured loose-tube cable"
    ]
    
    for pattern in detailed_patterns:
        if pattern.lower() in text.lower():
            return pattern
    
    # Fallback to simple patterns
    if "MTUA" in text: return "Indoor LSZH loose-tube cable"
    if "UTA" in text: return "Armoured loose-tube cable"
    if "MICRO" in text: return "Micro loose-tube cable"
    if "MT UA" in text: return "Unarmoured loose-tube cable"
    return "Optical Fiber Cable"

def _extract_parameter_value(text: str, parameter_name: str, fiber_count: str = None) -> str:
    """
    Extracts a specific parameter value using targeted regex patterns.
    """
    # Clean up the text for better pattern matching
    text = re.sub(r'\s+', ' ', text)
    
    if parameter_name.lower() == 'tensile strength':
        # Look for tensile strength values.
        patterns = [
            r"(\d+\s*N)",
            r"Installation\s*:\s*(\d+\s*N)",
            r"Short Term\s*:\s*(\d+\s*N)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    
    elif parameter_name.lower() == 'crush resistance':
        # Look for crush resistance values
        patterns = [
            r"(\d+\s*N/\d+\s*x?\s*\d*\s*cm)",
            r"(\d+\s*N/\d+\s*x?\s*\d*\s*mm)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    
    elif parameter_name.lower() == 'cable diameter':
        # Look for cable diameter values
        patterns = [
            r"(\d+\.\d+\s*±\s*\d+\.\d+\s*mm)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    
    return "N/A"

def _get_tube_type(text: str) -> str:
    """Extracts the specific tube type."""
    if "Unitube" in text or "UTA" in text: return "Unitube"
    if "Multitube" in text or "MTUA" in text or "MT UA" in text: return "Multitube"
    if "Micro" in text: return "Micro"
    return "Standard"

def _get_tube_color_coding(text: str) -> str:
    """Returns N/A for tube color coding as requested."""
    return "N/A"

def _get_detailed_fiber_type(text: str, fiber_count: str = None) -> str:
    """Extracts detailed fiber type information."""
    # Special case for 144F and 288F cables
    if fiber_count in ["144", "288"]:
        return "G.657A1"
    
    # Look for specific fiber type standards
    if "G.65" in text: return "G.652D"
    if "OM" in text: return "OM1"
    return "G.652D"

def _get_nesc_condition(text: str) -> str:
    """Extracts NESC condition information with temperature ranges."""
    # Look for temperature range patterns
    temp_match = re.search(r"(\-?\d+\s*°C\s*to\s*\+\d+\s*°C)", text)
    if temp_match:
        return temp_match.group(1).strip()
    
    # Look for individual temperature mentions
    temps = re.findall(r"(\-?\d+\s*°C)", text)
    if temps:
        return f"Temperature range: {', '.join(temps)}"
    
    return "N/A"

def _get_cable_type(text: str) -> str:
    """Determines if the cable is Unitube (UT) or Multitube (MT)."""
    if "Unitube" in text or "UTA" in text: return "UT"
    if "Multitube" in text or "MTUA" in text or "MT UA" in text: return "MT"
    return "N/A"

def _get_fiber_type(text: str) -> str:
    """Determines if the fiber is Single-Mode (SM) or Multi-Mode (MM)."""
    if "G.65" in text: return "SM"
    if "OM" in text: return "MM"
    return "N/A"

def _parse_single_datasheet(filename: str, text: str) -> List[Dict[str, Any]]:
    """Parses text from a single datasheet, returning a list of cable data dicts."""
    results = []
    cable_description = _get_cable_description(text)
    
    # Extract fiber counts from text
    text_fcs = re.findall(r'(\d+)F', text)
    
    # Combine, remove duplicates, and sort
    fiber_counts = sorted(list(set(text_fcs)), key=int)

    if not fiber_counts: 
        return []

    for fc in fiber_counts:
        # Extract parameters
        tensile = _extract_parameter_value(text, 'tensile strength')
        crush = _extract_parameter_value(text, 'crush resistance')
        diameter = _extract_parameter_value(text, 'cable diameter')

        # Create description with "F" suffix
        detailed_desc = f"{fc}F {cable_description}"

        data = {
            "cableID": 0, 
            "cableDescription": detailed_desc,
            "fiberCount": f"{fc}F",  # Add "F" suffix to fiber count
            "typeofCable": _get_cable_type(text),
            "span": "N/A", 
            "tube": _get_tube_type(text),
            "tubeColorCoding": "N/A",  # Set to N/A as requested
            "fiberType": _get_detailed_fiber_type(text, fc), 
            "diameter": diameter, 
            "tensile": tensile,
            "nescCondition": _get_nesc_condition(text), 
            "crush": crush, 
            "blowingLength": "N/A",
            "datasheetURL": filename, 
            "isActive": "Y"
        }
        results.append(data)
    
    return results

def parse_datasheets(files: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Main function to parse multiple datasheet files.
    Args:
        files: A dictionary of {filename: file_text_content}.
    Returns:
        A list of dictionaries, with each dictionary representing a cable variant.
    """
    all_cables = []
    for filename, content in files.items():
        try:
            parsed_cables = _parse_single_datasheet(filename, content)
            for cable in parsed_cables:
                cable['cableID'] = 0  # Set all cable IDs to 0
                all_cables.append(cable)
        except Exception as e:
            print(f"--> Could not process file {filename}. Error: {e}")
    return all_cables

# ============================================================================
# API POSTER CLASS
# ============================================================================

class APIPoster:
    """Handles posting cable data to the SQL database through the API."""
    
    def __init__(self, api_url: str, api_key: str = None, verify_ssl: bool = False):
        self.api_url = api_url
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
        # Set headers
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
        else:
            self.session.headers.update({
                'Content-Type': 'application/json'
            })
    
    def post_cable_data(self, cable_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Posts a single cable data record to the API.
        
        Args:
            cable_data: Dictionary containing cable information
            
        Returns:
            Dictionary with API response information
        """
        try:
            # Ensure all required fields are present
            required_fields = [
                "cableID", "cableDescription", "fiberCount", "typeofCable", 
                "span", "tube", "tubeColorCoding", "fiberType", "diameter", 
                "tensile", "nescCondition", "crush", "blowingLength", 
                "datasheetURL", "isActive"
            ]
            
            # Validate that all required fields exist
            missing_fields = [field for field in required_fields if field not in cable_data]
            if missing_fields:
                return {
                    "success": False,
                    "error": f"Missing required fields: {missing_fields}",
                    "cable_description": cable_data.get("cableDescription", "Unknown")
                }
            
            # Make the API call
            response = self.session.post(
                self.api_url,
                json=cable_data,
                timeout=30,
                verify=self.verify_ssl
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": response.json() if response.content else "Success",
                    "cable_description": cable_data.get("cableDescription", "Unknown")
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"API Error: {response.status_code} - {response.text}",
                    "cable_description": cable_data.get("cableDescription", "Unknown")
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "cable_description": cable_data.get("cableDescription", "Unknown")
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "cable_description": cable_data.get("cableDescription", "Unknown")
            }
    
    def post_multiple_cables(self, cable_data_list: List[Dict[str, Any]], delay: float = 1.0) -> List[Dict[str, Any]]:
        """
        Posts multiple cable data records to the API with optional delay between requests.
        
        Args:
            cable_data_list: List of cable data dictionaries
            delay: Delay in seconds between API calls (default: 1.0)
            
        Returns:
            List of API response dictionaries
        """
        results = []
        total_cables = len(cable_data_list)
        
        print(f" Starting to post {total_cables} cable records to API...")
        print(f" API Endpoint: {self.api_url}")
        print(f" Delay between requests: {delay} seconds")
        print("=" * 60)
        
        for i, cable_data in enumerate(cable_data_list, 1):
            print(f"📤 Posting cable {i}/{total_cables}: {cable_data.get('cableDescription', 'Unknown')}")
            
            result = self.post_cable_data(cable_data)
            results.append(result)
            
            # Print result
            if result["success"]:
                print(f"  ✅ Success: {result['response']}")
            else:
                print(f"  ❌ Failed: {result['error']}")
            
            # Add delay between requests (except for the last one)
            if i < total_cables and delay > 0:
                time.sleep(delay)
        
        # Summary
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        print("=" * 60)
        print(f"   API Posting Summary:")
        print(f"  ✅ Successful: {successful}")
        print(f"  ❌ Failed: {failed}")
        print(f"  📈 Success Rate: {(successful/total_cables)*100:.1f}%")
        
        return results
    
    def post_from_json_files(self, json_directory: str, delay: float = 1.0) -> List[Dict[str, Any]]:
        """
        Posts cable data from JSON files in a directory.
        
        Args:
            json_directory: Path to directory containing JSON files
            delay: Delay in seconds between API calls
            
        Returns:
            List of API response dictionaries
        """
        json_dir = Path(json_directory)
        if not json_dir.exists():
            return [{
                "success": False,
                "error": f"Directory not found: {json_directory}",
                "cable_description": "N/A"
            }]
        
        # Find all JSON files
        json_files = list(json_dir.glob("*.json"))
        if not json_files:
            return [{
                "success": False,
                "error": f"No JSON files found in directory: {json_directory}",
                "cable_description": "N/A"
            }]
        
        print(f"📁 Found {len(json_files)} JSON files in {json_directory}")
        
        all_cables = []
        
        # Load all JSON files
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    cable_data = json.load(f)
                    all_cables.append(cable_data)
                    print(f"  📄 Loaded: {json_file.name}")
            except Exception as e:
                print(f"  ❌ Failed to load {json_file.name}: {e}")
        
        if not all_cables:
            return [{
                "success": False,
                "error": "No valid cable data found in JSON files",
                "cable_description": "N/A"
            }]
        
        # Post all cables to API
        return self.post_multiple_cables(all_cables, delay)

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_json_output(cable_data: dict) -> bool:
    """Validates that the extracted cable data has reasonable values."""
    required_fields = ['fiberCount', 'typeofCable', 'fiberType', 'diameter', 'tensile', 'crush']
    
    for field in required_fields:
        if field not in cable_data:
            print(f"  Warning: Missing field '{field}'")
            return False
    
    # Check for reasonable values
    if cable_data['fiberCount'] and not cable_data['fiberCount'].replace('F', '').isdigit():
        print(f"  Warning: Invalid fiber count: {cable_data['fiberCount']}")
        return False
    
    if cable_data['typeofCable'] not in ['UT', 'MT', 'N/A']:
        print(f"  Warning: Invalid cable type: {cable_data['typeofCable']}")
    
    if cable_data['fiberType'] not in ['SM', 'MM', 'N/A']:
        print(f"  Warning: Invalid fiber type: {cable_data['fiberType']}")
    
    return True

# ============================================================================
# PDF PROCESSOR CLASS
# ============================================================================

class PDFProcessor:
    """Handles PDF processing and file monitoring."""
    
    def __init__(self, data_dir, output_dir):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.processed_files = set()
        self.lock = threading.Lock()
        
        # Initialize API poster
        self.api_poster = APIPoster(API_URL, API_KEY, VERIFY_SSL)
    
    def _process_single_pdf(self, pdf_path):
        """Process a single PDF file and generate JSON outputs."""
        pdf_name = os.path.basename(pdf_path)
        
        try:
            # Extract text from PDF
            with pdfplumber.open(pdf_path) as pdf:
                full_text = "".join(page.extract_text() + "\n--- PAGE BREAK ---\n" for page in pdf.pages)
                print(f"  ✅ Successfully extracted {len(full_text)} characters")
            
            # Parse the datasheet
            file_contents = {pdf_name: full_text}
            all_cables_data = parse_datasheets(file_contents)
            
            if not all_cables_data:
                print(f"  ⚠️  No cable data extracted from {pdf_name}")
                return
            
            print(f" Extracted {len(all_cables_data)} cable variants")
            
            # Validate and save each cable variant
            valid_count = 0
            saved_count = 0
            
            for cable in all_cables_data:
                print(f"    Cable {cable['cableID']}: {cable['cableDescription']}")
                print(f"      Fiber Count: {cable['fiberCount']}")
                print(f"      Type: {cable['typeofCable']}, Fiber: {cable['fiberType']}")
                print(f"      Diameter: {cable['diameter']}")
                print(f"      Tensile: {cable['tensile']}")
                print(f"      Crush: {cable['crush']}")
                
                if validate_json_output(cable):
                    valid_count += 1
                
                # Save individual JSON file
                original_filename = Path(cable['datasheetURL']).stem
                fiber_count = cable['fiberCount']
                
                output_filename = f"{original_filename}_{fiber_count}.json"
                output_path = self.output_dir / output_filename
                
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(cable, f, indent=2)
                    print(f"      💾 Saved: {output_filename}")
                    saved_count += 1
                except Exception as e:
                    print(f"      ❌ Failed to save {output_filename}: {e}")
                
                print()
            
            print(f"    Processing complete for {pdf_name}")
            print(f"    Valid cables: {valid_count}/{len(all_cables_data)}")
            print(f"    Saved files: {saved_count}/{len(all_cables_data)}")
            
            # Post to API if enabled
            if API_URL:
                print(f"  📡 Posting {len(all_cables_data)} cable records to API...")
                try:
                    api_results = self.api_poster.post_multiple_cables(all_cables_data, DELAY_BETWEEN_REQUESTS)
                    successful_api = sum(1 for r in api_results if r["success"])
                    print(f"  API Results: {successful_api}/{len(api_results)} successful")
                except Exception as e:
                    print(f"  ❌ API posting failed: {e}")
            
        except Exception as e:
            print(f"  ❌ Failed to process {pdf_name}: {e}")
            raise
    
    def process_existing_files(self):
        """Process all existing PDF files in the data directory."""
        pdf_files = list(self.data_dir.glob("*.pdf"))
        
        if not pdf_files:
            print("No existing PDF files found in data directory.")
            return
        
        print(f"📁 Found {len(pdf_files)} existing PDF files")
        print("Processing existing files...")
        
        for pdf_path in pdf_files:
            pdf_name = pdf_path.name
            self.processed_files.add(pdf_name)
            print(f"\n📄 Processing existing file: {pdf_name}")
            self._process_single_pdf(pdf_path)
        
        print("\n✅ All existing files processed!")
    
    def check_for_new_files(self):
        """Check for new PDF files and process them."""
        current_files = set()
        for file in os.listdir(self.data_dir):
            if file.endswith('.pdf'):
                current_files.add(file)
        
        new_files = current_files - self.processed_files
        
        for pdf_name in new_files:
            if pdf_name not in self.processed_files:
                pdf_path = self.data_dir / pdf_name
                print(f"\n🆕 New PDF detected: {pdf_name}")
                print("Processing...")
                
                try:
                    # Wait a bit for file to be fully written
                    time.sleep(1)
                    
                    # Process the new PDF file
                    self._process_single_pdf(pdf_path)
                    self.processed_files.add(pdf_name)
                    
                except Exception as e:
                    print(f"❌ Error processing {pdf_name}: {e}")
        
        return len(new_files) > 0

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def post_existing_json_to_api():
    """
    Posts all existing JSON files in the output directory to the API.
    This function can be called independently to post already processed data.
    """
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "scraper/output"
    
    if not output_dir.exists():
        print(f"❌ Output directory not found: {output_dir}")
        return
    
    print("🚀 Posting existing JSON files to API...")
    poster = APIPoster(API_URL, API_KEY, VERIFY_SSL)
    results = poster.post_from_json_files(str(output_dir), DELAY_BETWEEN_REQUESTS)
    
    # Summary
    successful = sum(1 for r in results if r.get("success", False))
    total = len(results)
    
    if total > 0:
        print(f"\n🎯 Final Summary:")
        print(f"  Total processed: {total}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {total - successful}")
        
        if successful == total:
            print("🎉 All existing cable data successfully posted to the database!")
        else:
            print("⚠️  Some cable data failed to post. Check the errors above.")

def run_all_functionalities():
    """
    Runs all functionalities in one click:
    1. Process all PDF files in data directory
    2. Generate JSON files
    3. Post all data to API
    4. Return comprehensive results
    
    This function is perfect for Angular frontend integration.
    """
    print("🚀 Starting Complete HFCL Cable Data Processing Pipeline")
    print("=" * 70)
    
    # Get project paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "scraper/data"
    output_dir = project_root / "scraper/output"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    if not data_dir.is_dir():
        error_msg = f"❌ Error: Input directory not found at '{data_dir}'"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "results": []
        }
    
    print(f"📁 Input directory: {data_dir}")
    print(f"💾 Output directory: {output_dir}")
    print("=" * 70)
    
    # Step 1: Process all PDF files
    print("\n📋 STEP 1: Processing PDF Files")
    print("-" * 40)
    
    processor = PDFProcessor(data_dir, output_dir)
    processor.process_existing_files()
    
    # Count processed files
    pdf_files = list(data_dir.glob("*.pdf"))
    print(f"\n✅ PDF Processing Complete: {len(pdf_files)} files processed")
    
    # Step 2: Post to API
    print("\n📋 STEP 2: Posting Data to API")
    print("-" * 40)
    
    api_results = None
    if API_URL:
        try:
            api_results = post_existing_json_to_api()
            print(f"\n✅ API Posting Complete")
        except Exception as e:
            print(f"❌ API posting failed: {e}")
            api_results = {
                "total_processed": 0,
                "successful": 0,
                "failed": 0,
                "results": [],
                "error": str(e)
            }
    else:
        print("⚠️  API URL not configured, skipping API posting")
        api_results = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "results": [],
            "message": "API URL not configured"
        }
    
    # Step 3: Generate final summary
    print("\n📋 STEP 3: Final Summary")
    print("-" * 40)
    
    # Count JSON files generated
    json_files = list(output_dir.glob("*.json"))
    
    final_summary = {
        "success": True,
        "pdf_files_processed": len(pdf_files),
        "json_files_generated": len(json_files),
        "api_results": api_results,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "message": "All functionalities completed successfully"
    }
    
    print(f"📊 Final Summary:")
    print(f"  📄 PDF files processed: {final_summary['pdf_files_processed']}")
    print(f"  💾 JSON files generated: {final_summary['json_files_generated']}")
    print(f"  📡 API records posted: {api_results['total_processed']}")
    print(f"  ✅ API successful: {api_results['successful']}")
    print(f"  ❌ API failed: {api_results['failed']}")
    print(f"  🕐 Completed at: {final_summary['timestamp']}")
    
    print("\n🎉 Complete Pipeline Finished Successfully!")
    print("=" * 70)
    
    return final_summary

def run_single_pdf_processing(pdf_filename):
    """
    Process a single PDF file and post to API immediately.
    Perfect for handling individual file uploads from Angular frontend.
    
    Args:
        pdf_filename: Name of the PDF file to process
        
    Returns:
        Dictionary with processing results
    """
    print(f"🚀 Processing single PDF: {pdf_filename}")
    print("=" * 50)
    
    # Get project paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "scraper/data"
    output_dir = project_root / "scraper/output"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    pdf_path = data_dir / pdf_filename
    
    if not pdf_path.exists():
        error_msg = f"❌ PDF file not found: {pdf_filename}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "pdf_processed": False,
            "api_posted": False
        }
    
    try:
        # Process the PDF
        processor = PDFProcessor(data_dir, output_dir)
        processor._process_single_pdf(pdf_path)
        
        # Post to API if enabled
        api_results = None
        if API_URL:
            try:
                # Get the generated JSON files for this PDF
                pdf_stem = Path(pdf_filename).stem
                json_files = list(output_dir.glob(f"{pdf_stem}_*.json"))
                
                if json_files:
                    print(f"\n📡 Posting {len(json_files)} cable records to API...")
                    poster = APIPoster(API_URL, API_KEY, VERIFY_SSL)
                    
                    # Load and post the JSON data
                    all_cables = []
                    for json_file in json_files:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            cable_data = json.load(f)
                            all_cables.append(cable_data)
                    
                    api_results = poster.post_multiple_cables(all_cables, DELAY_BETWEEN_REQUESTS)
                    successful_api = sum(1 for r in api_results if r["success"])
                    
                    print(f"✅ API posting complete: {successful_api}/{len(api_results)} successful")
                    api_posted = True
                else:
                    print("⚠️  No JSON files generated for API posting")
                    api_posted = False
                    api_results = []
                    
            except Exception as e:
                print(f"❌ API posting failed: {e}")
                api_posted = False
                api_results = [{"success": False, "error": str(e)}]
        else:
            print("⚠️  API URL not configured, skipping API posting")
            api_posted = False
            api_results = []
        
        # Return results
        result = {
            "success": True,
            "pdf_processed": True,
            "api_posted": api_posted,
            "pdf_filename": pdf_filename,
            "json_files_generated": len(list(output_dir.glob(f"{pdf_stem}_*.json"))),
            "api_results": api_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"\n✅ Single PDF processing complete!")
        print(f"  📄 PDF: {pdf_filename}")
        print(f"  💾 JSON files: {result['json_files_generated']}")
        print(f"  📡 API posted: {api_posted}")
        
        return result
        
    except Exception as e:
        error_msg = f"❌ Failed to process {pdf_filename}: {e}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "pdf_processed": False,
            "api_posted": False,
            "pdf_filename": pdf_filename
        }

def process_uploaded_pdf(pdf_filename):
    """
    Frontend-friendly function for processing uploaded PDF files.
    This function is specifically designed for Angular frontend integration.
    
    Workflow:
    1. User selects PDF file (handled by frontend)
    2. User clicks Upload button
    3. This function processes the selected PDF and posts to API
    
    Args:
        pdf_filename: Name of the PDF file that was selected/uploaded
        
    Returns:
        Dictionary with comprehensive processing results for frontend display
    """
    print(f"📤 Processing uploaded PDF: {pdf_filename}")
    print("=" * 60)
    
    # Get project paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "scraper/data"
    output_dir = project_root / "scraper/output"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    pdf_path = data_dir / pdf_filename
    
    if not pdf_path.exists():
        error_msg = f"❌ PDF file not found: {pdf_filename}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "pdf_processed": False,
            "api_posted": False,
            "pdf_filename": pdf_filename,
            "cables_extracted": 0,
            "json_files_generated": 0,
            "api_success_count": 0,
            "api_failure_count": 0,
            "processing_time": 0,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    start_time = time.time()
    
    try:
        # Step 1: Process the PDF and extract cable data
        print("📋 STEP 1: Processing PDF and extracting cable data...")
        processor = PDFProcessor(data_dir, output_dir)
        processor._process_single_pdf(pdf_path)
        
        # Count generated JSON files for this PDF
        pdf_stem = Path(pdf_filename).stem
        json_files = list(output_dir.glob(f"{pdf_stem}_*.json"))
        cables_extracted = len(json_files)
        
        print(f"✅ PDF Processing Complete: {cables_extracted} cable variants extracted")
        
        # Step 2: Post to API if enabled
        api_results = None
        api_success_count = 0
        api_failure_count = 0
        
        if API_URL and cables_extracted > 0:
            print("\n📋 STEP 2: Posting cable data to API...")
            try:
                # Load and post the JSON data
                all_cables = []
                for json_file in json_files:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        cable_data = json.load(f)
                        all_cables.append(cable_data)
                
                print(f"📡 Posting {len(all_cables)} cable records to API...")
                poster = APIPoster(API_URL, API_KEY, VERIFY_SSL)
                api_results = poster.post_multiple_cables(all_cables, DELAY_BETWEEN_REQUESTS)
                
                # Count API results
                api_success_count = sum(1 for r in api_results if r.get("success", False))
                api_failure_count = len(api_results) - api_success_count
                
                print(f"✅ API Posting Complete: {api_success_count}/{len(api_results)} successful")
                
            except Exception as e:
                print(f"❌ API posting failed: {e}")
                api_results = [{"success": False, "error": str(e)}]
                api_failure_count = 1
        else:
            if not API_URL:
                print("⚠️  API URL not configured, skipping API posting")
            else:
                print("⚠️  No cable data extracted, skipping API posting")
            api_results = []
        
        # Calculate processing time
        processing_time = round(time.time() - start_time, 2)
        
        # Generate comprehensive result for frontend
        result = {
            "success": True,
            "pdf_processed": True,
            "api_posted": len(api_results) > 0,
            "pdf_filename": pdf_filename,
            "cables_extracted": cables_extracted,
            "json_files_generated": cables_extracted,
            "api_success_count": api_success_count,
            "api_failure_count": api_failure_count,
            "api_total_count": len(api_results),
            "processing_time_seconds": processing_time,
            "api_results": api_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"Successfully processed {pdf_filename} in {processing_time}s"
        }
        
        # Print summary for console
        print("\n" + "=" * 60)
        print("📊 UPLOAD PROCESSING SUMMARY")
        print("=" * 60)
        print(f"📄 PDF File: {pdf_filename}")
        print(f"🔍 Cables Extracted: {cables_extracted}")
        print(f"💾 JSON Files Generated: {cables_extracted}")
        print(f"📡 API Records Posted: {len(api_results)}")
        print(f"✅ API Successful: {api_success_count}")
        print(f"❌ API Failed: {api_failure_count}")
        print(f"⏱️  Processing Time: {processing_time} seconds")
        print(f"🕐 Completed at: {result['timestamp']}")
        print("=" * 60)
        
        if api_success_count == len(api_results) and len(api_results) > 0:
            print("🎉 All cable data successfully posted to the database!")
        elif len(api_results) > 0:
            print("⚠️  Some cable data failed to post. Check the errors above.")
        
        return result
        
    except Exception as e:
        processing_time = round(time.time() - start_time, 2)
        error_msg = f"❌ Failed to process {pdf_filename}: {e}"
        print(error_msg)
        
        return {
            "success": False,
            "error": error_msg,
            "pdf_processed": False,
            "api_posted": False,
            "pdf_filename": pdf_filename,
            "cables_extracted": 0,
            "json_files_generated": 0,
            "api_success_count": 0,
            "api_failure_count": 0,
            "processing_time_seconds": processing_time,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def main():
    """
    Automated PDF processing with file monitoring.
    Continuously monitors for new PDF files and processes them automatically.
    """
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "scraper/data"
    output_dir = project_root / "scraper/output"

    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)

    if not data_dir.is_dir():
        print(f"❌ Error: Input directory not found at '{data_dir}'")
        return

    print("🚀 Starting Automated PDF Scraping System")
    print(f"📁 Monitoring directory: {data_dir}")
    print(f"💾 Output directory: {output_dir}")
    print("=" * 60)
    
    # Initialize processor
    processor = PDFProcessor(data_dir, output_dir)
    
    # Process existing files first
    processor.process_existing_files()
    
    print("\n👀 Starting file monitoring...")
    print("📋 System is now monitoring for new PDF files")
    print("💡 Drop new PDF files into the data directory to process them automatically")
    print("🛑 Press Ctrl+C to stop the system")
    print("=" * 60)
    
    try:
        # Continuous monitoring loop
        while True:
            # Check for new files every 2 seconds
            time.sleep(2)
            processor.check_for_new_files()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down automated system...")
        print("✅ System stopped successfully")

def api_poster_main():
    """
    Main function to demonstrate API posting functionality.
    """
    print("HFCL Cable Data API Poster")
    print("=" * 50)
    
    # Initialize API poster
    poster = APIPoster(API_URL, API_KEY, verify_ssl=False)  # Disable SSL verification for test APIs
    
    # Post data from JSON files
    results = poster.post_from_json_files(JSON_DIRECTORY, DELAY_BETWEEN_REQUESTS)
    
    # Final summary
    successful = sum(1 for r in results if r.get("success", False))
    total = len(results)
    
    if total > 0:
        print(f"\n Final Summary:")
        print(f"  Total processed: {total}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {total - successful}")
        
        if successful == total:
            print("🎉 All cable data successfully posted to the database!")
        else:
            print("⚠️  Some cable data failed to post. Check the errors above.")
    else:
        print("❌ No data was processed.")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--post-api":
            # Post existing JSON files to API
            post_existing_json_to_api()
        elif sys.argv[1] == "--api-only":
            # Run only the API poster
            api_poster_main()
        elif sys.argv[1] == "--run-all":
            # Run all functionalities in one click (perfect for Angular frontend)
            run_all_functionalities()
        elif sys.argv[1] == "--single-pdf":
            # Process a single PDF file
            if len(sys.argv) > 2:
                pdf_filename = sys.argv[2]
                run_single_pdf_processing(pdf_filename)
            else:
                print("❌ Error: Please provide PDF filename")
                print("Usage: python combined_scraper.py --single-pdf <filename.pdf>")
        elif sys.argv[1] == "--upload":
            # Process uploaded PDF (frontend-friendly)
            if len(sys.argv) > 2:
                pdf_filename = sys.argv[2]
                process_uploaded_pdf(pdf_filename)
            else:
                print("❌ Error: Please provide PDF filename")
                print("Usage: python combined_scraper.py --upload <filename.pdf>")
        elif sys.argv[1] == "--help":
            print("Combined HFCL Cable Data Scraper and API Poster")
            print("=" * 50)
            print("Usage:")
            print("  python combined_scraper.py                    # Run main scraper with monitoring")
            print("  python combined_scraper.py --run-all         # Run all functionalities in one click")
            print("  python combined_scraper.py --upload <file>   # Process uploaded PDF (frontend-friendly)")
            print("  python combined_scraper.py --single-pdf <file> # Process single PDF file")
            print("  python combined_scraper.py --post-api        # Post existing JSON files to API")
            print("  python combined_scraper.py --api-only        # Run only API poster")
            print("  python combined_scraper.py --help            # Show this help message")
            print("\nAngular Integration:")
            print("  Use --run-all for the main 'Process All' button")
            print("  Use --upload for the Upload button (processes selected PDF)")
            print("  Use --single-pdf for individual file upload processing")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        # Run the main PDF processing and monitoring
        main()
