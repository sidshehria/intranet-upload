import json
import re
from typing import List, Dict, Any, Optional

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
