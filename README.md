# Cosmos Generator

A Python library for procedurally generating detailed images of celestial bodies using PIL/Pillow. The core generator creates 12 different planet types with unique characteristics, incorporating lighting simulation and atmospheric effects.

## Features

- Generate 12 different planet types with unique visual characteristics
- Fixed resolution of 512x512 pixels for consistent display (not configurable by users)
- Container class for displaying planets with proper proportions and zoom control
- PNG output format with transparency
- Random seed or specified seed for reproducibility
- Lighting/shading model with directional light source
- Optional planetary features:
  - Rings: Elliptical ring systems with proper depth perception
  - Atmosphere: Simple atmospheric glow effect (boolean parameter)
  - Clouds: Layered cloud systems for applicable planet types with configurable coverage (0.0-1.0)
  - Surface details: Craters, mountains, etc.

## Installation

```bash
# Install the package
pip install cosmos-generator

# For development (including testing dependencies)
pip install -r requirements-dev.txt
```

## Usage

### Python API

```python
from cosmos_generator import PlanetGenerator
from cosmos_generator.utils import Container

# Create generator
generator = PlanetGenerator()

# Generate desert planet with rings, atmosphere and clouds
planet = generator.create("Desert", {
    "seed": 12345,
    "variation": "arid",  # Optional, uses default if not specified
    "rings": True,
    "lighting": {
        "intensity": 1.0,
        "angle": 45,
        "falloff": 0.7
    },
    "atmosphere": True,
    "clouds": True,
    "cloud_coverage": 1.0  # 0.0 to 1.0, where 1.0 is maximum coverage
})

# Generate ocean planet with archipelago variation
ocean_planet = generator.create("Ocean", {
    "seed": 54321,
    "variation": "archipelago",  # "water_world" is the default
    "atmosphere": True
})

# Basic save method
planet.save("desert_planet_12345.png")

# Use container for fixed size display, rotation and zoom control
container = Container(zoom_level=0.7)  # Optional zoom level (0.0=far/small, 1.0=close/large)
container.set_content(planet)
container.rotate(45)  # Optional rotation
container.export("desert_planet_container.png")

# Default zoom levels are:
# - 0.95 for planets without rings
# - 0.25 for planets with rings
```

### Command Line Interface

Cosmos Generator uses a subcommand structure to organize its functionalities:

```bash
# Show general help
python -m cosmos_generator --help

# Show version
python -m cosmos_generator --version

# Show specific help for the planet subcommand
python -m cosmos_generator planet --help

# Run tests
python -m cosmos_generator test
```

#### Planet Generation

```bash
# With custom output path
python -m cosmos_generator planet generate --type desert --seed 987 --output planet.png --rings --atmosphere --light-angle 30

# With default output path (output/planets/result/desert/987.png)
python -m cosmos_generator planet generate --type desert --seed 987 --rings --atmosphere --light-angle 30

# Generate planet with clouds (coverage of 0.7 or 70%)
python -m cosmos_generator planet generate --type ocean --clouds 0.7 --seed 12345

# Generate planet with specific variation
python -m cosmos_generator planet generate --type ocean --variation archipelago
python -m cosmos_generator planet generate --type desert --variation arid

# List available variations for each planet type
python -m cosmos_generator planet --list-variations

# List available planet types
python -m cosmos_generator planet --list-types

# Clean generated planet files
python -m cosmos_generator planet clean         # Clean all files
python -m cosmos_generator planet clean --debug    # Clean only debug files
python -m cosmos_generator planet clean --examples # Clean only example files
python -m cosmos_generator planet clean --results  # Clean only result files
python -m cosmos_generator planet clean --dry-run  # Show what would be deleted without deleting anything

# View planet generation logs
python -m cosmos_generator planet logs                # Show all logs
python -m cosmos_generator planet logs --tail 20       # Show the last 20 lines
python -m cosmos_generator planet logs --lines 50      # Show 50 lines
python -m cosmos_generator planet logs --level INFO    # Filter by level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# The summary is automatically included in the log file after each generation
python -m cosmos_generator planet logs --path          # Show the log file path
```

