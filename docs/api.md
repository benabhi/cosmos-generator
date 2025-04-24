# Cosmos Generator Web API Documentation

This document provides a comprehensive reference for the Cosmos Generator Web API endpoints.

## Base URL

All API endpoints are relative to the base URL of your Cosmos Generator web server, typically:

```
http://localhost:5000/api
```

## Authentication

The API currently does not require authentication.

## Response Format

All API responses are in JSON format. Successful responses typically include:

- Success indicator (`success: true`)
- Relevant data
- Message describing the result

Error responses typically include:

- Error indicator (`success: false` or `error` field)
- Error message
- HTTP status code appropriate to the error

## Planet Types

Get available planet types and their variations.

**Endpoint:** `/api/planet-types`
**Method:** GET
**Response:**
```json
{
  "types": ["Desert", "Ocean", "Furnace", "Jovian", "Vital", "Toxic"],
  "variations": {
    "desert": ["arid", "dunes", "mesa"],
    "ocean": ["water_world", "archipelago", "reef"],
    "furnace": ["magma_rivers", "ember_wastes", "volcanic_hellscape"],
    "jovian": ["bands", "storm", "nebulous"],
    "vital": ["earthlike", "archipelago", "pangaea"],
    "toxic": ["toxic_veins", "acid_lakes", "corrosive_storms"]
  },
  "defaults": {
    "desert": "arid",
    "ocean": "water_world",
    "furnace": "magma_rivers",
    "jovian": "bands",
    "vital": "earthlike",
    "toxic": "toxic_veins"
  }
}
```

## Planets

Get a list of generated planets with optional filtering.

**Endpoint:** `/api/planets`
**Method:** GET
**Parameters:**
- `type` (optional): Filter by planet type (e.g., "desert")
- `has_rings` (optional): Filter by presence of rings (true/false)
- `has_atmosphere` (optional): Filter by presence of atmosphere (true/false)
- `has_clouds` (optional): Filter by presence of clouds (true/false)
- `seed` (optional): Filter by seed (partial match)

**Response:**
```json
{
  "planets": [
    {
      "type": "Desert",
      "seed": "12345",
      "path": "/path/to/planet.png",
      "filename": "12345.png",
      "url": "/static/planets/desert/12345.png",
      "params": {
        "variation": "arid",
        "atmosphere": true,
        "clouds": true,
        "rings": true
      }
    }
  ],
  "count": 1,
  "total": 10
}
```

## Generate Planet

Generate a new planet with specified parameters.

**Endpoint:** `/api/generate`
**Method:** POST

### Parameters

| Parameter | Type | Required | Default | Range | Description |
|-----------|------|----------|---------|-------|-------------|
| `type` | string | Yes | - | See planet types | Type of planet to generate (e.g., "desert", "ocean") |
| `seed` | string | No | Random | - | Seed for reproducible generation |
| `variation` | string | No | Type-specific default | See variations | Texture variation (depends on planet type) |
| `rings` | boolean | No | false | - | Whether to add rings to the planet |
| `rings_complexity` | number | No | 2 | 1 - 3 | Ring system complexity (1=minimal, 2=medium, 3=full) |
| `rings_tilt` | number | No | 30 | 0 - 75 | Tilt angle of the rings in degrees (0=edge-on, 75=more face-on) |
| `atmosphere` | boolean | No | false | - | Whether to add atmosphere to the planet |
| `atmosphere_glow` | number | No | 0.5 | 0.0 - 1.0 | Atmosphere glow intensity |
| `atmosphere_halo` | number | No | 0.7 | 0.0 - 1.0 | Atmosphere halo intensity |
| `atmosphere_thickness` | number | No | 3 | 1 - 10 | Atmosphere halo thickness in pixels |
| `atmosphere_blur` | number | No | 0.5 | 0.0 - 1.0 | Atmosphere blur amount |
| `clouds` | boolean | No | false | - | Whether to add clouds to the planet |
| `clouds_coverage` | number | No | Random (0.3-0.8) | 0.0 - 1.0 | Cloud coverage (0.0 = minimal, 1.0 = maximum coverage) |
| `light_intensity` | number | No | 1.0 | 0.1 - 2.0 | Light intensity |
| `light_angle` | number | No | 45 | 0 - 360 | Light source angle in degrees |
| `rotation` | number | No | 0 | 0 - 360 | Rotation in degrees |
| `zoom` | number | No | Type-specific default | 0.0 - 1.0 | Zoom level (0.0 = far/small, 1.0 = close/large) |

