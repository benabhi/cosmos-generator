"""
Utility functions for the web interface.
"""
import os
import json
import glob
import subprocess
from typing import List, Dict, Any, Optional, Tuple
import threading
import time

import config
from cosmos_generator.utils.logger import logger


def get_planet_types() -> List[str]:
    """
    Get a list of available planet types.

    Returns:
        List of planet types
    """
    return config.PLANET_TYPES


def get_planet_variations() -> Dict[str, List[str]]:
    """
    Get a dictionary of planet types and their variations.

    Returns:
        Dictionary mapping planet types to their variations
    """
    return config.PLANET_VARIATIONS


def get_default_variations() -> Dict[str, str]:
    """
    Get a dictionary of default variations for each planet type.

    Returns:
        Dictionary mapping planet types to their default variations
    """
    return config.DEFAULT_PLANET_VARIATIONS


def get_generated_planets() -> List[Dict[str, Any]]:
    """
    Get a list of all generated planets.

    Returns:
        List of dictionaries containing planet information
    """
    planets = []

    # Get the absolute path to the output directory
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Iterate through each planet type directory
    for planet_type in config.PLANET_TYPES:
        # Use absolute path
        type_dir = os.path.join(base_dir, config.PLANETS_RESULT_DIR, planet_type.lower())

        # Skip if directory doesn't exist
        if not os.path.exists(type_dir):
            continue

        # Find all PNG files in the directory
        planet_files = glob.glob(os.path.join(type_dir, "*.png"))

        for file_path in planet_files:
            # Extract seed from filename
            filename = os.path.basename(file_path)
            seed = os.path.splitext(filename)[0]

            # Parse the filename to extract parameters
            # Format: [seed]_[variation]_[atmosphere]_[clouds]_[rings].png
            parts = seed.split('_')

            # Basic info
            planet_info = {
                "type": planet_type,
                "seed": parts[0] if len(parts) > 0 else seed,
                "path": file_path,
                "filename": filename,
                "url": f"/static/planets/{planet_type.lower()}/{filename}",
                "params": {}
            }

            # Add parameters based on filename parts
            if len(parts) >= 5:  # We have seed, variation, atmosphere, clouds, rings
                # Add variation (part 1)
                planet_info["params"]["variation"] = parts[1]

                # Add atmosphere parameter (0 or 1)
                if parts[2] == '1':
                    planet_info["params"]["atmosphere"] = True

                # Add clouds parameter (0 or 1)
                if parts[3] == '1':
                    planet_info["params"]["clouds"] = True

                # Add rings parameter (0 or 1)
                if parts[4] == '1':
                    planet_info["params"]["rings"] = True
            else:
                # For older filenames or non-standard formats, use defaults
                planet_info["params"]["variation"] = config.DEFAULT_PLANET_VARIATIONS.get(planet_type.lower(), "standard")


            planets.append(planet_info)

    return planets


