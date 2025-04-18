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

    if not params:
        return jsonify({'error': 'No parameters provided'}), 400

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
    status_info = get_generation_status(process_id)

    if not status_info:
        return jsonify({'error': 'Process not found'}), 404

    return jsonify(status_info)


@api_bp.route('/logs', methods=['GET'])
def logs():
    """
    Get recent logs.
    """
    # Get number of lines to retrieve
    lines = request.args.get('lines', 100, type=int)
    log_type = request.args.get('type', 'planets')

    # Get recent logs
    recent_logs = get_recent_logs(lines, log_type)

    return jsonify({
        'logs': recent_logs,
        'count': len(recent_logs),
        'type': log_type
    })