### Default Zoom Levels

- Planets without rings: 0.95
- Planets with rings: 0.25

### Planet Types and Variations

| Planet Type | Available Variations | Default Variation |
|-------------|----------------------|-------------------|
| desert | arid, dunes, mesa | arid |
| ocean | water_world, archipelago, reef | water_world |
| furnace | magma_rivers, ember_wastes, volcanic_hellscape | magma_rivers |
| jovian | bands, storm, nebulous | bands |
| vital | earthlike, archipelago, pangaea | earthlike |
| toxic | toxic_veins, acid_lakes, corrosive_storms | toxic_veins |

### Request Body Example

```json
{
  "type": "desert",
  "seed": "12345",
  "variation": "arid",
  "rings": true,
  "rings_complexity": 3,
  "rings_tilt": 45,
  "atmosphere": true,
  "atmosphere_glow": 0.7,
  "atmosphere_halo": 0.8,
  "atmosphere_thickness": 4,
  "atmosphere_blur": 0.6,
  "clouds": true,
  "clouds_coverage": 0.5,
  "light_intensity": 1.0,
  "light_angle": 45,
  "rotation": 0,
  "zoom": 0.5
}
```

### Response

```json
{
  "process_id": "1620000000000",
  "status": "started",
  "message": "Planet generation started"
}
```

### Error Responses

**Invalid planet type:**
```json
{
  "error": "Invalid planet type: 'invalid'. Valid types are: desert, ocean, furnace, jovian, vital, toxic"
}
```

**Invalid numeric parameter:**
```json
{
  "error": "Parameter 'atmosphere_glow' must be between 0.0 and 1.0. Got: 2.5"
}
```

**Invalid variation:**
```json
{
  "error": "Invalid variation 'invalid' for planet type 'desert'. Valid variations are: arid"
}
```

## Generation Status

Check the status of a planet generation process.

**Endpoint:** `/api/status/{process_id}`
**Method:** GET
**Response (in progress):**
```json
{
  "status": "running",
  "logs": ["Running command: ...", "Parameters: ...", "Working directory: ..."]
}
```

**Response (completed):**
```json
{
  "status": "completed",
  "logs": ["Running command: ...", "Parameters: ...", "Working directory: ...", "Process completed with return code: 0"],
  "result": {
    "path": "/path/to/planet.png",
    "url": "/static/planets/desert/12345.png"
  }
}
```

**Response (failed):**
```json
{
  "status": "failed",
  "logs": ["Running command: ...", "Parameters: ...", "Working directory: ...", "Error executing command: ..."],
  "error": "Generation process failed"
}
```

## Logs

Get recent log entries.

**Endpoint:** `/api/logs`
**Method:** GET
**Parameters:**
- `lines` (optional): Number of lines to retrieve (default: 100)
- `type` (optional): Type of log to retrieve ('planets' or 'webserver', default: 'planets')

**Response:**
```json
{
  "logs": ["2025-04-17 15:59:25 [INFO] cosmos_generator: [cli] Generating Desert planet with seed 12345", "..."],
  "count": 100,
  "type": "planets"
}
```

## Clean

Clean all generated files.

**Endpoint:** `/api/clean`
**Method:** POST
**Response (success):**
```json
{
  "success": true,
  "message": "All files cleaned successfully",
  "output": "Removed all planet directories from output/planets"
}
```

**Response (error):**
```json
{
  "success": false,
  "message": "Failed to clean files",
  "error": "Error message"
}
```

