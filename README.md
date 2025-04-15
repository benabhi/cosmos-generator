# Cosmos Generator

A Python library for procedurally generating detailed images of celestial bodies using PIL/Pillow. The core generator creates 12 different planet types with unique characteristics, incorporating lighting simulation and atmospheric effects.

## Features

- Generate 12 different planet types with unique visual characteristics
- Customizable resolution (default 512x512 pixels)
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
from cosmos_generator.utils import Viewport

# Create generator
generator = PlanetGenerator()

# Generate desert planet with rings and atmosphere
planet = generator.create("Desert", {
    "size": 1024,
    "seed": 12345,
    "rings": True,
    "lighting": {
        "intensity": 1.0,
        "angle": 45,
        "falloff": 0.7
    },
    "atmosphere": {
        "intensity": 0.8,
        "color": (200, 220, 255, 60)
    }
})

# Basic save method
planet.save("desert_planet_12345.png")

# Use viewport for more control
viewport = Viewport(width=800, height=600, initial_zoom=1.0)
viewport.set_content(planet)
viewport.zoom(1.5)
viewport.rotate(45)
viewport.pan(50, -30)
viewport.export("desert_planet_zoomed.png")
```

### Command Line Interface

```bash
python -m cosmos_generator --type Desert --size 512 --seed 987 --output planet.png --rings --atmosphere 0.7 --light-angle 30
```

Options:
- `--type TYPE`: Planet type (Desert, Furnace, etc.)
- `--size SIZE`: Image size in pixels (default: 512)
- `--seed SEED`: Seed for reproducible generation (default: random)
- `--output FILE`: Output file path
- `--rings`: Add rings
- `--atmosphere VALUE`: Atmosphere intensity (0.0-1.0)
- `--light-intensity VALUE`: Light intensity (0.0-2.0)
- `--light-angle DEG`: Light source angle (0-359)
- `--viewport-width/height WIDTH`: Viewport dimensions
- `--zoom FACTOR`: Zoom factor (0.1-5.0)
- `--rotation DEG`: Rotation in degrees
- `--help`: Display help

## Requirements

- Python 3.7+
- Pillow (PIL fork) for image manipulation
- NumPy for mathematical operations
- OpenSimplex for noise generation

## License

MIT
