# HFCL Cable Data Processing System - Setup Guide

This system integrates an Angular frontend with a Python Flask backend to process PDF datasheets and extract cable specifications using the existing `combined_scraper.py` functionality.

## 🏗️ Architecture

```
project_root/
├── scraper/                    # Existing Python scraper
│   ├── combined_scraper.py    # Main scraper logic
│   ├── data/                  # PDF input directory
│   └── output/                # JSON output directory
├── backend/                    # New Python Flask backend
│   ├── app.py                 # Flask application
│   ├── start_backend.py       # Standard startup script
│   ├── run_simple.py          # Windows-compatible startup script
│   ├── cleanup_files.py       # File cleanup script for permission issues
│   └── requirements.txt       # Python dependencies
└── src/                       # Angular frontend
    └── app/
        ├── file-upload/        # File upload component
        └── services/
            └── api.service.ts  # API communication service
```

## 🚀 Quick Start

### 1. Start the Python Backend

#### Option A: Standard Method (Linux/Mac)
```bash
# Navigate to the backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the Flask server
python start_backend.py
```

#### Option B: Windows-Compatible Method (Recommended for Windows)
```bash
# Navigate to the backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the Flask server (Windows-compatible)
python run_simple.py
```

#### Option C: Windows Batch File (Easiest for Windows)
```bash
# Double-click start_backend.bat from the project root
# Or run from command prompt:
start_backend.bat
```

The backend will start on `http://localhost:5000` and automatically import the scraper functionality.

### 2. Start the Angular Frontend

```bash
# In a new terminal, navigate to the project root
cd /path/to/project

# Install Angular dependencies (if not already done)
npm install

# Start the Angular development server
ng serve
```

The frontend will be available at `http://localhost:4200`.

## 🔧 Backend Configuration

### API Endpoints

- `POST /api/upload` - Upload and process PDF files
- `POST /api/process-all` - Process all PDF files in data directory
- `GET /api/health` - Health check
- `GET /api/files` - List processed files

### Environment Variables

The backend automatically configures itself based on the project structure. No additional environment variables are required.

## 📁 File Processing Workflow

1. **User selects PDF** → File is validated and prepared
2. **Upload button clicked** → File is sent to Python backend
3. **Backend processes PDF** → Uses `combined_scraper.py` functionality
4. **Data extraction** → Cable specifications are extracted and formatted
5. **API posting** → Data is automatically posted to HFCL API (if configured)
6. **Results display** → Extracted data is shown in the frontend

## 🔍 Troubleshooting

### Permission Denied Errors

If you encounter "Permission denied" errors when uploading files:

1. **Use the cleanup script (Recommended):**
   ```bash
   cd backend
   python cleanup_files.py
   ```

2. **Or use the Windows batch file cleanup option:**
   ```bash
   start_backend.bat
   # Choose option 2: Cleanup Files
   ```

3. **Manual cleanup:**
   - Close any applications that might be using the PDF files
   - Delete files in `backend/uploads/`, `backend/processed/`, `backend/output/`
   - Delete files in `scraper/data/` and `scraper/output/`
   - Restart the backend

### Windows-Specific Issues

If you encounter threading errors on Windows:

1. **Use the Windows-compatible startup:**
   ```bash
   python backend/run_simple.py
   ```

2. **Or use the batch file:**
   ```bash
   start_backend.bat
   ```

3. **Common Windows solutions:**
   - Close any other Python processes
   - Restart your terminal/command prompt
   - Run as Administrator if needed
   - Make sure you're in the project root directory

### Backend Connection Issues

If you see "Backend offline" status:

1. **Check if Python backend is running:**
   ```bash
   # For Windows (recommended):
   python backend/run_simple.py
   
   # For Linux/Mac:
   python backend/start_backend.py
   ```

2. **Verify Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Check port availability:**
   - Ensure port 5000 is not used by another service
   - Change port in `backend/app.py` if needed

### Import Errors

If you get import errors when starting the backend:

1. **Run from project root:**
   ```bash
   # Don't run from inside backend/ directory
   # Run from project root instead
   python backend/run_simple.py  # Windows
   python backend/start_backend.py  # Linux/Mac
   ```

