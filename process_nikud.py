#!/usr/bin/env python3

import sys
import os
from pathlib import Path
from services.nikud_service import NikudService

def main():
    """
    Process nikud from source to target document and output to a new file
    """
    # Command line arguments
    if len(sys.argv) < 4:
        print("Usage: python process_nikud.py <source_file> <target_file> <output_file> [--debug]")
        print("Example: python process_nikud.py source.docx target.docx output.docx --debug")
        return 1

    source_path = sys.argv[1]
    target_path = sys.argv[2]
    output_path = sys.argv[3]
    
    # Check for debug flag
    create_debug_file = "--debug" in sys.argv
    
    # Validate input files
    if not os.path.exists(source_path):
        print(f"Error: Source file '{source_path}' not found.")
        return 1
        
    if not os.path.exists(target_path):
        print(f"Error: Target file '{target_path}' not found.")
        return 1
    
    # Create output directory if needed
    output_dir = Path(output_path).parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create NikudService with API key (from environment variable)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY environment variable not set.")
        print("Please set this variable with your Gemini API key.")
        print("Example: export GEMINI_API_KEY=your_api_key_here")
        return 1
    
    # Create service and process files
    print(f"Processing nikud from '{source_path}' to '{target_path}'")
    print(f"Output will be saved to '{output_path}'")
    
    nikud_service = NikudService(gemini_api_key=api_key)
    nikud_service.process_files(source_path, target_path, output_path, create_debug_file)
    
    print("Processing complete!")
    
    # Show paths to output files
    report_path = output_path.replace('.docx', '_report.txt')
    print(f"- Document saved to: {output_path}")
    print(f"- Report saved to: {report_path}")
    
    if create_debug_file:
        debug_path = output_path.replace('.docx', '_debug.txt')
        print(f"- Debug file saved to: {debug_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 