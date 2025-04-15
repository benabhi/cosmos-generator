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

Cosmos Generator utiliza una estructura de subcomandos para organizar sus funcionalidades:

```bash
# Mostrar ayuda general
python -m cosmos_generator --help

# Mostrar versión
python -m cosmos_generator --version

# Mostrar ayuda específica para el subcomando planet
python -m cosmos_generator planet --help
```

#### Generación de Planetas

```bash
# Con ruta de salida personalizada
python -m cosmos_generator planet --type desert --size 512 --seed 987 --output planet.png --rings --atmosphere --light-angle 30

# Con ruta de salida por defecto (output/planets/desert/987.png)
python -m cosmos_generator planet --type desert --size 512 --seed 987 --rings --atmosphere --light-angle 30

# Listar tipos de planetas disponibles
python -m cosmos_generator planet --list-types
```

Opciones del subcomando `planet`:
- `--type TYPE`: Tipo de planeta (desert, furnace, etc.) - insensible a mayúsculas/minúsculas
- `--size SIZE`: Tamaño de la imagen en píxeles (default: 512)
- `--seed SEED`: Semilla para generación reproducible (default: aleatorio)
- `--output FILE`: Ruta del archivo de salida (default: output/planets/[type]/[seed].png)
- `--rings`: Añadir anillos
- `--atmosphere`: Añadir atmósfera
- `--light-intensity VALUE`: Intensidad de la luz (0.0-2.0)
- `--light-angle DEG`: Ángulo de la fuente de luz (0-359)
- `--rotation DEG`: Rotación en grados
- `--list-types`: Listar tipos de planetas disponibles
- `--help`: Mostrar ayuda

## Requirements

- Python 3.7+
- Pillow (PIL fork) for image manipulation
- NumPy for mathematical operations
- OpenSimplex for noise generation

## License

MIT
