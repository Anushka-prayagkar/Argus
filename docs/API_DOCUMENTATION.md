# ArgusAI API Documentation

Complete API reference for the ArgusAI Safe Route Intelligence System.

---

## Base URL

```
Production: https://your-app.railway.app
Development: http://localhost:8001
```

---

## Authentication

Currently, the API is open and does not require authentication. For production use, consider implementing API keys or OAuth.

---

## Endpoints

### 1. Live Conditions

Get current weather, traffic, air quality, and environmental conditions.

#### Request

```http
GET /api/live-conditions
```

#### Response

```json
{
  "conditions": {
    "weather": {
      "temperature_c": 28.5,
      "feels_like_c": 30.2,
      "precipitation_mm": 0.0,
      "windspeed_kmh": 12.3,
      "wind_direction_deg": 180,
      "humidity_pct": 65,
      "weathercode": 0,
      "visibility_km": 10.0,
      "source": "open-meteo"
    },
    "air_quality": {
      "pm2_5": 15.2,
      "pm10": 28.5,
      "dust": 0.0,
      "aqi": 65,
      "aqi_level": "MODERATE",
      "haze_present": false,
      "source": "open-meteo-airquality"
    },
    "sun": {
      "sunrise": "06:30 IST",
      "sunset": "18:45 IST",
      "is_night": false,
      "is_golden_hour": false,
      "daylight_hours": 12.3,
      "source": "sunrise-sunset.org"
    },
    "traffic": {
      "congestion_level": "FREE_FLOW",
      "avg_speed_kmh": 45.2,
      "free_flow_speed": 50.0,
      "congestion_ratio": 0.90,
      "traffic_delay_min": 2.5,
      "points": [...],
      "source": "tomtom"
    },
    "hour": 14,
    "is_rush_hour": 0,
    "is_night": false,
    "timestamp": "2026-04-14 14:30:00 IST"
  },
  "danger_multiplier": 1.15,
  "warnings": [
    "Moderate traffic expected",
    "Reduced visibility — ride carefully"
  ],
  "summary": {
    "road_surface_risk": "LOW",
    "visibility_status": "GOOD",
    "traffic_status": "FREE_FLOW",
    "air_quality": "MODERATE",
    "riding_advisory": "SAFE"
  }
}
```

#### Weather Codes

| Code | Description |
|------|-------------|
| 0 | Clear sky |
| 1-3 | Partly cloudy |
| 45, 48 | Fog |
| 51-67 | Rain |
| 71-77 | Snow |
| 80-82 | Rain showers |
| 85-86 | Snow showers |
| 95-99 | Thunderstorm |

---

### 2. Route Comparison

Compare safe route vs fast route between two points.

#### Request

```http
GET /api/route-comparison?origin_lat={lat}&origin_lng={lng}&dest_lat={lat}&dest_lng={lng}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| origin_lat | float | Yes | Origin latitude (e.g., 18.9894) |
| origin_lng | float | Yes | Origin longitude (e.g., 73.1175) |
| dest_lat | float | Yes | Destination latitude |
| dest_lng | float | Yes | Destination longitude |

#### Response

```json
{
  "status": "ok",
  "safe_route": {
    "distance_km": 9.82,
    "time_min": 18.2,
    "avg_danger": 0.156,
    "hazard_count": 7,
    "geojson": {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": {
            "type": "LineString",
            "coordinates": [[73.1175, 18.9894], ...]
          },
          "properties": {
            "mode": "safe",
            "total_distance_km": 9.82,
            "estimated_time_min": 18.2
          }
        },
        {
          "type": "Feature",
          "geometry": {
            "type": "Point",
            "coordinates": [73.1180, 18.9900]
          },
          "properties": {
            "pothole_count": 2,
            "crash_count": 1,
            "blackspot_present": 0,
            "danger_probability": 0.45
          }
        }
      ]
    }
  },
  "fast_route": {
    "distance_km": 9.57,
    "time_min": 16.5,
    "avg_danger": 0.342,
    "hazard_count": 11,
    "geojson": {...}
  },
  "safety_improvement": {
    "danger_reduction_pct": 54.4,
    "extra_distance_km": 0.25,
    "extra_time_min": 1.7,
    "avoided_hazards": 4,
    "live_conditions_applied": true,
    "danger_multiplier": 1.15,
    "routing_factors": {
      "rain_adjusted": false,
      "night_adjusted": false,
      "traffic_adjusted": false,
      "wind_adjusted": false
    },
    "performance_proof": {
      "nodes_analyzed": 8547,
      "nodes_selected": 142,
      "search_time_ms": 234.56,
      "total_path_weight": 1847.32,
      "ml_model_prediction": "ArgusVision-DeepRoute v3.1 (Optimal Safety)"
    }
  },
  "live_conditions": {...},
  "danger_multiplier": 1.15
}
```

---

### 3. Single Route

Get a single route (safe or fast mode).

#### Request

```http
GET /api/safe-route?origin_lat={lat}&origin_lng={lng}&dest_lat={lat}&dest_lng={lng}&mode={mode}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| origin_lat | float | Yes | Origin latitude |
| origin_lng | float | Yes | Origin longitude |
| dest_lat | float | Yes | Destination latitude |
| dest_lng | float | Yes | Destination longitude |
| mode | string | No | Route mode: `safe` or `fast` (default: `safe`) |

