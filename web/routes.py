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
    get_color_palettes,
    get_generated_planets,
    filter_planets,
    get_recent_logs
)

# Create blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def dashboard():
    """
    Render the dashboard page.
    """
    # Get all planets for statistics
    all_planets = get_generated_planets()

    # Get recent planets (limit to 5)
    recent_planets = all_planets[:5] if all_planets else []

    return render_template(
        'dashboard.html',
        planet_count=len(all_planets),
        planet_types=get_planet_types(),
        recent_planets=recent_planets
    )


@main_bp.route('/generate')
def index():
    """
    Render the planet generator page.
    """
    return render_template(
        'index.html',
        planet_types=get_planet_types(),
        planet_variations=get_planet_variations(),
        default_variations=get_default_variations(),
        color_palettes=get_color_palettes(),
        default_type="desert"
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

    # Reverse logs to show newest first (consistent with the API endpoint)
    recent_logs.reverse()

    return render_template(
        'logs.html',
        logs=recent_logs,
        lines=lines,
        log_type=log_type
    )


@main_bp.route('/static/planets/<planet_type>/<seed>/<filename>')
def planet_image(planet_type, seed, filename):
    """
    Serve planet images and related files.

    Args:
        planet_type: Type of planet
        seed: Seed used for generation
        filename: Image filename
    """
    # Get the absolute path to the directory
    directory = os.path.abspath(os.path.join(config.PLANETS_DIR, planet_type.lower(), seed))
    print(f"Serving file from {directory}/{filename}")
    return send_from_directory(directory, filename)


@main_bp.route('/static/planets/debug/textures/terrain/<seed>.png')
def terrain_texture_legacy(seed):
    """
    Serve terrain textures from the new location for backward compatibility.
    """
    # Find the planet type directory that contains this seed
    for planet_type in config.PLANET_TYPES:
        # Try with zero-padded seed
        padded_seed = seed.zfill(8)
        directory = os.path.abspath(os.path.join(config.PLANETS_DIR, planet_type.lower(), padded_seed))
        texture_path = os.path.join(directory, "terrain_texture.png")
        if os.path.exists(texture_path):
            return send_from_directory(directory, "terrain_texture.png")

        # Try with original seed format
        directory = os.path.abspath(os.path.join(config.PLANETS_DIR, planet_type.lower(), seed))
        texture_path = os.path.join(directory, "terrain_texture.png")
        if os.path.exists(texture_path):
            return send_from_directory(directory, "terrain_texture.png")

    # If not found, return 404
    return "Texture not found", 404


@main_bp.route('/static/planets/debug/textures/clouds/<seed>/texture.png')
def cloud_texture_legacy(seed):
    """
    Serve cloud textures from the new location for backward compatibility.
    """
    # Find the planet type directory that contains this seed
    for planet_type in config.PLANET_TYPES:
        # Try with zero-padded seed
        padded_seed = seed.zfill(8)
        directory = os.path.abspath(os.path.join(config.PLANETS_DIR, planet_type.lower(), padded_seed))
        texture_path = os.path.join(directory, "cloud_texture.png")
        if os.path.exists(texture_path):
            return send_from_directory(directory, "cloud_texture.png")

        # Try with original seed format
        directory = os.path.abspath(os.path.join(config.PLANETS_DIR, planet_type.lower(), seed))
        texture_path = os.path.join(directory, "cloud_texture.png")
        if os.path.exists(texture_path):
            return send_from_directory(directory, "cloud_texture.png")

    # If not found, return 404
    return "Texture not found", 404


@main_bp.route('/static/planets/debug/textures/clouds/<seed>/mask.png')
def cloud_mask_legacy(seed):
    """
    Serve cloud masks from the new location for backward compatibility.
    """
    # Find the planet type directory that contains this seed
    for planet_type in config.PLANET_TYPES:
        # Try with zero-padded seed
        padded_seed = seed.zfill(8)
        directory = os.path.abspath(os.path.join(config.PLANETS_DIR, planet_type.lower(), padded_seed))
        texture_path = os.path.join(directory, "cloud_mask.png")
        if os.path.exists(texture_path):
            return send_from_directory(directory, "cloud_mask.png")

        # Try with original seed format
        directory = os.path.abspath(os.path.join(config.PLANETS_DIR, planet_type.lower(), seed))
        texture_path = os.path.join(directory, "cloud_mask.png")
        if os.path.exists(texture_path):
            return send_from_directory(directory, "cloud_mask.png")

    # If not found, return 404
    return "Texture not found", 404



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

    # Reverse logs to show newest first
    recent_logs.reverse()

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
        # Note: The clean command has been removed in the current version
        # Instead, we'll manually remove the planet directories
        import shutil

        # Get the absolute path to the planets directory
        planets_dir = os.path.abspath(config.PLANETS_DIR)

        # Remove all planet type directories
        for planet_type in config.PLANET_TYPES:
            type_dir = os.path.join(planets_dir, planet_type.lower())
            if os.path.exists(type_dir):
                shutil.rmtree(type_dir)

        # Reset the planets.csv file
        planets_csv = os.path.join(planets_dir, "planets.csv")
        with open(planets_csv, 'w') as f:
            f.write("seed,planet_type,variation,atmosphere,rings,clouds\n")

        # Preserve the main log file but clear its contents
        log_file = os.path.join(planets_dir, "planets.log")
        with open(log_file, 'w') as f:
            f.write("# Cosmos Generator Planet Log\n# All previous logs have been cleared\n")

        # Return success response
        return jsonify({
            'success': True,
            'message': 'All files cleaned successfully',
            'output': f"Removed all planet directories from {planets_dir}"
        })
    except Exception as e:
        # Return error response
        return jsonify({
            'success': False,
            'message': 'Failed to clean files',
            'error': str(e)
        }), 500
