"""
Utility functions for the web interface.
"""
import os
import csv
import subprocess
from typing import List, Dict, Any, Optional
import threading
import time

import config
from cosmos_generator.utils.csv_utils import get_planet_details, is_seed_used


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


def get_color_palettes() -> Dict[str, Dict[str, Dict[str, List[List[int]]]]]:
    """
    Get a dictionary of color palettes for each planet type.

    Returns:
        Dictionary mapping planet types to their color palettes with all categories
    """
    # Import here to avoid circular imports
    from cosmos_generator.core.color_palette import ColorPalette

    # Create a color palette instance
    color_palette = ColorPalette()

    # Create a dictionary to store the color palettes
    palettes = {}

    # Define the number of palettes for each planet type
    palette_counts = {
        "jovian": 5,  # Jovian planets have 5 palettes
        "default": 3  # Most planets have 3 palettes
    }

    # For each planet type, extract all color categories for each palette ID
    for planet_type in config.PLANET_TYPES:
        planet_type_lower = planet_type.lower()
        palettes[planet_type_lower] = {}

        # Get the planet palettes for this type
        # Note: In ColorPalette, planet types have first letter capitalized
        planet_type_capitalized = planet_type.capitalize()
        if planet_type_capitalized in color_palette.planet_palettes:
            # Determine how many palettes this planet type has
            max_palettes = palette_counts.get(planet_type_lower, palette_counts["default"])

            # Extract all color categories for each palette ID
            for palette_id in range(1, max_palettes + 1):
                palette_id_str = str(palette_id)
                palettes[planet_type_lower][palette_id_str] = {}

                # Check for all possible categories for this palette ID
                for key, value in color_palette.planet_palettes[planet_type_capitalized].items():
                    # Check if this key belongs to the current palette ID (e.g., "base_1", "highlight_1", etc.)
                    if key.endswith(f"_{palette_id}"):
                        # Extract the category name (e.g., "base", "highlight", etc.)
                        category = key.rsplit('_', 1)[0]
                        palettes[planet_type_lower][palette_id_str][category] = value

                # If we didn't find any categories for this palette ID, remove it
                if not palettes[planet_type_lower][palette_id_str]:
                    del palettes[planet_type_lower][palette_id_str]

            # If we didn't find any palettes, add a default one
            if not palettes[planet_type_lower]:
                palettes[planet_type_lower]["1"] = {
                    "base": [(128, 128, 128), (150, 150, 150), (170, 170, 170)]
                }

    # Debug output
    print(f"Color palettes: {palettes.keys()}")
    for planet_type, type_palettes in palettes.items():
        print(f"  {planet_type}: {len(type_palettes)} palettes")
        for palette_id, categories in type_palettes.items():
            print(f"    Palette {palette_id}: {len(categories)} categories")
            for category, colors in categories.items():
                print(f"      {category}: {len(colors)} colors")

    return palettes


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
        type_dir = os.path.join(base_dir, config.PLANETS_DIR, planet_type.lower())

        # Skip if directory doesn't exist
        if not os.path.exists(type_dir):
            continue

        # Find all seed directories
        seed_dirs = [d for d in os.listdir(type_dir) if os.path.isdir(os.path.join(type_dir, d))]

        for seed in seed_dirs:
            # Path to the planet image
            planet_path = os.path.join(type_dir, seed, "planet.png")

            # Skip if planet image doesn't exist
            if not os.path.exists(planet_path):
                continue

            # Basic info
            planet_info = {
                "type": planet_type,
                "seed": seed,
                "path": planet_path,
                "filename": "planet.png",
                "url": f"/static/planets/{planet_type.lower()}/{seed}/planet.png",
                "log_url": f"/static/planets/{planet_type.lower()}/{seed}/planet.log",
                "params": {}
            }

            # Add texture URLs if the files exist
            terrain_texture_path = os.path.join(type_dir, seed, "terrain_texture.png")
            if os.path.exists(terrain_texture_path):
                planet_info["terrain_texture_url"] = f"/static/planets/{planet_type.lower()}/{seed}/terrain_texture.png"

            cloud_texture_path = os.path.join(type_dir, seed, "cloud_texture.png")
            if os.path.exists(cloud_texture_path):
                planet_info["cloud_texture_url"] = f"/static/planets/{planet_type.lower()}/{seed}/cloud_texture.png"

            cloud_mask_path = os.path.join(type_dir, seed, "cloud_mask.png")
            if os.path.exists(cloud_mask_path):
                planet_info["cloud_mask_url"] = f"/static/planets/{planet_type.lower()}/{seed}/cloud_mask.png"

            # Get details from planets.csv
            details = get_planet_details(seed)
            if details:
                # Add parameters from details
                if 'variation' in details:
                    planet_info["params"]["variation"] = details['variation']

                if 'atmosphere' in details and details['atmosphere']:
                    planet_info["params"]["atmosphere"] = True

                if 'clouds' in details and details['clouds']:
                    planet_info["params"]["clouds"] = True

                if 'rings' in details and details['rings']:
                    planet_info["params"]["rings"] = True

            # If no parameters were found, use defaults
            if not planet_info["params"]:
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
            'atmosphere_thickness', 'atmosphere_blur', 'clouds', 'cloud_coverage', 'variation', 'color_palette_id',
            'light_intensity', 'light_angle', 'rotation', 'zoom', 'rings_complexity', 'rings_tilt'
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

            # Special case for cloud_coverage -> clouds-coverage
            if cli_key == 'cloud-coverage':
                cli_key = 'clouds-coverage'

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

        # Get variation (use default if not specified or empty)
        variation = params.get('variation', '')
        if not variation.strip():
            variation = config.DEFAULT_PLANET_VARIATIONS.get(planet_type.lower(), 'standard')

        # We don't need to create a filename anymore, as the new structure uses a fixed filename (planet.png)
        # in a directory named after the seed

        # We don't need to specify the output path, as the new structure will handle it automatically
        # The CLI will create the appropriate directory structure and save the files in the right places

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

                # Check for specific error messages in the output
                if "Planet already exists" in line:
                    generation_processes[process_id]["error"] = line.strip()

            # Wait for process to complete
            return_code = process.wait()
            generation_processes[process_id]["logs"].append(f"Process completed with return code: {return_code}")
        except Exception as e:
            generation_processes[process_id]["logs"].append(f"Error executing command: {str(e)}")
            return_code = 1  # Set error code

        # Update status based on return code
        if return_code == 0:
            generation_processes[process_id]["status"] = "completed"
            # Create the result with the image URL
            image_url = f"/static/planets/{planet_type.lower()}/{seed_str}/planet.png"
            generation_processes[process_id]["result"] = {
                "path": f"output/planets/{planet_type.lower()}/{seed_str}/planet.png",
                "url": image_url
            }
            # Add the image URL directly to the process info for easier access
            generation_processes[process_id]["image_url"] = image_url
        else:
            generation_processes[process_id]["status"] = "failed"
            # Use the specific error message if available, otherwise use a generic one
            if not generation_processes[process_id].get("error"):
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


