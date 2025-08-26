import os
import json
import pdfplumber
from pathlib import Path
from scraper import parse_datasheets

def validate_json_output(cable_data: dict) -> bool:
    """Validates that the extracted cable data has reasonable values."""
    required_fields = ['fiberCount', 'typeofCable', 'fiberType', 'diameter', 'tensile', 'crush']
    
    for field in required_fields:
        if field not in cable_data:
            print(f"  Warning: Missing field '{field}'")
            return False
    
    # Check for reasonable values
    if cable_data['fiberCount'] and not cable_data['fiberCount'].isdigit():
        print(f"  Warning: Invalid fiber count: {cable_data['fiberCount']}")
        return False
    
    if cable_data['typeofCable'] not in ['UT', 'MT', 'N/A']:
        print(f"  Warning: Invalid cable type: {cable_data['typeofCable']}")
    
    if cable_data['fiberType'] not in ['SM', 'MM', 'N/A']:
        print(f"  Warning: Invalid fiber type: {cable_data['fiberType']}")
    
    return True

def main():
    """
    Entry point of the script. Reads PDF files from the data directory,
    processes them, and saves the output as separate JSON files for each fiber count.
    """
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "scraper/data"
    output_dir = project_root / "scraper/output"

    output_dir.mkdir(exist_ok=True)

    if not data_dir.is_dir():
        print(f"Error: Input directory not found at '{data_dir}'")
        return

    file_contents = {}
    pdf_files = list(data_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in '{data_dir}'.")
        return

    print("--- Starting PDF Scraping Process ---")
    print(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_path in pdf_files:
        print(f"\nReading file: {pdf_path.name}")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = "".join(page.extract_text() + "\n--- PAGE BREAK ---\n" for page in pdf.pages)
                file_contents[pdf_path.name] = full_text
                print(f"  Successfully extracted {len(full_text)} characters")
        except Exception as e:
            print(f"  --> Failed to read {pdf_path.name}. Error: {e}")

    if not file_contents:
        print("Could not extract text from any PDF files. Exiting.")
        return

    print(f"\nProcessing extracted text from {len(file_contents)} files...")
    all_cables_data = parse_datasheets(file_contents)

    if not all_cables_data:
        print("No cable data was extracted. Exiting.")
        return

    print(f"\n--- Extracted {len(all_cables_data)} Cable Variants ---")
    
    # Validate and display extracted data
    valid_count = 0
    for cable in all_cables_data:
        print(f"\nCable {cable['cableID']}: {cable['cableDescription']}")
        print(f"  Fiber Count: {cable['fiberCount']}F")
        print(f"  Type: {cable['typeofCable']}, Fiber: {cable['fiberType']}")
        print(f"  Diameter: {cable['diameter']}")
        print(f"  Tensile: {cable['tensile']}")
        print(f"  Crush: {cable['crush']}")
        
        if validate_json_output(cable):
            valid_count += 1
        print()

    print(f"--- Saving {len(all_cables_data)} JSON Files ---")
    print(f"Valid cables: {valid_count}/{len(all_cables_data)}")
    
    saved_count = 0
    for cable in all_cables_data:
        original_filename = Path(cable['datasheetURL']).stem
        fiber_count = cable['fiberCount']
        
        output_filename = f"{original_filename}_{fiber_count}F.json"
        output_path = output_dir / output_filename

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(cable, f, indent=2)
            print(f"Saved: {output_path.name}")
            saved_count += 1
        except Exception as e:
            print(f"--> Failed to write {output_filename}. Error: {e}")

    print(f"\n--- Success! ---")
    print(f"Saved {saved_count}/{len(all_cables_data)} files in: {output_dir}")
    
    if saved_count < len(all_cables_data):
        print(f"Warning: {len(all_cables_data) - saved_count} files failed to save")

if __name__ == "__main__":
    main()