Options for the `planet generate` subcommand:
- `--type TYPE`: Planet type (desert, furnace, etc.) - case insensitive
- `--seed SEED`: Seed for reproducible generation (default: random)
- `--output FILE`: Output file path (default: output/planets/result/[type]/[seed].png)
- `--variation NAME`: Texture variation (depends on planet type, see below)
- `--rings`: Add rings
- `--atmosphere`: Add atmosphere
- `--clouds VALUE`: Add clouds with specific coverage (0.0-1.0, where 1.0 is full coverage)
- `--light-intensity VALUE`: Light intensity (0.0-2.0)
- `--light-angle DEG`: Light source angle (0-359)
- `--rotation DEG`: Rotation in degrees
- `--zoom VALUE`: Zoom level (0.0-1.0, where 0.0=far/small, 1.0=close/large). Default values: 0.95 for planets without rings, 0.25 for planets with rings.
- `--list-types`: List available planet types
- `--list-variations`: List available variations for each planet type
- `--help`: Show help

Options for the `planet clean` subcommand:
- `--debug`: Delete only debug files (textures, etc.)
- `--examples`: Delete only example files
- `--results`: Delete only final result files
- `--all`: Delete all files (default if no option is specified)
- `--dry-run`: Show which files would be deleted without actually deleting them
- `--help`: Show help

Options for the `planet logs` subcommand:
- `--lines N`: Show N lines of the log (default: all)
- `--tail N`: Show the last N lines of the log
- `--level LEVEL`: Filter logs by minimum level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--path`: Show the log file path
- `--help`: Show help

## Planet Variations

Cosmos Generator supports different texture variations for each planet type. You can specify a variation using the `--variation` parameter. If not specified, a default variation will be used.

Currently available variations:

- **Desert**:
  - `arid` (default): Classic desert planet with dunes and canyons

- **Ocean**:
  - `water_world` (default): Planet entirely covered by water with no land masses
  - `archipelago`: Ocean planet with scattered islands and archipelagos

You can list all available variations with:
```bash
python -m cosmos_generator planet generate --list-variations
```

Example usage:
```bash
# Generate an Ocean planet with archipelago variation
python -m cosmos_generator planet generate --type ocean --variation archipelago

# Generate a Desert planet with default variation (arid)
python -m cosmos_generator planet generate --type desert
```

## Output Folder Structure

Cosmos Generator organizes the generated files in the following folder structure:

```
output/
└── planets/                # Main folder for planets
    ├── debug/              # Debug files
    │   ├── planets.log     # Log file with detailed generation information
    │   └── textures/       # Textures generated during the process
    │       ├── terrain/    # Base terrain textures
    │       │   └── [seed].png
    │       └── clouds/     # Cloud textures
    │           └── [seed]/
    │               ├── texture.png  # Cloud texture
    │               └── mask.png     # Cloud mask
    ├── examples/           # Examples generated by example scripts
    │   ├── test_clouds/
    │   ├── test_ocean/
    │   ├── test_atmosphere/
    │   └── ...
    └── result/             # Final results organized by type
        ├── desert/         # Desert type planets
        │   └── [seed].png
        ├── ocean/          # Ocean type planets
        │   └── [seed].png
        └── .../            # Other planet types
```

### Folder Description

- **debug**: Contains intermediate files generated during the creation process, useful for debugging and analysis.
  - **planets.log**: Log file containing detailed information about the planet generation process, including execution times, parameters used, and errors encountered. This file is deleted when using the `clean` command with the `--debug` or `--all` option.
  - **textures/terrain**: Base terrain textures before applying lighting and effects.
  - **textures/clouds**: Cloud textures and masks used in planets with clouds.

- **examples**: Contains images generated by the example scripts in the `examples/planets/` folder.

- **result**: Contains the final generated planets, organized by type. This is the default location where planets are saved when using the CLI without specifying an output path.

## Logging System

Cosmos Generator includes a detailed logging system that records information about the planet generation process. The logs are saved in the `output/planets/debug/planets.log` file and can be viewed with the `planet logs` subcommand.

Each planet generation is clearly marked in the log file with visual separators, making it easy to identify where a generation starts and ends. The logging system records:

- General information about planet generation (type, seed, parameters)
- Execution times for each step of the process with specific details:
  - Texture generation: planet type, size
  - Lighting: angle, intensity, falloff factor
  - Atmosphere: fill percentage, blur radius
  - Clouds: coverage, generation threshold
  - Rings: complexity, number of rings, size factor
- A detailed summary at the end of each generation showing:
  - Duration of each step
  - Percentage of total time spent on each step
  - Total generation time
- Errors and exceptions that may occur during the process
- Paths of generated files

The summary is automatically included in the log file after each generation.

Example log output:

```
2025-04-17 15:59:25 [INFO] cosmos_generator: [cli] Generating Desert planet with seed 12345
2025-04-17 15:59:25 [INFO] cosmos_generator: [generator] Initializing Desert planet instance
2025-04-17 15:59:25 [DEBUG] cosmos_generator: [generator] Planet instance initialized in 1.97ms (rendering will start next)
2025-04-17 15:59:25 [INFO] cosmos_generator: [generator]
================================================================================
=== STARTING GENERATION: DESERT PLANET (SEED: 12345) - 2025-04-17 15:59:25 ===
================================================================================
2025-04-17 15:59:25 [DEBUG] cosmos_generator: [generator] Generation parameters:
    size: 512
    light_intensity: 1.0
    light_angle: 45.0
    has_rings: False
    has_atmosphere: False
    has_clouds: False
