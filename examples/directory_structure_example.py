#!/usr/bin/env python3
"""
Example script demonstrating the use of directory utilities.

This script shows how to use the directory utilities to ensure that
the necessary directory structure exists before performing operations.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from cosmos_generator.utils.directory_utils import (
    ensure_output_directories,
    get_planet_result_directory,
    get_planet_debug_directory,
    get_planet_example_directory,
    ensure_log_file_directory
)


def main():
    """
    Demonstrate the use of directory utilities.
    """
    print("Ensuring all output directories exist...")
    ensure_output_directories()
    print("Done!")
    
    # Verify that the directories were created
    print("\nVerifying directory structure:")
    
    # Check base output directory
    print(f"- {config.OUTPUT_DIR}: {os.path.exists(config.OUTPUT_DIR)}")
    
    # Check planets directory
    print(f"- {config.PLANETS_DIR}: {os.path.exists(config.PLANETS_DIR)}")
    
    # Check debug directory
    print(f"- {config.PLANETS_DEBUG_DIR}: {os.path.exists(config.PLANETS_DEBUG_DIR)}")
    
    # Check examples directory
    print(f"- {config.PLANETS_EXAMPLES_DIR}: {os.path.exists(config.PLANETS_EXAMPLES_DIR)}")
    
    # Check result directory
    print(f"- {config.PLANETS_RESULT_DIR}: {os.path.exists(config.PLANETS_RESULT_DIR)}")
    
    # Check result subdirectories for each planet type
    print("\nVerifying planet type subdirectories:")
    for planet_type in config.PLANET_TYPES:
        result_dir = os.path.join(config.PLANETS_RESULT_DIR, planet_type)
        print(f"- {result_dir}: {os.path.exists(result_dir)}")
    
    # Demonstrate getting specific directories
    print("\nDemonstrating specific directory functions:")
    
    # Get result directory for a specific planet type
    desert_dir = get_planet_result_directory("desert")
    print(f"Desert result directory: {desert_dir}")
    
    # Get debug directory for terrain textures
    terrain_dir = get_planet_debug_directory("terrain")
    print(f"Terrain textures directory: {terrain_dir}")
    
    # Get debug directory for cloud textures with a specific seed
    clouds_dir = get_planet_debug_directory("clouds", 12345)
    print(f"Cloud textures directory for seed 12345: {clouds_dir}")
    
    # Get example directory
    example_dir = get_planet_example_directory("test_clouds")
    print(f"Example directory for test_clouds: {example_dir}")
    
    # Ensure log file directory exists
    ensure_log_file_directory()
    print(f"Log file directory: {os.path.dirname(config.PLANETS_LOG_FILE)}")
    
    print("\nAll directories verified and created successfully!")


if __name__ == "__main__":
    main()
