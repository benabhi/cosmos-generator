"""
Main routes for the web interface.
"""
import os
import subprocess
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify

import config
from web.utils import (
    get_planet_types,
    get_planet_variations,
    get_default_variations,
    get_generated_planets,
    filter_planets,
    get_recent_logs
)

# Create blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Render the home page.
    """
    return render_template(
        'index.html',
        planet_types=get_planet_types(),
        planet_variations=get_planet_variations(),
        default_variations=get_default_variations()
    )


@main_bp.route('/planets')
def planets():
    """
    Render the planets gallery page.
    """
    # Get filter parameters
    filters = {
        'type': request.args.get('type', ''),
        'seed': request.args.get('seed', ''),
        'has_rings': request.args.get('has_rings') == 'true',
        'has_atmosphere': request.args.get('has_atmosphere') == 'true',
        'has_clouds': request.args.get('has_clouds') == 'true'
    }

    # Get all planets and apply filters
    all_planets = get_generated_planets()
    filtered_planets = filter_planets(all_planets, filters)

    return render_template(
        'planets.html',
        planets=filtered_planets,
        filters=filters,
        planet_types=get_planet_types(),
        count=len(filtered_planets),
        total=len(all_planets)
    )


@main_bp.route('/logs')
def logs():
    """
    Render the logs page.
    """
    # Get number of lines to display
    lines = request.args.get('lines', 100, type=int)
    log_type = request.args.get('type', 'planets')

    # Get recent logs
    recent_logs = get_recent_logs(lines, log_type)

    return render_template(
        'logs.html',
        logs=recent_logs,
        lines=lines,
        log_type=log_type
    )


@main_bp.route('/static/planets/<planet_type>/<filename>')
def planet_image(planet_type, filename):
    """
    Serve planet images.

    Args:
        planet_type: Type of planet
        filename: Image filename
    """
    # Get the absolute path to the directory
    directory = os.path.abspath(os.path.join(config.PLANETS_RESULT_DIR, planet_type.lower()))
    print(f"Serving image from {directory}/{filename}")
    return send_from_directory(directory, filename)


@main_bp.route('/static/planets/debug/textures/terrain/<filename>')
def terrain_texture(filename):
    """
    Serve terrain texture images.

    Args:
        filename: Image filename
    """
    # Get the absolute path to the directory
    directory = os.path.abspath(os.path.join(config.PLANETS_DEBUG_DIR, 'textures/terrain'))
    print(f"Serving terrain texture from {directory}/{filename}")
    return send_from_directory(directory, filename)


@main_bp.route('/static/planets/debug/textures/clouds/<seed>/<filename>')
def cloud_texture(seed, filename):
    """
    Serve cloud texture images.

    Args:
        seed: Planet seed
        filename: Image filename (texture.png or mask.png)
    """
    # Get the absolute path to the directory
    directory = os.path.abspath(os.path.join(config.PLANETS_DEBUG_DIR, f'textures/clouds/{seed}'))
    print(f"Serving cloud texture from {directory}/{filename}")
    return send_from_directory(directory, filename)


@main_bp.route('/api/logs')
def api_logs():
    """
    Get logs as JSON.
    """
    # Get number of lines to display
    lines = request.args.get('lines', 100, type=int)
    log_type = request.args.get('type', 'planets')

    # Get recent logs
    recent_logs = get_recent_logs(lines, log_type)

    return jsonify({
        'logs': recent_logs,
        'lines': lines,
        'log_type': log_type
    })


@main_bp.route('/api/clean', methods=['POST'])
def clean():
    """
    Clean all generated files.
    """
    try:
        # Run the clean command
        result = subprocess.run(
            ['python', '-m', 'cosmos_generator', 'planet', 'clean', '--all'],
            capture_output=True,
            text=True,
            check=True
        )

        # Return success response
        return jsonify({
            'success': True,
            'message': 'All files cleaned successfully',
            'output': result.stdout
        })
    except subprocess.CalledProcessError as e:
        # Return error response
        return jsonify({
            'success': False,
            'message': 'Failed to clean files',
            'error': e.stderr
        }), 500
