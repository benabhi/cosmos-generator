# Cosmos Generator

A Python library for procedurally generating detailed images of celestial bodies using PIL/Pillow. The core generator creates 12 different planet types with unique characteristics, incorporating lighting simulation and atmospheric effects.

## Features

- Generate 12 different planet types with unique visual characteristics
- Fixed resolution of 512x512 pixels for consistent display
- Container class for displaying planets with proper proportions
- PNG output format with transparency
- Random seed or specified seed for reproducibility
- Lighting/shading model with directional light source
- Optional planetary features:
  - Rings: Elliptical ring systems with proper depth perception
  - Atmosphere: Configurable atmospheric glow
  - Clouds: Layered cloud systems for applicable planet types
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

# Generate desert planet with rings and atmosphere
planet = generator.create("Desert", {
    "size": 512,  # Tamaño fijo de 512x512
    "seed": 12345,
    "rings": True,
    "lighting": {
        "intensity": 1.0,
        "angle": 45,
        "falloff": 0.7
    },
    "atmosphere": True
})

# Basic save method
planet.save("desert_planet_12345.png")

# Use container for fixed size display and rotation
container = Container()
container.set_content(planet)
container.rotate(45)  # Optional rotation
container.export("desert_planet_container.png")
```

### Command Line Interface

```bash
# Con ruta de salida personalizada
python -m cosmos_generator --type desert --size 512 --seed 987 --output planet.png --rings --atmosphere --light-angle 30

# Con ruta de salida por defecto (output/planets/desert/987.png)
python -m cosmos_generator --type desert --size 512 --seed 987 --rings --atmosphere --light-angle 30
```

Options:
- `--type TYPE`: Planet type (desert, furnace, etc.) - case insensitive
- `--size SIZE`: Image size in pixels (default: 512)
- `--seed SEED`: Seed for reproducible generation (default: random)
- `--output FILE`: Output file path (default: output/planets/[type]/[seed].png)
- `--rings`: Add rings
- `--atmosphere`: Add atmosphere
- `--light-intensity VALUE`: Light intensity (0.0-2.0)
- `--light-angle DEG`: Light source angle (0-359)
- `--rotation DEG`: Rotation in degrees
- `--help`: Display help

## Requirements

- Python 3.7+
- Pillow (PIL fork) for image manipulation
- NumPy for mathematical operations
- OpenSimplex for noise generation

## License

MIT
