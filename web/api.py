"""
API endpoints for the web interface.
"""
from flask import Blueprint, request, jsonify, current_app

from web.utils import (
    get_planet_types,
    get_planet_variations,
    get_default_variations,
    get_color_palettes,
    get_generated_planets,
    filter_planets,
    generate_planet_async,
    get_generation_status,
    get_recent_logs,
    clean_planets
)
from cosmos_generator.utils.csv_utils import is_seed_used

# Create blueprint
api_bp = Blueprint('api', __name__)


@api_bp.route('/planet-types', methods=['GET'])
def planet_types():
    """
    Get available planet types, variations, default variations, and color palettes.

    Returns:
        JSON object with the following keys:
        - types: List of available planet types
        - variations: Dictionary mapping planet types to their available variations
        - defaults: Dictionary mapping planet types to their default variations
        - color_palettes: Dictionary mapping planet types to their available color palettes
    """
    return jsonify({
        'types': get_planet_types(),
        'variations': get_planet_variations(),
        'defaults': get_default_variations(),
        'color_palettes': get_color_palettes()
    })


@api_bp.route('/planets', methods=['GET'])
def planets():
    """
    Get generated planets with optional filtering.

    Query Parameters:
        type (str, optional): Filter by planet type (e.g., 'desert', 'ocean')
        seed (str, optional): Filter by seed (partial match)
        has_rings (bool, optional): Filter by presence of rings ('true' or 'false')
        has_atmosphere (bool, optional): Filter by presence of atmosphere ('true' or 'false')
        has_clouds (bool, optional): Filter by presence of clouds ('true' or 'false')

    Returns:
        JSON object with the following keys:
        - planets: List of planet objects matching the filters
        - count: Number of planets matching the filters
        - total: Total number of planets before filtering
    """
    # Get filter parameters
    filters = {
        'type': request.args.get('type', ''),
        'has_rings': request.args.get('has_rings') == 'true',
        'has_atmosphere': request.args.get('has_atmosphere') == 'true',
        'has_clouds': request.args.get('has_clouds') == 'true',
        'seed': request.args.get('seed', '')
    }

    # Get all planets and apply filters
    all_planets = get_generated_planets()
    filtered_planets = filter_planets(all_planets, filters)

    return jsonify({
        'planets': filtered_planets,
        'count': len(filtered_planets),
        'total': len(all_planets)
    })


@api_bp.route('/generate', methods=['POST'])
def generate():
    """
    Generate a new planet asynchronously.

    Request Body (JSON):
        type (str): Planet type (e.g., 'desert', 'ocean')
        seed (str, optional): Seed for the planet. If not provided, a random seed will be generated.
        variation (str, optional): Variation of the planet. If not provided, the default variation for the planet type will be used.
        rings (bool, optional): Whether the planet has rings.
        atmosphere (bool, optional): Whether the planet has an atmosphere.
        clouds (float, optional): Cloud coverage (0.0 to 1.0).
        atmosphere_density (float, optional): Atmosphere density (0.0 to 1.0).
        atmosphere_scattering (float, optional): Atmosphere light scattering intensity (0.0 to 1.0).
        atmosphere_color_shift (float, optional): Atmosphere color shift amount (0.0 to 1.0).
        light_intensity (float, optional): Light intensity (0.1 to 2.0).
        light_angle (int, optional): Light angle in degrees (0 to 360).
        rotation (int, optional): Planet rotation in degrees (0 to 360).
        zoom (float, optional): Zoom level (0.0 to 1.0).

    Returns:
        JSON object with the following keys:
        - process_id: ID of the generation process
        - status: Status of the process ('started')
        - message: Message describing the status

    Errors:
        400 Bad Request: If the parameters are invalid
    """
    # Import validation utilities
    from cosmos_generator.utils.validation import validate_planet_params, sanitize_planet_params
    from cosmos_generator.utils.exceptions import ValidationError

    # Get parameters from request
    params = request.json

    # Validate parameters
    if not params:
        return jsonify({'error': 'No parameters provided'}), 400

    # Validate planet type against available types
    if 'type' in params and params['type']:
        planet_type = params['type'].lower()
        valid_types = [t.lower() for t in get_planet_types()]
        if planet_type not in valid_types:
            return jsonify({
                'error': f"Invalid planet type: '{planet_type}'. Valid types are: {', '.join(valid_types)}"
            }), 400

    # Validate variation against available variations for the planet type
    if 'variation' in params and params['variation'] and 'type' in params and params['type']:
        planet_type = params['type'].lower()
        variations = get_planet_variations().get(planet_type, [])
        if params['variation'] not in variations:
            return jsonify({
                'error': f"Invalid variation '{params['variation']}' for planet type '{planet_type}'. "
                        f"Valid variations are: {', '.join(variations)}"
            }), 400

    # Validate all other parameters
    is_valid, errors = validate_planet_params(params)
    if not is_valid:
        # Format errors for API response
        error_messages = []
        for error in errors:
            for param, message in error.items():
                # Make error messages more user-friendly
                if param == 'seed':
                    error_messages.append(f"Invalid seed: {message}")
                elif param == 'type':
                    error_messages.append(f"Invalid planet type: {message}")
                elif param == 'variation':
                    error_messages.append(f"Invalid variation: {message}")
                elif param == 'clouds':
                    error_messages.append(f"Invalid cloud parameter: {message}")
                elif param == 'cloud_coverage':
                    error_messages.append(f"Invalid cloud coverage: {message} (must be between 0.0 and 1.0)")
                elif param == 'rings_complexity':
                    error_messages.append(f"Invalid rings complexity: {message} (must be between 1 and 5)")
                elif param == 'rings_tilt':
                    error_messages.append(f"Invalid rings tilt: {message} (must be between -45 and 45)")
                else:
                    error_messages.append(f"{param}: {message}")

        # Check if the seed already exists
        if 'seed' in params and is_seed_used(params['seed']):
            error_messages.append(f"A planet with seed '{params['seed']}' already exists. Please use a different seed.")

        return jsonify({
            'error': 'Invalid parameters',
            'details': error_messages
        }), 400

    # Sanitize parameters (convert strings to appropriate types)
    sanitized_params = sanitize_planet_params(params)

    try:
        # Start generation process
        process_id = generate_planet_async(sanitized_params)

        return jsonify({
            'process_id': process_id,
            'status': 'started',
            'message': 'Planet generation started'
        })
    except Exception as e:
        # Log the error
        current_app.logger.error(f"Error starting planet generation: {str(e)}", exc_info=True)

        # Return error response
        return jsonify({
            'error': 'Failed to start planet generation',
            'message': str(e)
        }), 500


