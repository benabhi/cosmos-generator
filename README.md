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
pip install cosmos-generator
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
```

#### Planet Generation

```bash
# With custom output path
python -m cosmos_generator planet generate --type desert --seed 987 --output planet.png --rings --atmosphere --light-angle 30

# With default output path (output/planets/result/desert/987.png)
python -m cosmos_generator planet generate --type desert --seed 987 --rings --atmosphere --light-angle 30

# Generate planet with clouds (coverage of 0.7 or 70%)
python -m cosmos_generator planet generate --type ocean --clouds 0.7 --seed 12345

# List available planet types
python -m cosmos_generator planet generate --list-types

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
python -m cosmos_generator planet logs --summary       # Show the last generation summary
python -m cosmos_generator planet logs --path          # Show the log file path
```

Options for the `planet generate` subcommand:
- `--type TYPE`: Planet type (desert, furnace, etc.) - case insensitive
- `--seed SEED`: Seed for reproducible generation (default: random)
- `--output FILE`: Output file path (default: output/planets/result/[type]/[seed].png)
- `--rings`: Add rings
- `--atmosphere`: Add atmosphere
- `--clouds VALUE`: Add clouds with specific coverage (0.0-1.0, where 1.0 is full coverage)
- `--light-intensity VALUE`: Light intensity (0.0-2.0)
- `--light-angle DEG`: Light source angle (0-359)
- `--rotation DEG`: Rotation in degrees
- `--zoom VALUE`: Zoom level (0.0-1.0, where 0.0=far/small, 1.0=close/large). Default values: 0.95 for planets without rings, 0.25 for planets with rings.
- `--list-types`: List available planet types
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
- `--summary`: Show the last generation summary
- `--path`: Show the log file path
- `--help`: Show help

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

The logging system records:

- General information about planet generation (type, seed, parameters)
- Execution times for each step of the process with specific details:
  - Texture generation: planet type, size
  - Lighting: angle, intensity, falloff factor
  - Atmosphere: fill percentage, blur radius
  - Clouds: coverage, generation threshold
  - Rings: complexity, number of rings, size factor
- Errors and exceptions that may occur during the process
- Paths of generated files

Example log output:

```
2025-04-15 19:10:19 [INFO] cosmos_generator: [cli] Generating Desert planet with seed 12345
2025-04-15 19:10:19 [INFO] cosmos_generator: [generator] Initializing Desert planet instance
2025-04-15 19:10:19 [DEBUG] cosmos_generator: [generator] Planet instance initialized in 1.53ms (rendering will start next)
2025-04-15 19:10:19 [INFO] cosmos_generator: [cli] Exporting planet to output/planets/result/desert/12345.png
2025-04-15 19:10:19 [INFO] cosmos_generator: [generator] Starting generation of Desert planet with seed 12345
2025-04-15 19:10:19 [DEBUG] cosmos_generator: [planet] Generating texture for Desert planet (size: 512x512)
2025-04-15 19:11:22 [DEBUG] cosmos_generator: [generator] Step 'generate_texture' completed in 63014.32ms - Type: Desert, Size: 512x512
2025-04-15 19:10:19 [DEBUG] cosmos_generator: [planet] Applying lighting to Desert planet (angle: 315°, intensity: 0.8)
2025-04-15 19:11:23 [DEBUG] cosmos_generator: [generator] Step 'apply_lighting' completed in 1294.48ms - Angle: 315°, Intensity: 0.8, Falloff: 1.8
2025-04-15 19:11:23 [DEBUG] cosmos_generator: [planet] Applying atmosphere to Desert planet
2025-04-15 19:11:24 [DEBUG] cosmos_generator: [generator] Step 'apply_atmosphere' completed in 18.23ms - Padding: 2.0%, blur: 1px
2025-04-15 19:11:24 [DEBUG] cosmos_generator: [generator] Step 'apply_features' completed in 18.40ms - Applied: atmosphere
2025-04-15 19:11:24 [INFO] cosmos_generator: [cli] Planet generation completed in 64396.38ms
2025-04-15 19:11:24 [INFO] cosmos_generator: [generator] Successfully generated Desert planet with seed 12345 in 64394.41ms
2025-04-15 19:11:24 [INFO] cosmos_generator: [generator] Saved to output/planets/result/desert/12345.png
2025-04-15 19:11:24 [DEBUG] cosmos_generator: [generator] Generation steps:
    generate_texture: 63014.32ms - Type: Desert, Size: 512x512
    apply_lighting: 1294.48ms - Angle: 315°, Intensity: 0.8, Falloff: 1.8
    apply_atmosphere: 18.23ms - Padding: 2.0%, blur: 1px
    apply_features: 18.40ms - Applied: atmosphere
```

## Requirements

- Python 3.7+
- Pillow (PIL fork) for image manipulation
- NumPy for mathematical operations
- OpenSimplex for noise generation

## License

MIT
