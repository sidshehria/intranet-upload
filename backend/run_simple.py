#!/usr/bin/env python3
"""
Simple startup script for Windows compatibility
This script avoids the threading issues that can occur with Flask on Windows
"""

import sys
import os
import platform
from pathlib import Path

def main():
    # Add the parent directory to Python path to access the scraper
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    scraper_dir = parent_dir / "scraper"
    
    # Add both directories to Python path
    sys.path.insert(0, str(parent_dir))
    sys.path.insert(0, str(scraper_dir))
    
    print("🔧 Setting up Python paths...")
    print(f"📁 Current directory: {current_dir}")
    print(f"📁 Parent directory: {parent_dir}")
    print(f"📁 Scraper directory: {scraper_dir}")
    print(f"🖥️  Platform: {platform.system()}")
    print(f"🐍 Python version: {platform.python_version()}")
    
    try:
        # Try to import the scraper modules
        print("📦 Importing scraper modules...")
        from combined_scraper import process_uploaded_pdf, run_all_functionalities
        print("✅ Successfully imported scraper modules")
        
        # Import Flask app
        print("🚀 Importing Flask application...")
        from app import app
        
        print("🎉 Backend started successfully!")
        print("🌐 Server will be available at: http://localhost:5000")
        print("📡 API endpoints:")
        print("  - POST /api/upload - Upload and process PDF files")
        print("  - POST /api/process-all - Process all PDF files")
        print("  - GET  /api/health - Health check")
        print("  - GET  /api/files - List processed files")
        print("=" * 60)
        
        # Start the Flask app with Windows-compatible settings
        print("🚀 Starting Flask server...")
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔍 This usually means the scraper modules are not available")
        print("💡 Make sure you're running this from the project root directory")
        print("📁 Expected structure:")
        print("   project_root/")
        print("   ├── scraper/")
        print("   │   └── combined_scraper.py")
        print("   └── backend/")
        print("       └── run_simple.py")
        print("\n💡 Try running from the project root:")
        print("   python backend/run_simple.py")
        return 1
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    if exit_code != 0:
        print("\n💡 If you're still having issues, try:")
        print("   1. Close any other Python processes")
        print("   2. Restart your terminal/command prompt")
        print("   3. Make sure you're in the project root directory")
        print("   4. Run: python backend/run_simple.py")
        input("\nPress Enter to exit...")
    sys.exit(exit_code)
