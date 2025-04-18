"""
Flask application for the Cosmos Generator web interface.
"""
from web import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
