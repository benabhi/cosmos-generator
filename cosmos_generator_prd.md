# Product Requirements Document: Cosmos Generator (Python v1.0)

## 1. Product Overview

### 1.1 Product Description
Cosmos Generator is a Python library that procedurally generates detailed images of celestial bodies using PIL/Pillow. The core generator creates 12 different planet types with unique characteristics, incorporating lighting simulation and atmospheric effects.

### 1.2 Purpose
The library is designed to be integrated into Python applications requiring procedurally generated celestial bodies, such as space exploration games, educational tools, or sci-fi themed applications.

### 1.3 Future Scope
Although initial focus is on planet generation, the architecture supports future expansion to include stars, moons, nebulae, and asteroid fields.

## 2. Features and Requirements

### 2.1 Planet Types
The generator will create these planet types, each with distinct visual characteristics:
- Desert: Arid worlds with dunes, canyons, and erosion patterns
- Furnace: Volcanic with lava flows, magma, and active volcanism
- Grave: Dead worlds with heavy cratering and ancient terrain
- Ice: Frozen surfaces with ice sheets, glaciers, and crystalline structures
- Jovian: Gas giants with cloud bands, storms, and atmospheric turbulence
- Jungle: Verdant worlds with dense vegetation and river systems
- Living: Biotechnological worlds with organic-looking surface patterns
- Ocean: Water-covered worlds with archipelagos and varied depths
- Rocky: Mountainous terrain with canyons, peaks, and geological formations
- Tainted: Contaminated worlds with unnatural colors and degradation
- Vital: Earth-like balanced ecosystems with varied biomes
- Shattered: Catastrophically destroyed worlds with exposed cores and fragments

### 2.2 Technical Requirements

#### 2.2.1 Core Functionality
- Generate planet images with customizable resolution (default 512x512 pixels)
- Support PNG output format with transparency
- Allow generation with random seed or specified seed for reproducibility
- Implement lighting/shading model with directional light source
- Customize basic planet attributes (colors, texture variations, etc.)
- Provide methods for optional planetary features:
  - Rings: Elliptical ring systems with proper depth perception
  - Atmosphere: Configurable atmospheric glow
  - Clouds: Layered cloud systems for applicable planet types
  - Surface details: Craters, mountains, etc.

#### 2.2.2 Library Structure
- Object-oriented architecture following Python best practices
- Modular design allowing easy extension
- Proper docstrings and type hints
- Basic error handling and input validation
- Extensible for future celestial body types
- Use of standard Python libraries (Pillow, NumPy)

#### 2.2.3 Command Line Interface
- Provide script for generating images directly from command line
- Support parameters for planet type, size, seed, output path, and features
- Include help documentation

## 3. Architecture and Design

### 3.1 Module Structure
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
│       ├── furnace.py
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

### 3.2 Class Structure

#### Core Components
- **PlanetGenerator**: Main entry point for creating planets
- **NoiseGenerator**: Implements and combines noise algorithms (Perlin, Simplex, Worley)
- **TextureGenerator**: Creates base textures for different planet types
- **ColorPalette**: Manages color schemes for different celestial bodies

#### Celestial Bodies
- **AbstractCelestialBody**: Base class for all celestial objects
- **AbstractPlanet**: Base for all planet types with common generation flow:
  ```
  generate() -> generateTexture() -> applyLighting() -> applyFeatures()
  ```
- **Concrete Planet Classes**: Implement specific characteristics for each planet type

#### Features
- **Rings**: Generates realistic planetary ring systems
- **Atmosphere**: Creates atmospheric glow effects
- **Clouds**: Generates cloud layers with varying patterns and opacity
- **Surface**: Adds terrain details like craters, mountains, etc.

#### Utils
- **ImageUtils**: Image manipulation helpers
- **LightingUtils**: Handles lighting and shading calculations
- **MathUtils**: Common mathematical operations
- **RandomUtils**: Seeded random number generation
- **Viewport**: Manages view perspective, zoom, pan, and rotation

### 3.3 Ring System Implementation
The ring system will use the following approach:
1. Generate an elliptical master template centered on the planet
2. Decompose into logical layers:
   - External arcs: Areas of rings not intersecting with planet (using difference operation)
   - Front semi-band: Only the portion passing in front of planet (using intersection)
3. Render in Z-buffer order:
   - First: Planet
   - Second: External arcs
   - Third: Front semi-band
4. Ensure the ellipse is significantly wider than the planet with its central part passing through the planet

### 3.4 API Usage Example

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

## 4. Command Line Interface

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

## 5. Texture Generation Approach

### 5.1 Noise Algorithm Stack
- Multiple layers of noise (Perlin, Simplex, Worley)
- Combined at different frequencies and amplitudes
- Domain warping for more organic distortions
- Fractal techniques for natural details

### 5.2 Key Visual Elements by Planet Type

#### Desert
- Dune patterns using domain-warped Simplex noise
- Canyon formations with ridged-multi fractal
- Erosion patterns and ancient riverbeds

#### Furnace
- Lava flows with animated noise patterns
- Volcanic cones and calderas using cellular noise
- Heat distortion and emission effects

#### Ice
- Crystalline patterns with high-frequency noise
- Fracture patterns using Voronoi/cellular noise
- Glacier formations with flow algorithms

#### Jovian
- Horizontal cloud bands with varied colors
- Large storm systems using distorted Worley noise
- Turbulent flow patterns between bands

#### Vital (Earth-like)
- Varied biomes based on latitude/elevation
- Realistic continent generation
- Ocean depth variations
- Cloud systems with weather patterns

## 6. Implementation Plan

### 6.1 Phase 1: Core Framework
- Set up project structure
- Implement core classes and utilities
- Develop noise generators and basic texture generation
- Create viewport system

### 6.2 Phase 2: Initial Planet Implementation
- Implement first planet type (Desert)
- Develop spherical lighting model
- Create basic atmospheric effects
- Implement CLI interface

### 6.3 Phase 3: Features and Additional Planets
- Implement rings system with proper perspective
- Add cloud generation
- Develop remaining planet types
- Enhance texture algorithms

### 6.4 Phase 4: Refinement
- Optimize performance
- Add customization options
- Comprehensive documentation
- Example scripts and usage guides

## 7. Technical Requirements
- Python 3.7+
- Pillow (PIL fork) for image manipulation
- NumPy for mathematical operations
- Optional: OpenSimplex for noise generation

## 8. Success Criteria
- All 12 planet types visually distinct and recognizable
- High-quality procedural textures using multi-layered noise
- Realistic lighting/shading with parameterized controls
- Ring systems with proper perspective and depth sorting
- Viewport system for manipulation (zoom, pan, rotate)
- Deterministic generation with same seed producing same result
- Clean, well-documented API for easy integration
- Performance suitable for real-time applications
