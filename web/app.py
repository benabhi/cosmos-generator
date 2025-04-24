"""
Flask application for the Cosmos Generator web interface.
"""
from web import create_app

app = create_app()

if __name__ == '__main__':
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the Cosmos Generator web interface')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()

    # Run the app
    app.run(host=args.host, port=args.port, debug=args.debug)
