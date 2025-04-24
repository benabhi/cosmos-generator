# Cosmos Generator

A Python library for procedurally generating detailed images of celestial bodies using PIL/Pillow. The core generator creates 12 different planet types with unique characteristics, incorporating lighting simulation and atmospheric effects.

## Directory Structure

```
cosmos_generator/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── color_palette.py
│   ├── noise_generator.py
│   ├── celestial_generator.py
│   ├── planet_generator.py
│   └── texture_generator.py
├── celestial_bodies/
│   ├── __init__.py
│   ├── base.py
│   └── planets/
│       ├── __init__.py
│       ├── abstract_planet.py
│       ├── desert.py
│       └── # Other planet types
├── features/
│   ├── __init__.py
│   ├── atmosphere.py
│   ├── clouds.py
│   ├── rings.py
│   └── surface.py
├── utils/
│   ├── __init__.py
│   ├── image_utils.py
│   ├── lighting_utils.py
│   ├── math_utils.py
│   ├── random_utils.py
│   └── viewport.py
└── cli.py
```

## Module Descriptions

### Core

- **color_palette.py**: Manages color schemes for different celestial bodies
- **noise_generator.py**: Implements and combines noise algorithms (Perlin, Simplex, Worley)
- **celestial_generator.py**: Base generator class for celestial bodies
- **planet_generator.py**: Planet-specific generator
- **texture_generator.py**: Creates base textures for different planet types

### Celestial Bodies

- **base.py**: Abstract base class for all celestial objects
- **planets/abstract_planet.py**: Base class for planets with common generation flow
- **planets/desert.py**: Desert planet implementation
- **planets/[other].py**: Other planet type implementations

### Features

- **atmosphere.py**: Creates atmospheric glow effects
- **clouds.py**: Generates cloud layers with varying patterns and opacity
- **rings.py**: Generates realistic planetary ring systems
- **surface.py**: Adds terrain details like craters, mountains, etc.

### Utils

- **image_utils.py**: Image manipulation helpers
- **lighting_utils.py**: Handles lighting and shading calculations
- **math_utils.py**: Common mathematical operations
- **random_utils.py**: Seeded random number generation
- **container.py**: Manages view perspective and rotation with fixed size display

### CLI

- **cli.py**: Command-line interface for generating planets
