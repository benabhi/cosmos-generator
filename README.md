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
python -m cosmos_generator planet generate --type desert --size 512 --seed 987 --output planet.png --rings --atmosphere --light-angle 30

# Con ruta de salida por defecto (output/planets/result/desert/987.png)
python -m cosmos_generator planet generate --type desert --size 512 --seed 987 --rings --atmosphere --light-angle 30

# Generar planeta con nubes (cobertura de 0.7 o 70%)
python -m cosmos_generator planet generate --type ocean --clouds 0.7 --seed 12345

# Listar tipos de planetas disponibles
python -m cosmos_generator planet generate --list-types

# Limpiar archivos generados de planetas
python -m cosmos_generator planet clean         # Limpia todos los archivos
python -m cosmos_generator planet clean --debug    # Limpia solo archivos de depuración
python -m cosmos_generator planet clean --examples # Limpia solo archivos de ejemplos
python -m cosmos_generator planet clean --results  # Limpia solo archivos de resultados
python -m cosmos_generator planet clean --dry-run  # Muestra qué se eliminaría sin eliminar nada
```

Opciones del subcomando `planet generate`:
- `--type TYPE`: Tipo de planeta (desert, furnace, etc.) - insensible a mayúsculas/minúsculas
- `--size SIZE`: Tamaño de la imagen en píxeles (default: 512)
- `--seed SEED`: Semilla para generación reproducible (default: aleatorio)
- `--output FILE`: Ruta del archivo de salida (default: output/planets/result/[type]/[seed].png)
- `--rings`: Añadir anillos
- `--atmosphere`: Añadir atmósfera
- `--clouds VALUE`: Añadir nubes con cobertura específica (0.0-1.0, donde 1.0 es cobertura total)
- `--light-intensity VALUE`: Intensidad de la luz (0.0-2.0)
- `--light-angle DEG`: Ángulo de la fuente de luz (0-359)
- `--rotation DEG`: Rotación en grados
- `--list-types`: Listar tipos de planetas disponibles
- `--help`: Mostrar ayuda

Opciones del subcomando `planet clean`:
- `--debug`: Eliminar solo archivos de depuración (texturas, etc.)
- `--examples`: Eliminar solo archivos de ejemplos
- `--results`: Eliminar solo archivos de resultados finales
- `--all`: Eliminar todos los archivos (por defecto si no se especifica ninguna opción)
- `--dry-run`: Mostrar qué archivos se eliminarían sin eliminarlos realmente
- `--help`: Mostrar ayuda

## Estructura de Carpetas de Output

Cosmos Generator organiza los archivos generados en la siguiente estructura de carpetas:

```
output/
└── planets/                # Carpeta principal para planetas
    ├── debug/              # Archivos de depuración
    │   └── textures/       # Texturas generadas durante el proceso
    │       ├── terrain/    # Texturas base de terreno
    │       │   └── [seed].png
    │       └── clouds/     # Texturas de nubes
    │           └── [seed]/
    │               ├── texture.png  # Textura de nubes
    │               └── mask.png     # Máscara de nubes
    ├── examples/           # Ejemplos generados por los scripts de ejemplo
    │   ├── test_clouds/
    │   ├── test_ocean/
    │   ├── test_atmosphere/
    │   └── ...
    └── result/             # Resultados finales organizados por tipo
        ├── desert/         # Planetas tipo desierto
        │   └── [seed].png
        ├── ocean/          # Planetas tipo océano
        │   └── [seed].png
        └── .../            # Otros tipos de planetas
```

### Descripción de las Carpetas

- **debug**: Contiene archivos intermedios generados durante el proceso de creación, útiles para depuración y análisis.
  - **textures/terrain**: Texturas base de terreno antes de aplicar iluminación y efectos.
  - **textures/clouds**: Texturas y máscaras de nubes utilizadas en planetas con nubes.

- **examples**: Contiene imágenes generadas por los scripts de ejemplo en la carpeta `examples/planets/`.

- **result**: Contiene los planetas finales generados, organizados por tipo. Esta es la ubicación por defecto donde se guardan los planetas cuando se usa el CLI sin especificar una ruta de salida.

## Requirements

- Python 3.7+
- Pillow (PIL fork) for image manipulation
- NumPy for mathematical operations
- OpenSimplex for noise generation

## License

MIT