## Check Seed

Check if a seed is already used.

**Endpoint:** `/api/check-seed/{seed}`
**Method:** GET
**Response:**
```json
{
  "seed": "12345",
  "used": true
}
```

## Examples

### Command Line Examples (curl)

#### Generate a Desert Planet with Rings and Atmosphere

```bash
curl -X POST http://localhost:4000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "desert",
    "seed": "12345",
    "rings": true,
    "rings_complexity": 3,
    "rings_tilt": 45,
    "atmosphere": true,
    "clouds": true,
    "clouds_coverage": 0.5,
    "light_angle": 45,
    "zoom": 0.5
  }'
```

#### Generate an Ocean Planet with Archipelago Variation

```bash
curl -X POST http://localhost:4000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "ocean",
    "variation": "archipelago",
    "atmosphere": true,
    "atmosphere_glow": 0.8,
    "atmosphere_halo": 0.6,
    "light_intensity": 1.2
  }'
```

#### Generate a Gas Planet with Custom Lighting

```bash
curl -X POST http://localhost:4000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "jovian",
    "rings": true,
    "light_angle": 135,
    "light_intensity": 1.5,
    "rotation": 30,
    "zoom": 0.3
  }'
```

#### Generate a Toxic Planet with Acid Lakes

```bash
curl -X POST http://localhost:4000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "toxic",
    "variation": "acid_lakes",
    "atmosphere": true,
    "atmosphere_glow": 0.9,
    "clouds": true,
    "clouds_coverage": 0.4,
    "light_intensity": 1.1,
    "zoom": 0.7
  }'
```

#### Check Generation Status

```bash
curl http://localhost:4000/api/status/1620000000000
```

#### Get Planet Types and Variations

```bash
curl http://localhost:4000/api/planet-types
```

#### Get Generated Planets

```bash
curl http://localhost:4000/api/planets
```

#### Filter Planets by Type and Features

```bash
curl "http://localhost:4000/api/planets?type=desert&has_rings=true&has_atmosphere=true"
```

#### Search Planets by Seed

```bash
curl "http://localhost:4000/api/planets?seed=12345"
```

#### Get Planet Logs

```bash
curl "http://localhost:4000/api/logs?type=planets&lines=10"
```

#### Get Web Server Logs

```bash
curl "http://localhost:4000/api/logs?type=webserver&lines=20"
```

#### Clean All Generated Files

```bash
curl -X POST http://localhost:4000/api/clean
```

#### Check if a Seed is Already Used

```bash
curl http://localhost:4000/api/check-seed/12345
```

### JavaScript Examples

#### Generate a Planet and Poll for Status

```javascript
fetch('/api/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    type: 'desert',
    seed: '12345',
    rings: true,
    atmosphere: true,
    clouds: true,
    clouds_coverage: 0.5,
    light_angle: 45,
    zoom: 0.5
  })
})
.then(response => response.json())
.then(data => {
  console.log('Process ID:', data.process_id);

  // Poll for status
  const checkStatus = () => {
    fetch(`/api/status/${data.process_id}`)
      .then(response => response.json())
      .then(statusData => {
        console.log('Status:', statusData.status);

        if (statusData.status === 'completed') {
          console.log('Planet URL:', statusData.result.url);
          // Display the planet image
          document.getElementById('planet-image').src = statusData.result.url;
        } else if (statusData.status === 'failed') {
          console.error('Error:', statusData.error);
        } else {
          // Continue polling
          setTimeout(checkStatus, 500);
        }
      });
  };

  checkStatus();
})
.catch(error => {
  console.error('Error:', error);
});
```

#### Load and Filter Planets