def filter_planets(planets: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filter planets based on criteria.

    Args:
        planets: List of planet dictionaries
        filters: Dictionary of filter criteria

    Returns:
        Filtered list of planets
    """
    result = planets

    # Filter by type
    if 'type' in filters and filters['type']:
        result = [p for p in result if p['type'].lower() == filters['type'].lower()]

    # Filter by features
    if 'has_rings' in filters and filters['has_rings']:
        result = [p for p in result if 'params' in p and 'rings' in p['params']]

    if 'has_atmosphere' in filters and filters['has_atmosphere']:
        result = [p for p in result if 'params' in p and 'atmosphere' in p['params']]

    if 'has_clouds' in filters and filters['has_clouds']:
        result = [p for p in result if 'params' in p and 'clouds' in p['params']]

    # Filter by seed
    if 'seed' in filters and filters['seed']:
        result = [p for p in result if filters['seed'] in p['seed']]

    return result


# Dictionary to store running generation processes
generation_processes = {}


def generate_planet_async(params: Dict[str, Any]) -> str:
    """
    Generate a planet asynchronously.

    Args:
        params: Dictionary of generation parameters

    Returns:
        Process ID for tracking the generation
    """
    # Generate a unique process ID
    process_id = str(int(time.time() * 1000))

    # Start a new thread for generation
    thread = threading.Thread(
        target=_generate_planet_thread,
        args=(process_id, params)
    )

    # Store process information
    generation_processes[process_id] = {
        "status": "starting",
        "params": params,
        "start_time": time.time(),
        "logs": [],
        "result": None,
        "error": None
    }

    # Start the thread
    thread.daemon = True
    thread.start()

    return process_id


def _generate_planet_thread(process_id: str, params: Dict[str, Any]) -> None:
    """
    Thread function for planet generation.

    Args:
        process_id: Unique process ID
        params: Generation parameters
    """
    try:
        # Update status
        generation_processes[process_id]["status"] = "running"

        # Build command
        cmd = ["python", "-m", "cosmos_generator", "planet", "generate"]

        # Define valid parameters for the CLI
        valid_params = [
            'type', 'seed', 'rings', 'atmosphere', 'atmosphere_glow', 'atmosphere_halo',
            'atmosphere_thickness', 'atmosphere_blur', 'clouds', 'variation',
            'light_intensity', 'light_angle', 'rotation', 'zoom'
        ]

        # Add parameters
        for key, value in params.items():
            if key == 'output':
                continue  # Skip output, we'll handle it separately

            # Skip invalid parameters
            if key not in valid_params:
                continue

            # Convert parameter names from snake_case to kebab-case for CLI
            cli_key = key.replace('_', '-')

            if isinstance(value, bool):
                if value:
                    cmd.append(f"--{cli_key}")
            else:
                cmd.append(f"--{cli_key}")
                cmd.append(str(value))

        # Set output path
        # Ensure planet type is never empty
        planet_type = params.get('type', 'desert')
        if not planet_type.strip():
            planet_type = 'desert'
        planet_type = planet_type.lower()
        seed = params.get('seed', str(int(time.time())))

        # Standardize seed to 8 characters (pad with zeros if needed)
        # If seed is longer than 8 characters, use the first 8
        seed_str = str(seed)
        if len(seed_str) > 8:
            seed_str = seed_str[:8]
        else:
            seed_str = seed_str.zfill(8)

        # Create filename with standardized format: [seed]_[variation]_[atmosphere]_[clouds]_[rings].png
        # Where atmosphere, clouds, rings are 0 or 1
        has_atmosphere = 1 if params.get('atmosphere', False) else 0
        has_clouds = 1 if 'clouds' in params and float(params['clouds']) > 0 else 0
        has_rings = 1 if params.get('rings', False) else 0

        # Get variation (use default if not specified or empty)
        variation = params.get('variation', '')
        if not variation.strip():
            variation = config.DEFAULT_PLANET_VARIATIONS.get(planet_type.lower(), 'standard')

        # Create filename parts
        filename_parts = [seed_str, variation, str(has_atmosphere), str(has_clouds), str(has_rings)]

        # Join parts with underscores
        filename = "_".join(filename_parts) + ".png"

        # Get the absolute path to the output directory
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

        # Set output path with absolute path
        output_dir = os.path.join(base_dir, config.PLANETS_RESULT_DIR, planet_type)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, filename)
        cmd.extend(["--output", output_path])

        # Log the command and parameters for debugging
        cmd_str = ' '.join(cmd)
        generation_processes[process_id]["logs"].append(f"Running command: {cmd_str}")
        generation_processes[process_id]["logs"].append(f"Parameters: {params}")
        generation_processes[process_id]["logs"].append(f"Working directory: {os.getcwd()}")

        # Run the command
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Capture output in real-time
            for line in iter(process.stdout.readline, ''):
                generation_processes[process_id]["logs"].append(line.strip())

            # Wait for process to complete
            return_code = process.wait()
            generation_processes[process_id]["logs"].append(f"Process completed with return code: {return_code}")
        except Exception as e:
            generation_processes[process_id]["logs"].append(f"Error executing command: {str(e)}")
            return_code = 1  # Set error code

        # Update status based on return code
        if return_code == 0:
            generation_processes[process_id]["status"] = "completed"
            generation_processes[process_id]["result"] = {
                "path": output_path,
                "url": f"/static/planets/{planet_type.lower()}/{filename}"
            }
        else:
            generation_processes[process_id]["status"] = "failed"
            generation_processes[process_id]["error"] = "Generation process failed"

    except Exception as e:
        # Handle any exceptions
        generation_processes[process_id]["status"] = "failed"
        generation_processes[process_id]["error"] = str(e)

    # Set end time
    generation_processes[process_id]["end_time"] = time.time()


def get_generation_status(process_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the status of a generation process.

    Args:
        process_id: Process ID

    Returns:
        Dictionary with process status information or None if not found
    """
    return generation_processes.get(process_id)


def get_recent_logs(lines: int = 100, log_type: str = 'planets') -> List[str]:
    """
    Get recent log entries.

    Args:
        lines: Number of lines to retrieve
        log_type: Type of log to retrieve ('planets' or 'web')

    Returns:
        List of log lines
    """
    if log_type == 'web':
        # Get web server logs
        log_file = os.path.join(config.OUTPUT_DIR, 'web.log')
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    # Read the last 'lines' lines
                    return list(f.readlines())[-lines:]
            except Exception as e:
                return [f"Error reading web logs: {str(e)}"]
        return ["No web logs found"]
    else:
        # Get planet generation logs
        return logger.get_log_file_content(lines)


def get_planet_preview(planet_type: str, seed: str) -> Optional[str]:
    """
    Get the path to a planet preview image.

    Args:
        planet_type: Type of planet
        seed: Seed value

    Returns:
        Path to preview image or None if not found
    """
    path = os.path.join(config.PLANETS_RESULT_DIR, planet_type.lower(), f"{seed}.png")
    if os.path.exists(path):
        return path
    return None