2. **Check Python path:**
   The startup script automatically adds the scraper directory to Python path.

### PDF Processing Issues

1. **Check file format:** Only PDF files are supported
2. **Verify scraper functionality:** Test the scraper independently first
3. **Check logs:** Backend provides detailed logging for debugging

## 🧪 Testing

### Test Backend Health

```bash
curl http://localhost:5000/api/health
```

### Test File Upload

```bash
curl -X POST -F "file=@test.pdf" http://localhost:5000/api/upload
```

### Test Batch Processing

```bash
curl -X POST http://localhost:5000/api/process-all
```

## 📊 Data Flow

```
PDF Upload → Flask Backend → combined_scraper.py → Data Extraction → JSON Generation → API Posting → Frontend Display
```

## 🔐 Security Notes

- The backend runs in debug mode for development (Linux/Mac) or debug=False for Windows
- CORS is enabled for Angular frontend communication
- File uploads are validated for PDF format only
- Temporary files are automatically cleaned up
- Unique filenames are generated to prevent conflicts

## 🚀 Production Deployment

For production deployment:

1. **Disable debug mode** in `backend/app.py`
2. **Configure proper CORS** settings
3. **Add authentication** if required
4. **Use production WSGI server** (Gunicorn, uWSGI)
5. **Configure reverse proxy** (Nginx, Apache)

## 📝 API Response Format

### Successful Upload Response

```json
{
  "success": true,
  "message": "File processed successfully. Generated 2 cable variants.",
  "results": [
    {
      "metadata": {
        "fiber_type": "G.652D",
        "source_file": "example.pdf",
        "cable_description": "24F Indoor LSZH loose-tube cable"
      },
      "technical_specifications": {
        "Cable Properties": {
          "Fiber Count": "24F",
          "Cable Type": "MT",
          "Tube Type": "Multitube",
          "Fiber Type": "G.652D",
          "Diameter": "8.5 ± 0.5 mm",
          "Tensile Strength": "600 N",
          "Crush Resistance": "1000 N/10cm",
          "NESC Condition": "Temperature range: -40°C, +70°C",
          "Blowing Length": "N/A"
        },
        "API Status": {
          "Records Posted": 1,
          "Successful": 1,
          "Failed": 0,
          "Processing Time": "2.5s"
        }
      }
    }
  ]
}
```

### Error Response

```json
{
  "success": false,
  "error": "PDF processing failed: Invalid file format"
}
```

## 🎯 Key Features

- ✅ **Seamless Integration** with existing `combined_scraper.py`
- ✅ **Real-time Processing** with progress indicators
- ✅ **Automatic API Posting** to HFCL database
- ✅ **Comprehensive Error Handling** with user-friendly messages
- ✅ **Backend Status Monitoring** with retry functionality
- ✅ **Responsive Design** for all device sizes
- ✅ **Detailed Logging** for debugging and monitoring
- ✅ **Windows Compatibility** with dedicated startup scripts
- ✅ **Permission Issue Resolution** with built-in cleanup tools
- ✅ **Unique Filename Generation** to prevent conflicts

## 🪟 Windows-Specific Features

- **Dedicated Windows startup script** (`run_simple.py`)
- **Batch file for easy startup** (`start_backend.bat`)
- **Automatic platform detection** and configuration
- **Threading issue prevention** with `use_reloader=False`
- **File cleanup tools** to resolve permission issues

## 🧹 File Management Features

- **Automatic cleanup** of temporary files
- **Unique filename generation** to prevent conflicts
- **Safe file operations** with comprehensive error handling
- **Permission issue resolution** with cleanup scripts
- **Organized file structure** with separate directories for uploads, processed files, and outputs

## 📞 Support

If you encounter issues:

1. **Permission errors:** Use `python backend/cleanup_files.py` or `start_backend.bat` option 2
2. **Windows users:** Use `python backend/run_simple.py` or `start_backend.bat`
3. **Linux/Mac users:** Use `python backend/start_backend.py`
4. Check the backend console for detailed error messages
5. Verify all dependencies are installed correctly
6. Ensure the scraper functionality works independently
7. Check network connectivity between frontend and backend

The system is designed to be robust and provide clear feedback for any issues that arise during processing.
