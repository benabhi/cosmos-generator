# Cosmos Generator

A Python library for procedurally generating detailed images of celestial bodies using PIL/Pillow. The core generator creates 12 different planet types with unique characteristics, incorporating lighting simulation and atmospheric effects.

## Features

- Generate 12 different planet types with unique visual characteristics
- Fixed resolution of 512x512 pixels for consistent display (not configurable by users)
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
python -m cosmos_generator planet generate --type desert --seed 987 --output planet.png --rings --atmosphere --light-angle 30

# Con ruta de salida por defecto (output/planets/result/desert/987.png)
python -m cosmos_generator planet generate --type desert --seed 987 --rings --atmosphere --light-angle 30

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

# View planet generation logs
python -m cosmos_generator planet logs                # Show all logs
python -m cosmos_generator planet logs --tail 20       # Show the last 20 lines
python -m cosmos_generator planet logs --lines 50      # Show 50 lines
python -m cosmos_generator planet logs --level INFO    # Filter by level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
python -m cosmos_generator planet logs --summary       # Show the last generation summary
python -m cosmos_generator planet logs --path          # Show the log file path
```

Opciones del subcomando `planet generate`:
- `--type TYPE`: Tipo de planeta (desert, furnace, etc.) - insensible a mayúsculas/minúsculas
- `--seed SEED`: Semilla para generación reproducible (default: aleatorio)
- `--output FILE`: Ruta del archivo de salida (default: output/planets/result/[type]/[seed].png)
- `--rings`: Añadir anillos
- `--atmosphere`: Añadir atmósfera
- `--clouds VALUE`: Añadir nubes con cobertura específica (0.0-1.0, donde 1.0 es cobertura total)
- `--light-intensity VALUE`: Intensidad de la luz (0.0-2.0)
- `--light-angle DEG`: Ángulo de la fuente de luz (0-359)
- `--rotation DEG`: Rotación en grados
- `--zoom VALUE`: Nivel de zoom (0.0-1.0, donde 0.0=muy lejos/pequeño, 1.0=muy cerca/grande)
- `--list-types`: Listar tipos de planetas disponibles
- `--help`: Mostrar ayuda

Opciones del subcomando `planet clean`:
- `--debug`: Eliminar solo archivos de depuración (texturas, etc.)
- `--examples`: Eliminar solo archivos de ejemplos
- `--results`: Eliminar solo archivos de resultados finales
- `--all`: Eliminar todos los archivos (por defecto si no se especifica ninguna opción)
- `--dry-run`: Mostrar qué archivos se eliminarían sin eliminarlos realmente
- `--help`: Mostrar ayuda

Options for the `planet logs` subcommand:
- `--lines N`: Show N lines of the log (default: all)
- `--tail N`: Show the last N lines of the log
- `--level LEVEL`: Filter logs by minimum level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--summary`: Show the last generation summary
- `--path`: Show the log file path
- `--help`: Show help

## Estructura de Carpetas de Output

Cosmos Generator organiza los archivos generados en la siguiente estructura de carpetas:

```
output/
└── planets/                # Carpeta principal para planetas
    ├── debug/              # Archivos de depuración
    │   ├── planets.log     # Archivo de log con información detallada de generación
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
  - **planets.log**: Archivo de log que contiene información detallada sobre el proceso de generación de planetas, incluyendo tiempos de ejecución, parámetros utilizados y errores encontrados. Este archivo se elimina cuando se usa el comando `clean` con la opción `--debug` o `--all`.
  - **textures/terrain**: Texturas base de terreno antes de aplicar iluminación y efectos.
  - **textures/clouds**: Texturas y máscaras de nubes utilizadas en planetas con nubes.

- **examples**: Contiene imágenes generadas por los scripts de ejemplo en la carpeta `examples/planets/`.

- **result**: Contiene los planetas finales generados, organizados por tipo. Esta es la ubicación por defecto donde se guardan los planetas cuando se usa el CLI sin especificar una ruta de salida.

## Sistema de Logging

Cosmos Generator incluye un sistema de logging detallado que registra información sobre el proceso de generación de planetas. Los logs se guardan en el archivo `output/planets/debug/planets.log` y pueden ser visualizados con el subcomando `planet logs`.

El sistema de logging registra:

- Información general sobre la generación de planetas (tipo, semilla, parámetros)
- Tiempos de ejecución para cada paso del proceso con detalles específicos:
  - Generación de textura: tipo de planeta, tamaño
  - Iluminación: ángulo, intensidad, factor de caída
  - Atmósfera: porcentaje de relleno, radio de desenfoque
  - Nubes: cobertura, umbral de generación
  - Anillos: complejidad, número de anillos, factor de tamaño
- Errores y excepciones que puedan ocurrir durante el proceso
- Rutas de archivos generados

Ejemplo de salida del log:

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