@api_bp.route('/status/<process_id>', methods=['GET'])
def status(process_id):
    """
    Get status of a planet generation process.

    Args:
        process_id (str): ID of the generation process

    Returns:
        JSON object with the following keys:
        - status: Status of the process ('starting', 'running', 'completed', or 'failed')
        - logs: List of log messages from the generation process
        - result: (if completed) Object with information about the generated planet
        - error: (if failed) Error message

    Errors:
        400 Bad Request: If the process ID is not provided
        404 Not Found: If the process ID is not found
    """
    # Validate process_id
    if not process_id:
        return jsonify({'error': 'Process ID is required'}), 400

    # Get status information
    status_info = get_generation_status(process_id)

    if not status_info:
        return jsonify({
            'error': f"Process not found: '{process_id}'. The process may have expired or never existed."
        }), 404

    return jsonify(status_info)


@api_bp.route('/logs', methods=['GET'])
def logs():
    """
    Get recent logs from the system.

    Query Parameters:
        lines (int, optional): Number of lines to retrieve. Default is 100.
        type (str, optional): Type of logs to retrieve. Valid values are 'planets', 'webserver', and 'planet'. Default is 'planets'.
        planet_type (str, optional): Required if type is 'planet'. The type of the planet.
        seed (str, optional): Required if type is 'planet'. The seed of the planet.

    Returns:
        JSON object with the following keys:
        - logs: List of log lines
        - count: Number of log lines
        - type: Type of logs retrieved

    Errors:
        400 Bad Request: If the parameters are invalid
    """
    # Get number of lines to retrieve
    try:
        lines = request.args.get('lines', 100, type=int)
        if lines <= 0:
            return jsonify({
                'error': f"Parameter 'lines' must be a positive integer. Got: {lines}"
            }), 400
    except ValueError:
        return jsonify({
            'error': f"Parameter 'lines' must be a valid integer. Got: {request.args.get('lines')}"
        }), 400

    # Validate log type
    log_type = request.args.get('type', 'planets')
    valid_types = ['planets', 'webserver', 'planet']
    if log_type not in valid_types:
        return jsonify({
            'error': f"Invalid log type: '{log_type}'. Valid types are: {', '.join(valid_types)}"
        }), 400

    # For planet-specific logs, we need planet_type and seed
    if log_type == 'planet':
        planet_type = request.args.get('planet_type')
        seed = request.args.get('seed')

        if not planet_type or not seed:
            return jsonify({
                'error': "Parameters 'planet_type' and 'seed' are required for planet logs"
            }), 400

        # Get planet-specific logs
        recent_logs = get_recent_logs(lines, log_type, planet_type, seed)
    else:
        # Get general logs
        recent_logs = get_recent_logs(lines, log_type)

    return jsonify({
        'logs': recent_logs,
        'count': len(recent_logs),
        'type': log_type
    })


@api_bp.route('/check-seed/<seed>', methods=['GET'])
def check_seed(seed):
    """
    Check if a seed is already used for a planet.

    Args:
        seed (str): Seed to check

    Returns:
        JSON object with the following keys:
        - seed: The seed that was checked
        - used: Boolean indicating whether the seed is already used
    """
    return jsonify({
        'seed': seed,
        'used': is_seed_used(seed)
    })


