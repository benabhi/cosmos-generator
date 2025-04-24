"""
Directory utilities for Cosmos Generator.

This module provides functions for managing directories and files,
ensuring that the necessary directory structure exists before operations.
"""
import os
from typing import Dict, Any

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


def get_planet_type_directory(planet_type: str) -> str:
    """
    Get the directory for a specific planet type, ensuring it exists.

    Args:
        planet_type: Type of planet

    Returns:
        Path to the planet type directory
    """
    type_dir = os.path.join(config.PLANETS_DIR, planet_type.lower())
    ensure_directory_exists(type_dir)
    return type_dir


def get_planet_seed_directory(planet_type: str, seed: str) -> str:
    """
    Get the directory for a specific planet seed, ensuring it exists.

    Args:
        planet_type: Type of planet
        seed: Seed used for generation (as string)

    Returns:
        Path to the seed directory
    """
    seed_dir = config.get_planet_seed_dir(planet_type, seed)
    ensure_directory_exists(seed_dir)
    return seed_dir


def ensure_planet_seed_structure(planet_type: str, seed: str) -> None:
    """
    Ensure that the directory structure for a planet seed exists.

    Args:
        planet_type: Type of planet
        seed: Seed used for generation (as string)
    """
    # Ensure the seed directory exists
    seed_dir = get_planet_seed_directory(planet_type, seed)

    # Ensure the log file directory exists
    log_path = config.get_planet_log_path(planet_type, seed)
    ensure_file_directory(log_path)

    # Ensure the details CSV file directory exists
    details_path = config.get_planet_details_path(planet_type, seed)
    ensure_file_directory(details_path)


def ensure_log_file_directory() -> None:
    """
    Ensure that the directory containing the log file exists.
    """
    ensure_directory_exists(os.path.dirname(config.PLANETS_LOG_FILE))