2025-04-17 15:59:25 [DEBUG] cosmos_generator: [planet] Generating texture for Desert planet (size: 512x512)
2025-04-17 16:00:21 [DEBUG] cosmos_generator: [generator] Step 'generate_texture' completed in 55298.61ms - Type: Desert, Size: 512x512
2025-04-17 16:00:21 [DEBUG] cosmos_generator: [planet] Applying lighting to Desert planet (angle: 45.0°, intensity: 1.0)
2025-04-17 16:00:22 [DEBUG] cosmos_generator: [generator] Step 'apply_lighting' completed in 1109.86ms - Angle: 45.0°, Intensity: 1.0, Falloff: 0.6
2025-04-17 16:00:22 [INFO] cosmos_generator: [cli] Planet generation completed in 56477.01ms
2025-04-17 16:00:22 [INFO] cosmos_generator: [generator]
================================================================================
=== GENERATION COMPLETED: DESERT PLANET (SEED: 12345) - 2025-04-17 16:00:22 ===
=== Duration: 56474.67ms ===
================================================================================
2025-04-17 16:00:22 [INFO] cosmos_generator: [generator] Successfully generated Desert planet with seed 12345 in 56474.67ms
2025-04-17 16:00:22 [INFO] cosmos_generator: [generator] Saved to output/planets/result/desert/12345.png
2025-04-17 16:00:22 [DEBUG] cosmos_generator: [generator]
--------------------------------------------------------------------------------
=== GENERATION STEPS SUMMARY ===
--------------------------------------------------------------------------------
    generate_texture: 55298.61ms (98.0%) - Type: Desert, Size: 512x512
    apply_lighting: 1109.86ms (2.0%) - Angle: 45.0°, Intensity: 1.0, Falloff: 0.6
    apply_features: 0.00ms (0.0%) - No features applied
--------------------------------------------------------------------------------
    Total steps duration: 56408.46ms
--------------------------------------------------------------------------------
```

## Testing

Cosmos Generator includes a comprehensive test suite to ensure all functionality works as expected. To run the tests, you'll need to install the testing dependencies first:

```bash
# Install testing dependencies
pip install pytest pytest-cov

# Or install all development dependencies
pip install -r requirements-dev.txt
```

Then you can run the tests using the `test` subcommand:

```bash
# Run all tests
python -m cosmos_generator test

# Run tests with verbose output
python -m cosmos_generator test --verbose

# Run tests with coverage report
python -m cosmos_generator test --coverage

# Run specific tests
python -m cosmos_generator test --test-path tests/test_planet_generator.py

# Run tests matching a pattern
python -m cosmos_generator test --pattern "test_planet_*.py"
```

The test suite includes tests for:

- **Planet Generation**: Tests for creating different types of planets with various features
- **Planet Features**: Tests for atmosphere, clouds, rings, and other planet features
- **Container**: Tests for the Container class that handles display, zoom, and rotation
- **Utilities**: Tests for utility functions like image manipulation, math operations, and directory management
- **CLI**: Tests for the command-line interface and its subcommands

Running tests with the `--coverage` option generates a coverage report showing which parts of the code are covered by tests.

## Requirements

- Python 3.7+
- Pillow (PIL fork) for image manipulation
- NumPy for mathematical operations
- PyFastNoiseLite for high-performance noise generation
- pytest (for running tests)
- pytest-cov (for test coverage reports)

## License

MIT
