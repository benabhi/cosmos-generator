"""
Web interface module for Cosmos Generator.

This module provides a web interface for generating and exploring procedural
celestial bodies created with the Cosmos Generator.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request

import config
from cosmos_generator.utils.directory_utils import ensure_directory_exists


def create_app(testing=False):
    """
    Create and configure the Flask application.

    Args:
        testing (bool): Whether to configure the app for testing

    Returns:
        Flask application instance
    """
    # Create Flask app
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')

    # Load configuration
    app.config['SECRET_KEY'] = config.WEB_CONFIG['secret_key']
    app.config['MAX_CONTENT_LENGTH'] = config.WEB_CONFIG['max_content_length']

    # Configure for testing if needed
    if testing:
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    # Configure logging
    ensure_directory_exists(config.WEB_CONFIG['log_dir'])

    # Set up logging only if not in testing mode
    if not testing:
        # Set up logging - always log to file regardless of debug mode
        web_log_file = config.WEB_CONFIG['log_file']
        ensure_directory_exists(os.path.dirname(web_log_file))
        file_handler = RotatingFileHandler(
            web_log_file,
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Cosmos Generator Web Interface startup')
    else:
        # In testing mode, set up minimal logging
        app.logger.setLevel(logging.ERROR)

    # Log all requests (only in non-testing mode)
    if not testing:
        @app.after_request
        def after_request(response):
            app.logger.info(
                '%s %s %s %s %s',
                request.remote_addr,
                request.method,
                request.full_path,
                response.status,
                response.content_length
            )
            return response

    # Register blueprints
    from web.routes import main_bp
    app.register_blueprint(main_bp)

    from web.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