@api_bp.route('/clean', methods=['POST'])
def clean():
    """
    Clean all generated planets.

    This endpoint deletes all generated planets and their associated files.

    Returns:
        JSON object with the following keys:
        - success: Boolean indicating whether the operation was successful
        - message: Message describing the result
        - output: Output from the cleaning process

    Errors:
        500 Internal Server Error: If there was an error during the cleaning process
    """
    try:
        # Call the clean_planets function
        output = clean_planets()

        return jsonify({
            'success': True,
            'message': 'All planets cleaned successfully',
            'output': output
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to clean planets',
            'error': str(e)
        }), 500


@api_bp.route('/delete-planet', methods=['POST'])
def delete_planet():
    """
    Delete a specific planet by seed.

    Request Body (JSON):
        seed (str): Seed of the planet to delete

    Returns:
        JSON object with the following keys:
        - success: Boolean indicating whether the operation was successful
        - message: Message describing the result
        - output: Output from the deletion process

    Errors:
        400 Bad Request: If the seed parameter is missing or invalid
        404 Not Found: If the planet with the specified seed does not exist
        500 Internal Server Error: If there was an error during the deletion process
    """
    # Get parameters from request
    params = request.json

    # Validate parameters
    if not params or 'seed' not in params:
        return jsonify({
            'success': False,
            'message': 'Seed parameter is required'
        }), 400

    seed = params['seed']

    # Validate seed format
    from cosmos_generator.utils.validation import validate_seed
    is_valid, error_message = validate_seed(seed, allow_none=False)
    if not is_valid:
        return jsonify({
            'success': False,
            'message': f'Invalid seed: {error_message}'
        }), 400

    try:
        # Check if the planet exists
        if not is_seed_used(seed):
            return jsonify({
                'success': False,
                'message': f'Planet with seed {seed} not found'
            }), 404

        # Delete the planet
        from web.utils import delete_planet_by_seed
        result = delete_planet_by_seed(seed)

        # Log the deletion
        current_app.logger.info(f"Planet with seed {seed} deleted successfully")

        return jsonify({
            'success': True,
            'message': f'Planet with seed {seed} deleted successfully',
            'output': result
        })
    except Exception as e:
        # Log the error
        current_app.logger.error(f"Error deleting planet with seed {seed}: {str(e)}", exc_info=True)

        return jsonify({
            'success': False,
            'message': f'Failed to delete planet with seed {seed}',
            'error': str(e)
        }), 500


@api_bp.route('/planet-log/<planet_type>/<seed>', methods=['GET'])
def planet_log(planet_type, seed):
    """
    Get the log for a specific planet.

    Args:
        planet_type (str): Type of the planet (e.g., 'desert', 'ocean')
        seed (str): Seed of the planet

    Returns:
        JSON object with the following keys:
        - success: Boolean indicating whether the operation was successful
        - log_content: Content of the planet's log file
        - planet_type: Type of the planet
        - seed: Seed of the planet

    Errors:
        400 Bad Request: If the planet type or seed is invalid
        404 Not Found: If the planet or its log file does not exist
        500 Internal Server Error: If there was an error retrieving the log
    """
    # Validate planet type
    valid_types = [t.lower() for t in get_planet_types()]
    if planet_type.lower() not in valid_types:
        return jsonify({
            'success': False,
            'message': f"Invalid planet type: '{planet_type}'. Valid types are: {', '.join(valid_types)}"
        }), 400

    # Validate seed format
    from cosmos_generator.utils.validation import validate_seed
    is_valid, error_message = validate_seed(seed, allow_none=False)
    if not is_valid:
        return jsonify({
            'success': False,
            'message': f'Invalid seed: {error_message}'
        }), 400

    try:
        # Check if the planet exists
        if not is_seed_used(seed):
            return jsonify({
                'success': False,
                'message': f'Planet with seed {seed} not found'
            }), 404

        # Get the log content
        from web.utils import get_planet_log
        try:
            log_content = get_planet_log(planet_type, seed)
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'message': f'Log file for planet {planet_type} with seed {seed} not found'
            }), 404

        # Log the access
        current_app.logger.info(f"Log for planet {planet_type} with seed {seed} accessed")

        return jsonify({
            'success': True,
            'log_content': log_content,
            'planet_type': planet_type,
            'seed': seed
        })
    except FileNotFoundError as e:
        # Specific handling for file not found
        return jsonify({
            'success': False,
            'message': f'Log file for planet {planet_type} with seed {seed} not found',
            'error': str(e)
        }), 404
    except Exception as e:
        # Log the error
        current_app.logger.error(f"Error retrieving log for planet {planet_type} with seed {seed}: {str(e)}", exc_info=True)

        return jsonify({
            'success': False,
            'message': f'Failed to get log for planet {planet_type} with seed {seed}',
            'error': str(e)
        }), 500
