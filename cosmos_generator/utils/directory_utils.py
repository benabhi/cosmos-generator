"""
Directory utilities for Cosmos Generator.

This module provides functions for managing directories and files,
ensuring that the necessary directory structure exists before operations.
"""
import os
from typing import Dict, Any, Optional

import config


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory to ensure
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def ensure_directory_structure(structure: Dict[str, Any], base_path: str = "") -> None:
    """
    Recursively ensure that a directory structure exists.
    
    Args:
        structure: Dictionary representing the directory structure
        base_path: Base path for the structure (default: current directory)
    """
    for dir_name, substructure in structure.items():
        # Construct the full path
        dir_path = os.path.join(base_path, dir_name) if base_path else dir_name
        
        # Ensure this directory exists
        ensure_directory_exists(dir_path)
        
        # Recursively process subdirectories
        if substructure:
            ensure_directory_structure(substructure, dir_path)


def ensure_output_directories() -> None:
    """
    Ensure that all output directories defined in the configuration exist.
    This is a centralized function to verify and create the entire directory structure.
    """
    ensure_directory_structure(config.DIRECTORY_STRUCTURE)


def ensure_file_directory(file_path: str) -> None:
    """
    Ensure that the directory containing a file exists.
    
    Args:
        file_path: Path to the file
    """
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory_exists(directory)


def get_planet_result_directory(planet_type: str) -> str:
    """
    Get the result directory for a specific planet type, ensuring it exists.
    
    Args:
        planet_type: Type of planet
        
    Returns:
        Path to the result directory
    """
    result_dir = os.path.join(config.PLANETS_RESULT_DIR, planet_type.lower())
    ensure_directory_exists(result_dir)
    return result_dir


def get_planet_debug_directory(texture_type: Optional[str] = None, seed: Optional[int] = None) -> str:
    """
    Get a debug directory for planet generation, ensuring it exists.
    
    Args:
        texture_type: Optional type of texture (terrain, clouds, etc.)
        seed: Optional seed for specific texture directories
        
    Returns:
        Path to the debug directory
    """
    if not texture_type:
        # Return the base debug directory
        ensure_directory_exists(config.PLANETS_DEBUG_DIR)
        return config.PLANETS_DEBUG_DIR
        
    if texture_type == "terrain":
        debug_dir = config.PLANETS_TERRAIN_TEXTURES_DIR
    elif texture_type == "clouds" and seed is not None:
        debug_dir = os.path.join(config.PLANETS_CLOUDS_TEXTURES_DIR, str(seed))
    else:
        # For other texture types, use a generic approach
        debug_dir = os.path.join(config.PLANETS_TEXTURES_DIR, texture_type)
        if seed is not None:
            debug_dir = os.path.join(debug_dir, str(seed))
    
    ensure_directory_exists(debug_dir)
    return debug_dir


def get_planet_example_directory(example_name: str) -> str:
    """
    Get an example directory for planet generation, ensuring it exists.
    
    Args:
        example_name: Name of the example
        
    Returns:
        Path to the example directory
    """
    example_dir = os.path.join(config.PLANETS_EXAMPLES_DIR, example_name)
    ensure_directory_exists(example_dir)
    return example_dir


def ensure_log_file_directory() -> None:
    """
    Ensure that the directory containing the log file exists.
    """
    ensure_directory_exists(os.path.dirname(config.PLANETS_LOG_FILE))
