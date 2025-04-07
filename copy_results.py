import os
import shutil
import sys
import datetime

def copy_results(temp_dir, output_name=None):
    """Copy the section matcher results to a permanent location"""
    if not os.path.exists(temp_dir):
        print(f"Error: Directory {temp_dir} does not exist")
        return False
    
    # Create a results directory if it doesn't exist
    results_dir = os.path.join(os.getcwd(), "section_matcher_results")
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Create a unique name for this run
    if not output_name:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"matcher_results_{timestamp}"
    
    output_dir = os.path.join(results_dir, output_name)
    
    # Don't overwrite existing directories
    if os.path.exists(output_dir):
        print(f"Warning: Directory {output_dir} already exists")
        return False
    
    # Copy the entire directory
    try:
        shutil.copytree(temp_dir, output_dir)
        print(f"Results copied to: {output_dir}")
        return True
    except Exception as e:
        print(f"Error copying results: {str(e)}")
        return False

if __name__ == "__main__":
    # Check if a directory was provided
    if len(sys.argv) > 1:
        temp_dir = sys.argv[1]
        output_name = sys.argv[2] if len(sys.argv) > 2 else None
        copy_results(temp_dir, output_name)
    else:
        print("Usage: python copy_results.py <temp_directory> [output_name]")
        print("Example: python copy_results.py /var/folders/.../section_matcher_test_... source_target_match") 