#### Response

```json
{
  "status": "ok",
  "mode": "safe",
  "origin": {
    "lat": 18.9894,
    "lng": 73.1175,
    "node": 123456
  },
  "destination": {
    "lat": 19.0771,
    "lng": 72.9988,
    "node": 789012
  },
  "metrics": {
    "total_distance_km": 9.82,
    "estimated_time_min": 18.2,
    "avg_danger_score": 0.156,
    "max_danger_score": 0.45,
    "hazard_count": 7,
    "blackspot_count": 2
  },
  "geojson": {...},
  "live_conditions": {...},
  "danger_multiplier": 1.15
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid coordinates provided"
}
```

### 404 Not Found

```json
{
  "detail": "No route found between these points"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Route engine not initialized"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production:

- Recommended: 100 requests per minute per IP
- TomTom API: 2500 requests per day (free tier)

---

## Data Models

### Danger Multiplier Calculation

```python
danger_multiplier = (
    rain_multiplier *      # 1.0 + (rain_mm * 0.15)
    visibility_multiplier * # 1.5 if vis < 0.5km else 1.25 if vis < 2km else 1.0
    wind_multiplier *      # 1.2 if wind > 40kmh else 1.1 if wind > 25kmh else 1.0
    temperature_multiplier * # 1.15 if temp > 40°C else 1.1 if temp > 37°C else 1.0
    storm_multiplier *     # 1.6 if thunderstorm else 1.4 if heavy rain else 1.0
    haze_multiplier *      # 1.3 if AQI > 150 else 1.15 if AQI > 100 else 1.0
    night_multiplier *     # 1.35 if night else 1.0
    traffic_multiplier *   # 1.4 if standstill else 1.25 if heavy else 1.1 if moderate else 1.0
    rush_hour_multiplier   # 1.15 if rush hour else 1.0
)
```

### Edge Weight Calculation

```python
dynamic_weight = base_safety_weight * danger_multiplier * edge_specific_factors

# Edge-specific factors:
# - Bridge in rain: 1.4x
# - Residential road at night: 1.25x
# - High-speed road in strong wind: 1.2x
# - Major road in heavy traffic: 1.3x
```

---

## Usage Examples

### cURL

```bash
# Get live conditions
curl "http://localhost:8001/api/live-conditions"

# Compare routes
curl "http://localhost:8001/api/route-comparison?origin_lat=18.9894&origin_lng=73.1175&dest_lat=19.0771&dest_lng=72.9988"

# Get safe route
curl "http://localhost:8001/api/safe-route?origin_lat=18.9894&origin_lng=73.1175&dest_lat=19.0220&dest_lng=73.0297&mode=safe"
```

### JavaScript (Axios)

```javascript
import axios from 'axios';

const API_URL = 'http://localhost:8001';

// Get live conditions
const conditions = await axios.get(`${API_URL}/api/live-conditions`);

// Compare routes
const comparison = await axios.get(`${API_URL}/api/route-comparison`, {
  params: {
    origin_lat: 18.9894,
    origin_lng: 73.1175,
    dest_lat: 19.0771,
    dest_lng: 72.9988
  }
});

// Get safe route
const route = await axios.get(`${API_URL}/api/safe-route`, {
  params: {
    origin_lat: 18.9894,
    origin_lng: 73.1175,
    dest_lat: 19.0220,
    dest_lng: 73.0297,
    mode: 'safe'
  }
});
```

### Python (Requests)

```python
import requests

API_URL = 'http://localhost:8001'

# Get live conditions
response = requests.get(f'{API_URL}/api/live-conditions')
conditions = response.json()

# Compare routes
response = requests.get(f'{API_URL}/api/route-comparison', params={
    'origin_lat': 18.9894,
    'origin_lng': 73.1175,
    'dest_lat': 19.0771,
    'dest_lng': 72.9988
})
comparison = response.json()

# Get safe route
response = requests.get(f'{API_URL}/api/safe-route', params={
    'origin_lat': 18.9894,
    'origin_lng': 73.1175,
    'dest_lat': 19.0220,
    'dest_lng': 73.0297,
    'mode': 'safe'
})
route = response.json()
```

---

## WebSocket Support (Future)

Real-time updates via WebSocket (planned):

```javascript
const ws = new WebSocket('ws://localhost:8001/ws/live-updates');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Live update:', data);
};
```

---

## API Versioning

Current version: `v1` (implicit)

Future versions will use URL prefix:
- `/api/v1/route-comparison`
- `/api/v2/route-comparison`

---

## Best Practices

1. **Cache live conditions** for 5 minutes to reduce API calls
2. **Batch route requests** when possible
3. **Handle errors gracefully** with fallback routes
4. **Validate coordinates** before sending requests
5. **Use HTTPS** in production
6. **Implement retry logic** for failed requests
7. **Monitor API usage** to stay within rate limits

---

## Support

For API issues or questions:
- GitHub Issues: https://github.com/yourusername/argusai/issues
- Email: support@argusai.com

---

**Last Updated:** 2026-04-14  
**API Version:** 1.0.0
