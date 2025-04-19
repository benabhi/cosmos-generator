"""
API endpoints for the web interface.
"""
from flask import Blueprint, request, jsonify

from web.utils import (
    get_planet_types,
    get_planet_variations,
    get_default_variations,
    get_generated_planets,
    filter_planets,
    generate_planet_async,
    get_generation_status,
    get_recent_logs
)

# Create blueprint
api_bp = Blueprint('api', __name__)


@api_bp.route('/planet-types', methods=['GET'])
def planet_types():
    """
    Get available planet types.
    """
    return jsonify({
        'types': get_planet_types(),
        'variations': get_planet_variations(),
        'defaults': get_default_variations()
    })


@api_bp.route('/planets', methods=['GET'])
def planets():
    """
    Get generated planets with optional filtering.
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
    Generate a new planet.
    """
    # Get parameters from request
    params = request.json

    # Validate parameters
    if not params:
        return jsonify({'error': 'No parameters provided'}), 400

    # Validate planet type
    if 'type' in params and params['type']:
        planet_type = params['type'].lower()
        valid_types = [t.lower() for t in get_planet_types()]
        if planet_type not in valid_types:
            return jsonify({
                'error': f"Invalid planet type: '{planet_type}'. Valid types are: {', '.join(valid_types)}"
            }), 400

    # Validate numeric parameters
    numeric_params = [
        ('atmosphere_glow', 0.0, 1.0),
        ('atmosphere_halo', 0.0, 1.0),
        ('atmosphere_thickness', 1, 10),
        ('atmosphere_blur', 0.0, 1.0),
        ('clouds', 0.0, 1.0),
        ('light_intensity', 0.1, 2.0),
        ('light_angle', 0, 360),
        ('rotation', 0, 360),
        ('zoom', 0.0, 1.0)
    ]

    for param_name, min_val, max_val in numeric_params:
        if param_name in params and params[param_name] is not None:
            try:
                # Convert to float for validation
                value = float(params[param_name])
                if value < min_val or value > max_val:
                    return jsonify({
                        'error': f"Parameter '{param_name}' must be between {min_val} and {max_val}. Got: {value}"
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'error': f"Parameter '{param_name}' must be a number. Got: {params[param_name]}"
                }), 400

    # Validate variation
    if 'variation' in params and params['variation']:
        if 'type' in params and params['type']:
            planet_type = params['type'].lower()
            variations = get_planet_variations().get(planet_type, [])
            if params['variation'] not in variations:
                return jsonify({
                    'error': f"Invalid variation '{params['variation']}' for planet type '{planet_type}'. "
                            f"Valid variations are: {', '.join(variations)}"
                }), 400

    # Start generation process
    process_id = generate_planet_async(params)

    return jsonify({
        'process_id': process_id,
        'status': 'started',
        'message': 'Planet generation started'
    })


@api_bp.route('/status/<process_id>', methods=['GET'])
def status(process_id):
    """
    Get status of a generation process.

    Args:
        process_id: Process ID
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
    Get recent logs.
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
    valid_types = ['planets', 'webserver']
    if log_type not in valid_types:
        return jsonify({
            'error': f"Invalid log type: '{log_type}'. Valid types are: {', '.join(valid_types)}"
        }), 400

    # Get recent logs
    recent_logs = get_recent_logs(lines, log_type)

    return jsonify({
        'logs': recent_logs,
        'count': len(recent_logs),
        'type': log_type
    })
