# Cosmos Generator Web API

This document describes the API endpoints available in the Cosmos Generator web interface.

## Planet Types

Get available planet types and their variations.

**Endpoint:** `/api/planet-types`  
**Method:** GET  
**Response:**
```json
{
  "types": ["Desert", "Ocean", "Furnace", "Gas", "Ice", "Lava", "Rocky", "Terran", "Toxic"],
  "variations": {
    "desert": ["arid"],
    "ocean": ["water_world", "archipelago"],
    "furnace": ["standard"],
    "gas": ["standard"],
    "ice": ["standard"],
    "lava": ["standard"],
    "rocky": ["standard"],
    "terran": ["standard"],
    "toxic": ["standard"]
  },
  "defaults": {
    "desert": "arid",
    "ocean": "water_world",
    "furnace": "standard",
    "gas": "standard",
    "ice": "standard",
    "lava": "standard",
    "rocky": "standard",
    "terran": "standard",
    "toxic": "standard"
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
**Request Body:**
```json
{
  "type": "desert",
  "seed": "12345",
  "variation": "arid",
  "rings": true,
  "atmosphere": true,
  "atmosphere_glow": 0.7,
  "atmosphere_halo": 0.8,
  "atmosphere_thickness": 4,
  "atmosphere_blur": 0.6,
  "clouds": 0.5,
  "light_intensity": 1.0,
  "light_angle": 45,
  "rotation": 0,
  "zoom": 0.5
}
```

**Response:**
```json
{
  "process_id": "1620000000000",
  "status": "started",
  "message": "Planet generation started"
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
  "output": "Cleaned output/planets/debug\nCleaned output/planets/examples\nCleaned output/planets/result"
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

## Examples

### Generate a planet with curl

```bash
curl -X POST http://localhost:4000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "desert",
    "seed": "12345",
    "rings": true,
    "atmosphere": true,
    "clouds": 0.5,
    "light_angle": 45,
    "zoom": 0.5
  }'
```

### Check generation status with curl

```bash
curl http://localhost:4000/api/status/1620000000000
```

### Get planet types with curl

```bash
curl http://localhost:4000/api/planet-types
```

### Get generated planets with curl

```bash
curl http://localhost:4000/api/planets
```

### Get logs with curl

```bash
curl http://localhost:4000/api/logs?type=planets&lines=10
```

### Clean all files with curl

```bash
curl -X POST http://localhost:4000/api/clean
```

### Generate a planet with JavaScript (fetch)

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
    clouds: 0.5,
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
