# Cosmos Generator

A Python library for procedurally generating detailed images of celestial bodies using PIL/Pillow. The core generator creates various planet types with unique characteristics, incorporating lighting simulation and atmospheric effects.

## Features

- Generate various planet types (Desert, Ocean, Jungle, Ice, Rocky, Toxic, Jovian) with unique visual characteristics
- Multiple variations and color palettes for each planet type
- Fixed resolution of 512x512 pixels for consistent display
- Container class for displaying planets with proper proportions and zoom control
- PNG output format with transparency
- Random seed or specified seed for reproducibility
- Lighting/shading model with directional light source
- Web interface for generating and exploring planets
- Optional planetary features (rings, atmosphere, clouds)
- Consistent planet generation based on seeds
- Standardized output directory structure
- Comprehensive logging system
- RESTful API for integration with other applications

## Documentation

The documentation for Cosmos Generator is organized into several sections:

- [Planet Generation Documentation](docs/planets.md) - Detailed information about:
  - Planet types and variations
  - Command-line interface usage
  - Python API examples
  - Output folder structure
  - Logging system

- [Web Interface Documentation](web/README.md) - Information about:
  - Web interface features and usage
  - Interface sections
  - Technical details

- [Web API Documentation](docs/api.md) - Complete reference for:
  - RESTful API endpoints
  - Parameters and examples
  - JavaScript and curl usage examples

## Quick Start

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cosmos-generator.git
   cd cosmos-generator
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

```bash
# Generate a planet via CLI
python -m cosmos_generator planet generate --type desert --seed 987 --rings --atmosphere

# List available planet types
python -m cosmos_generator planet --list-types

# Show variations for a specific planet type
python -m cosmos_generator planet --variations desert

# Launch web interface
python -m cosmos_generator web
```

For detailed Python API examples, see the [Planet Generation Documentation](docs/planets.md).

## Testing

```bash
# Run all tests
pytest tests/

# Run tests for a specific module
pytest tests/test_planet_generator.py

# Run tests with coverage report
pytest tests/ --cov=cosmos_generator
```

### Test Structure

The test suite is organized to test different components of the system:

- `tests/test_planet_generator.py`: Tests for the core planet generation functionality
- `tests/test_cli.py`: Tests for the command-line interface
- `tests/test_web_api.py`: Tests for the web API endpoints
- `tests/test_features/`: Tests for planet features (rings, atmosphere, clouds)

## Project Structure

```
cosmos_generator/             # Main package
├── celestial_bodies/         # Planet and feature implementations
│   ├── planets/              # Planet type implementations
│   │   ├── abstract_planet.py # Base planet class
│   │   ├── desert_planet.py  # Desert planet implementation
│   │   ├── ocean_planet.py   # Ocean planet implementation
│   │   └── ...               # Other planet types
│   ├── atmosphere.py         # Atmosphere implementation
│   ├── clouds.py             # Clouds implementation
│   ├── color_palettes.py     # Color palette definitions
│   └── rings.py              # Rings implementation
├── core/                     # Core functionality and interfaces
│   ├── interfaces.py         # Abstract interfaces
│   ├── celestial_body.py     # Base celestial body class
│   ├── noise_generator.py    # Noise generation utilities
│   ├── planet_generator.py   # Planet factory and registry
│   └── texture_generator.py  # Texture generation utilities
├── utils/                    # Utility functions and helpers
│   ├── csv_utils.py          # CSV file handling
│   ├── directory_utils.py    # Directory management
│   ├── exceptions.py         # Custom exceptions
│   ├── image_utils.py        # Image processing utilities
│   ├── logger.py             # Logging system
│   └── validation.py         # Parameter validation
└── cli.py                    # Command-line interface
config.py                     # Configuration
docs/                         # Documentation
├── api.md                    # Web API documentation
└── planets.md                # Planet generation documentation
web/                          # Web interface
├── static/                   # Static assets (CSS, JS)
├── templates/                # HTML templates
├── app.py                    # Flask application
├── api.py                    # API endpoints
└── README.md                 # Web interface documentation
tests/                        # Test suite
```

## Requirements

- Python 3.8+
- Pillow (PIL fork) for image manipulation
- NumPy for mathematical operations
- PyFastNoiseLite for high-performance noise generation
- Flask (for the web interface)
- Click for command-line interface
- Pytest for testing

## Configuration

The system configuration is managed in `config.py`. Key settings include:

- Output directory structure
- Debug and logging options
- Web server configuration
- Default generation parameters

## Adding New Planet Types

To add a new planet type:

1. Create a new class in `cosmos_generator/celestial_bodies/planets/` that inherits from `AbstractPlanet`
2. Implement the required methods, especially `generate_texture()`
3. Add color palettes for your planet type in `cosmos_generator/celestial_bodies/color_palettes.py`
4. Register your planet type in `cosmos_generator/core/planet_generator.py`

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
