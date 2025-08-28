#!/usr/bin/env python3
"""
Cleanup script to resolve file permission issues
Run this if you encounter permission errors with existing files
"""

import os
import shutil
from pathlib import Path

def cleanup_files():
    """Clean up files that might be causing permission issues"""
    
    # Get project paths
    current_dir = Path(__file__).parent
    scraper_dir = current_dir.parent / "scraper"
    
    print("🧹 Starting file cleanup...")
    print(f"📁 Current directory: {current_dir}")
    print(f"📁 Scraper directory: {scraper_dir}")
    
    # Clean up backend directories
    backend_dirs = [
        current_dir / "uploads",
        current_dir / "processed", 
        current_dir / "output"
    ]
    
    for dir_path in backend_dirs:
        if dir_path.exists():
            print(f"🗑️  Cleaning {dir_path.name} directory...")
            try:
                # Remove all files in the directory
                for file_path in dir_path.glob("*"):
                    try:
                        if file_path.is_file():
                            file_path.unlink()
                            print(f"  ✅ Removed: {file_path.name}")
                        elif file_path.is_dir():
                            shutil.rmtree(file_path)
                            print(f"  ✅ Removed directory: {file_path.name}")
                    except PermissionError:
                        print(f"  ⚠️  Could not remove: {file_path.name} (permission denied)")
                    except Exception as e:
                        print(f"  ❌ Error removing {file_path.name}: {e}")
            except Exception as e:
                print(f"  ❌ Error cleaning {dir_path.name}: {e}")
        else:
            print(f"📁 Creating {dir_path.name} directory...")
            dir_path.mkdir(exist_ok=True)
    
    # Clean up scraper data directory (optional - ask user first)
    scraper_data_dir = scraper_dir / "data"
    if scraper_data_dir.exists():
        print(f"\n🗑️  Found existing scraper data directory: {scraper_data_dir}")
        print("⚠️  This directory contains existing PDF files that might cause conflicts.")
        
        response = input("Do you want to clean this directory? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            try:
                for file_path in scraper_data_dir.glob("*.pdf"):
                    try:
                        file_path.unlink()
                        print(f"  ✅ Removed: {file_path.name}")
                    except PermissionError:
                        print(f"  ⚠️  Could not remove: {file_path.name} (permission denied)")
                    except Exception as e:
                        print(f"  ❌ Error removing {file_path.name}: {e}")
            except Exception as e:
                print(f"  ❌ Error cleaning scraper data directory: {e}")
        else:
            print("  ℹ️  Skipping scraper data directory cleanup")
    
    # Clean up scraper output directory
    scraper_output_dir = scraper_dir / "output"
    if scraper_output_dir.exists():
        print(f"\n🗑️  Cleaning scraper output directory...")
        try:
            for file_path in scraper_output_dir.glob("*.json"):
                try:
                    file_path.unlink()
                    print(f"  ✅ Removed: {file_path.name}")
                except PermissionError:
                    print(f"  ⚠️  Could not remove: {file_path.name} (permission denied)")
                except Exception as e:
                    print(f"  ❌ Error removing {file_path.name}: {e}")
        except Exception as e:
            print(f"  ❌ Error cleaning scraper output directory: {e}")
    
    print("\n✅ Cleanup complete!")
    print("💡 You can now try uploading files again.")
    print("🚀 Start the backend with: python run_simple.py")

if __name__ == "__main__":
    try:
        cleanup_files()
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