```javascript
// Load all planets
fetch('/api/planets')
  .then(response => response.json())
  .then(data => {
    console.log(`Loaded ${data.count} planets out of ${data.total} total`);

    // Display planets in a grid
    const planetsGrid = document.getElementById('planets-grid');
    planetsGrid.innerHTML = '';

    data.planets.forEach(planet => {
      const planetCard = document.createElement('div');
      planetCard.className = 'planet-card';

      const img = document.createElement('img');
      img.src = planet.url;
      img.alt = `${planet.type} planet (${planet.seed})`;

      const info = document.createElement('div');
      info.className = 'planet-info';
      info.innerHTML = `
        <h3>${planet.type} Planet</h3>
        <p>Seed: ${planet.seed}</p>
        <p>Features:
          ${planet.params.rings ? 'Rings, ' : ''}
          ${planet.params.atmosphere ? 'Atmosphere, ' : ''}
          ${planet.params.clouds ? 'Clouds' : ''}
        </p>
      `;

      planetCard.appendChild(img);
      planetCard.appendChild(info);
      planetsGrid.appendChild(planetCard);
    });
  })
  .catch(error => {
    console.error('Error loading planets:', error);
  });

// Filter planets by type and features
function filterPlanets() {
  const type = document.getElementById('filter-type').value;
  const hasRings = document.getElementById('filter-rings').checked;
  const hasAtmosphere = document.getElementById('filter-atmosphere').checked;
  const hasClouds = document.getElementById('filter-clouds').checked;

  let url = '/api/planets?';
  if (type) url += `type=${type}&`;
  if (hasRings) url += 'has_rings=true&';
  if (hasAtmosphere) url += 'has_atmosphere=true&';
  if (hasClouds) url += 'has_clouds=true&';

  fetch(url)
    .then(response => response.json())
    .then(data => {
      console.log(`Filtered to ${data.count} planets`);
      // Update display with filtered planets
      // ...
    });
}
```

#### View Logs

```javascript
// Load planet logs
function loadLogs(type = 'planets', lines = 100) {
  fetch(`/api/logs?type=${type}&lines=${lines}`)
    .then(response => response.json())
    .then(data => {
      const logsContainer = document.getElementById('logs-container');
      logsContainer.innerHTML = '';

      data.logs.forEach(log => {
        const logLine = document.createElement('div');
        logLine.className = 'log-line';

        // Add appropriate class based on log level
        if (log.includes('[ERROR]')) {
          logLine.classList.add('log-error');
        } else if (log.includes('[WARNING]')) {
          logLine.classList.add('log-warning');
        } else if (log.includes('[INFO]')) {
          logLine.classList.add('log-info');
        } else if (log.includes('[DEBUG]')) {
          logLine.classList.add('log-debug');
        }

        logLine.textContent = log;
        logsContainer.appendChild(logLine);
      });
    })
    .catch(error => {
      console.error('Error loading logs:', error);
    });
}

// Switch between log types
document.getElementById('planets-logs-tab').addEventListener('click', () => {
  loadLogs('planets');
});

document.getElementById('webserver-logs-tab').addEventListener('click', () => {
  loadLogs('webserver');
});
```

#### Clean All Files

```javascript
function cleanAllFiles() {
  if (confirm('Are you sure you want to clean all generated files? This action cannot be undone.')) {
    fetch('/api/clean', {
      method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert('All files cleaned successfully!');
        // Refresh the page or update the UI
        window.location.reload();
      } else {
        alert('Failed to clean files: ' + data.message);
      }
    })
    .catch(error => {
      alert('An error occurred: ' + error.message);
    });
  }
}
```

#### Check if a Seed is Already Used

```javascript
function checkSeed(seed) {
  fetch(`/api/check-seed/${seed}`)
    .then(response => response.json())
    .then(data => {
      if (data.used) {
        console.log(`Seed ${seed} is already used.`);
        // Generate a new random seed
        generateRandomSeed();
      } else {
        console.log(`Seed ${seed} is available.`);
        // Use the seed
        document.getElementById('seed-input').value = seed;
      }
    })
    .catch(error => {
      console.error('Error checking seed:', error);
    });
}

function generateRandomSeed() {
  // Generate a random seed
  const newSeed = Math.floor(Math.random() * 100000).toString();

  // Check if the seed is already used
  checkSeed(newSeed);
}
```
