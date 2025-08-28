#!/usr/bin/env python3
"""
Flask Backend for HFCL Cable Data Processing
Integrates with the existing combined_scraper.py functionality
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import tempfile
import shutil
from pathlib import Path
import traceback
import json
import platform
import time
import uuid

# Add the scraper directory to Python path
current_dir = Path(__file__).parent
scraper_dir = current_dir.parent / "scraper"
sys.path.insert(0, str(scraper_dir))

# Import the scraper functionality
from combined_scraper import process_uploaded_pdf, run_all_functionalities

app = Flask(__name__)
CORS(app)  # Enable CORS for Angular frontend

# Configuration
UPLOAD_FOLDER = current_dir / "uploads"
PROCESSED_FOLDER = current_dir / "processed"
OUTPUT_FOLDER = current_dir / "output"

# Create necessary directories
UPLOAD_FOLDER.mkdir(exist_ok=True)
PROCESSED_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_unique_filename(original_filename, target_dir):
    """Generate a unique filename to avoid conflicts"""
    base_name = Path(original_filename).stem
    extension = Path(original_filename).suffix
    
    # Try the original name first
    target_path = target_dir / original_filename
    
    if not target_path.exists():
        return original_filename
    
    # If file exists, add timestamp and random suffix
    timestamp = int(time.time())
    random_suffix = str(uuid.uuid4())[:8]
    unique_filename = f"{base_name}_{timestamp}_{random_suffix}{extension}"
    
    return unique_filename

def safe_copy_file(source_path, target_path):
    """Safely copy a file with error handling"""
    try:
        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # If target file exists, remove it first
        if target_path.exists():
            try:
                target_path.unlink()
            except PermissionError:
                # If we can't remove, use a unique name
                unique_name = get_unique_filename(target_path.name, target_path.parent)
                target_path = target_path.parent / unique_name
        
        # Copy the file
        shutil.copy2(str(source_path), str(target_path))
        return target_path, None
        
    except PermissionError as e:
        return None, f"Permission denied: {str(e)}"
    except Exception as e:
        return None, f"File copy error: {str(e)}"

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle PDF file upload and processing"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Generate unique filename for upload
        unique_filename = get_unique_filename(file.filename, UPLOAD_FOLDER)
        temp_path = UPLOAD_FOLDER / unique_filename
        
        try:
            # Save uploaded file temporarily
            file.save(str(temp_path))
            print(f"📁 File saved temporarily: {temp_path}")
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to save uploaded file: {str(e)}'
            }), 500
        
        # Copy file to scraper data directory for processing
        scraper_data_dir = scraper_dir / "data"
        scraper_data_dir.mkdir(exist_ok=True)
        
        # Generate unique filename for scraper directory
        scraper_filename = get_unique_filename(file.filename, scraper_data_dir)
        target_path = scraper_data_dir / scraper_filename
        
        # Safely copy the file
        copied_path, copy_error = safe_copy_file(temp_path, target_path)
        if copy_error:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
            return jsonify({
                'success': False,
                'error': f'Failed to copy file to scraper directory: {copy_error}'
            }), 500
        
        print(f"📁 File copied to scraper data directory: {copied_path}")
        
        # Process the PDF using the existing scraper functionality
        print(f"🚀 Starting PDF processing for: {scraper_filename}")
        
        try:
            # Use the process_uploaded_pdf function from combined_scraper.py
            result = process_uploaded_pdf(scraper_filename)
            
            if result['success']:
                # Get the generated JSON files
                scraper_output_dir = scraper_dir / "output"
                pdf_stem = Path(scraper_filename).stem
                json_files = list(scraper_output_dir.glob(f"{pdf_stem}_*.json"))
                
                # Load the JSON data for frontend display
                extracted_data = []
                for json_file in json_files:
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            cable_data = json.load(f)
                            # Format data for frontend display
                            formatted_data = {
                                'metadata': {
                                    'fiber_type': cable_data.get('fiberType', 'Unknown'),
                                    'source_file': file.filename,  # Use original filename for display
                                    'cable_description': cable_data.get('cableDescription', 'Unknown')
                                },
                                'technical_specifications': {
                                    'Cable Properties': {
                                        'Fiber Count': cable_data.get('fiberCount', 'N/A'),
                                        'Cable Type': cable_data.get('typeofCable', 'N/A'),
                                        'Tube Type': cable_data.get('tube', 'N/A'),
                                        'Fiber Type': cable_data.get('fiberType', 'N/A'),
                                        'Diameter': cable_data.get('diameter', 'N/A'),
                                        'Tensile Strength': cable_data.get('tensile', 'N/A'),
                                        'Crush Resistance': cable_data.get('crush', 'N/A'),
                                        'NESC Condition': cable_data.get('nescCondition', 'N/A'),
                                        'Blowing Length': cable_data.get('blowingLength', 'N/A')
                                    },
                                    'API Status': {
                                        'Records Posted': result.get('api_total_count', 0),
                                        'Successful': result.get('api_success_count', 0),
                                        'Failed': result.get('api_failure_count', 0),
                                        'Processing Time': f"{result.get('processing_time_seconds', 0)}s"
                                    }
                                },
                                'document_content': {
                                    'Processing Summary': f"Successfully processed {file.filename} in {result.get('processing_time_seconds', 0)} seconds"
                                }
                            }
                            extracted_data.append(formatted_data)
                    except Exception as e:
                        print(f"❌ Error loading JSON file {json_file}: {e}")
                
                # Move processed file to processed folder (use original filename)
                processed_filename = get_unique_filename(file.filename, PROCESSED_FOLDER)
                processed_path = PROCESSED_FOLDER / processed_filename
                
                try:
                    shutil.move(str(copied_path), str(processed_path))
                    print(f"📁 Moved processed file to: {processed_path}")
                except Exception as e:
                    print(f"⚠️  Warning: Could not move processed file: {e}")
                    # Try to copy instead
                    try:
                        shutil.copy2(str(copied_path), str(processed_path))
                        copied_path.unlink()  # Remove from scraper directory
                    except Exception as copy_e:
                        print(f"⚠️  Warning: Could not copy processed file: {copy_e}")
                
                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()
                
                print(f"✅ Processing complete. Generated {len(extracted_data)} cable variants")
                
                return jsonify({
                    'success': True,
                    'message': f'File processed successfully. Generated {len(extracted_data)} cable variants.',
                    'results': extracted_data,
                    'processing_summary': {
                        'pdf_processed': result.get('pdf_processed', False),
                        'api_posted': result.get('api_posted', False),
                        'cables_extracted': result.get('cables_extracted', 0),
                        'api_success_count': result.get('api_success_count', 0),
                        'api_failure_count': result.get('api_failure_count', 0),
                        'processing_time_seconds': result.get('processing_time_seconds', 0)
                    }
                })
            else:
                # Processing failed
                error_msg = result.get('error', 'Unknown processing error')
                print(f"❌ Processing failed: {error_msg}")
                
                # Clean up files
                if temp_path.exists():
                    temp_path.unlink()
                if copied_path and copied_path.exists():
                    try:
                        copied_path.unlink()
                    except:
                        pass
                
                return jsonify({
                    'success': False,
                    'error': f'PDF processing failed: {error_msg}'
                }), 500
                
        except Exception as e:
            error_msg = f"Error during PDF processing: {str(e)}"
            print(f"❌ {error_msg}")
            print(traceback.format_exc())
            
            # Clean up files
            if temp_path.exists():
                temp_path.unlink()
            if copied_path and copied_path.exists():
                try:
                    copied_path.unlink()
                except:
                    pass
            
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
            
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/process-all', methods=['POST'])
def process_all_files():
    """Process all PDF files in the data directory"""
    try:
        print("🚀 Starting batch processing of all PDF files...")
        
        # Use the run_all_functionalities function from combined_scraper.py
        result = run_all_functionalities()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'All files processed successfully',
                'summary': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error during batch processing')
            }), 500
            
    except Exception as e:
        error_msg = f"Error during batch processing: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'HFCL Cable Data Processing Backend',
        'version': '1.0.0',
        'scraper_available': scraper_dir.exists(),
        'platform': platform.system(),
        'python_version': platform.python_version()
    })

@app.route('/api/files', methods=['GET'])
def list_files():
    """List all processed files"""
    try:
        processed_files = []
        for file_path in PROCESSED_FOLDER.glob("*.pdf"):
            processed_files.append({
                'filename': file_path.name,
                'size': file_path.stat().st_size,
                'modified': file_path.stat().st_mtime
            })
        
        return jsonify({
            'success': True,
            'files': processed_files
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting HFCL Cable Data Processing Backend...")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"📁 Processed folder: {PROCESSED_FOLDER}")
    print(f"📁 Output folder: {OUTPUT_FOLDER}")
    print(f"🔧 Scraper directory: {scraper_dir}")
    print(f"🖥️  Platform: {platform.system()}")
    print("=" * 60)
    
    # Windows-compatible configuration
    if platform.system() == 'Windows':
        print("🪟 Windows detected - using compatible configuration")
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    else:
        print("🐧 Unix/Linux detected - using standard configuration")
        app.run(debug=True, host='0.0.0.0', port=5000)
