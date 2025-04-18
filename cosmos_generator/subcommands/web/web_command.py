"""
Web interface subcommand for Cosmos Generator.
"""
import argparse
import os
import sys
import importlib.util

import config
from cosmos_generator.utils.logger import logger


def setup_parser(subparsers):
    """
    Set up the command line parser for the web subcommand.
    
    Args:
        subparsers: Subparsers object from the main parser
    """
    web_parser = subparsers.add_parser(
        'web',
        help='Launch the web interface'
    )
    
    web_parser.add_argument(
        '--host',
        type=str,
        default=config.WEB_CONFIG['host'],
        help=f'Host to bind to (default: {config.WEB_CONFIG["host"]})'
    )
    
    web_parser.add_argument(
        '--port',
        type=int,
        default=config.WEB_CONFIG['port'],
        help=f'Port to bind to (default: {config.WEB_CONFIG["port"]})'
    )
    
    web_parser.add_argument(
        '--debug',
        action='store_true',
        default=config.WEB_CONFIG['debug'],
        help='Enable debug mode (default: False)'
    )
    
    web_parser.set_defaults(func=run_web_interface)


def run_web_interface(args):
    """
    Run the web interface.
    
    Args:
        args: Command line arguments
    """
    try:
        # Check if Flask is installed
        if importlib.util.find_spec('flask') is None:
            logger.error("Flask is not installed. Please install it with 'pip install flask'.", "web")
            return 1
        
        # Add the project root to the path so we can import the web module
        sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))
        
        # Import the web app
        from web import create_app
        
        # Create the app
        app = create_app()
        
        # Log startup information
        logger.info(f"Starting web interface on http://{args.host}:{args.port}", "web")
        logger.info(f"Debug mode: {'enabled' if args.debug else 'disabled'}", "web")
        
        # Run the app
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to start web interface: {str(e)}", "web", exc_info=True)
        return 1