def get_recent_logs(lines: int = 100, log_type: str = 'planets', planet_type: str = None, seed: str = None) -> List[str]:
    """
    Get recent log entries.

    Args:
        lines: Number of lines to retrieve
        log_type: Type of log to retrieve ('planets', 'webserver', or 'planet')
        planet_type: Type of planet (only used when log_type is 'planet')
        seed: Seed of the planet (only used when log_type is 'planet')

    Returns:
        List of log lines
    """
    if log_type == 'webserver':
        # Get web server logs
        log_file = config.WEB_CONFIG['log_file']
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    # Read the last 'lines' lines
                    return list(f.readlines())[-lines:]
            except Exception as e:
                return [f"Error reading web logs: {str(e)}"]
        return ["No web logs found"]
    elif log_type == 'planet' and planet_type and seed:
        # Get individual planet log
        planet_log_file = config.get_planet_log_path(planet_type, seed)
        if os.path.exists(planet_log_file):
            try:
                with open(planet_log_file, 'r') as f:
                    # Read the last 'lines' lines
                    return list(f.readlines())[-lines:]
            except Exception as e:
                return [f"Error reading planet log: {str(e)}"]
        return [f"No log file found for {planet_type} planet with seed {seed}"]
    else:
        # Get main planet generation logs
        planets_log_file = config.PLANETS_LOG_FILE
        if os.path.exists(planets_log_file):
            try:
                with open(planets_log_file, 'r') as f:
                    # Read the last 'lines' lines
                    return list(f.readlines())[-lines:]
            except Exception as e:
                return [f"Error reading planet logs: {str(e)}"]
        return ["No planet logs found"]


# Function get_planet_preview was removed as it was not being used


def clean_planets() -> str:
    """
    Clean all generated planets using the CLI command.

    Returns:
        Output message from the cleaning process
    """
    try:
        # Build command to clean all planets
        cmd = ["python", "-m", "cosmos_generator", "planet", "clean", "--all"]

        # Run the command
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            check=True
        )

        # Return the output
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        # If the command fails, raise an exception with the error message
        raise Exception(f"Failed to clean planets: {e.stdout}")
    except Exception as e:
        # For any other exception, re-raise it
        raise Exception(f"Error cleaning planets: {str(e)}")


def delete_planet_by_seed(seed: str) -> str:
    """
    Delete a specific planet by seed using the CLI command.

    Args:
        seed: The seed of the planet to delete

    Returns:
        Output message from the deletion process
    """
    try:
        # Build command to delete the planet
        cmd = ["python", "-m", "cosmos_generator", "planet", "clean", "--seeds", seed]

        # Run the command
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            check=True
        )

        # Return the output
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        # If the command fails, raise an exception with the error message
        raise Exception(f"Failed to delete planet with seed {seed}: {e.stdout}")
    except Exception as e:
        # For any other exception, re-raise it
        raise Exception(f"Error deleting planet with seed {seed}: {str(e)}")


def get_planet_log(planet_type: str, seed: str) -> str:
    """
    Get the log for a specific planet.

    Args:
        planet_type: The type of the planet
        seed: The seed of the planet

    Returns:
        The log content as a string
    """
    try:
        # Try different possible log file names and locations
        possible_log_paths = [
            # Current structure with planet.log
            os.path.join(config.OUTPUT_DIR, 'planets', planet_type.lower(), seed, 'planet.log'),
            # Current structure with generation.log
            os.path.join(config.OUTPUT_DIR, 'planets', planet_type.lower(), seed, 'generation.log'),
            # Old debug structure with generation.log
            os.path.join(config.OUTPUT_DIR, 'planets', 'debug', planet_type.lower(), seed, 'generation.log'),
            # Old debug structure with planet.log
            os.path.join(config.OUTPUT_DIR, 'planets', 'debug', planet_type.lower(), seed, 'planet.log')
        ]

        # Try each possible log path
        for log_path in possible_log_paths:
            if os.path.exists(log_path):
                # Read the log file
                with open(log_path, 'r') as f:
                    log_content = f.read()
                return log_content

        # If no log file is found
        return f"No log file found for {planet_type} planet with seed {seed}. Checked paths: {', '.join(possible_log_paths)}"
    except Exception as e:
        # If there's an error, return an error message
        return f"Error reading log file: {str(e)}"
