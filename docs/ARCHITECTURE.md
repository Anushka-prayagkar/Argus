# ArgusAI System Architecture

Detailed technical architecture of the ArgusAI Safe Route Intelligence System.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Graph Processing](#graph-processing)
5. [Routing Algorithm](#routing-algorithm)
6. [Live Conditions Integration](#live-conditions-integration)
7. [Frontend Architecture](#frontend-architecture)
8. [Database Schema](#database-schema)
9. [Scalability Considerations](#scalability-considerations)
10. [Security](#security)

---

## System Overview

ArgusAI is a microservices-based system with clear separation between frontend, backend, and external data sources.

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                    (React + Mapbox GL JS)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│                         (FastAPI)                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   CORS       │  │  Rate        │  │  Error       │          │
│  │  Middleware  │  │  Limiting    │  │  Handling    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Route      │  │   Live       │  │   Graph      │          │
│  │  Calculator  │  │  Conditions  │  │   Manager    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
│   Graph Data     │  │  External    │  │   Cache      │
│   (OSM + ML)     │  │   APIs       │  │   Layer      │
└──────────────────┘  └──────────────┘  └──────────────┘
```

---

## Component Architecture

### Backend Components

#### 1. Route API (`route_api.py`)

**Responsibilities:**
- HTTP endpoint handling
- Request validation
- Response formatting
- CORS management

**Key Functions:**
```python
@app.get("/api/route-comparison")
async def compare_routes(origin_lat, origin_lng, dest_lat, dest_lng)

@app.get("/api/live-conditions")
async def get_live_conditions()

@app.get("/api/safe-route")
async def get_safe_route(origin_lat, origin_lng, dest_lat, dest_lng, mode)
```

#### 2. Graph Engine

**Responsibilities:**
- Load and manage OSM graph
- Node snapping
- Edge weight management
- Dynamic graph generation

**Key Functions:**
```python
def load_route_engine()
def snap_to_driveable_node(graph, lat, lng)
def build_dynamic_graph(conditions)
```

#### 3. Live Conditions Manager

**Responsibilities:**
- Parallel API calls to external services
- Data aggregation
- Danger multiplier calculation

**Key Functions:**
```python
def fetch_all_live_conditions(route_coords)
def apply_live_multipliers(conditions)
def fetch_weather()
def fetch_air_quality()
def fetch_traffic(route_coords)
def fetch_sunrise_sunset()
```

#### 4. Route Calculator

**Responsibilities:**
- A* pathfinding
- Route metrics calculation
- GeoJSON generation
- Hazard mapping

**Key Functions:**
```python
def get_route_path(origin_node, dest_node, mode)
def calculate_route_metrics(path)
def build_geojson(path, mode, metrics)
```

### Frontend Components

#### 1. MapPage Component

**Responsibilities:**
- Map initialization and rendering
- User interaction handling
- Route visualization
- Marker management

**State Management:**
```javascript
const [origin, setOrigin] = useState(null);
const [destination, setDestination] = useState(null);
const [routeData, setRouteData] = useState(null);
const [liveConditions, setLiveConditions] = useState(null);
```

#### 2. RouteStatsPanel Component

**Responsibilities:**
- Route comparison display
- Safety metrics visualization
- AI proof modal
- Live conditions display

**Props:**
```javascript
<RouteStatsPanel routeData={routeData} />
```

#### 3. API Service

**Responsibilities:**
- HTTP client configuration
- API endpoint abstraction
- Error handling

```javascript
const fetchRouteComparison = async (origin, destination);
const fetchLiveConditions = async ();
```

---

## Data Flow

### Route Calculation Flow

```
1. User clicks on map
   ↓
2. Frontend captures coordinates
   ↓
3. API request to /api/route-comparison
   ↓
4. Backend snaps coordinates to graph nodes
   ↓
5. Fetch live conditions (parallel)
   ├─ Weather API
   ├─ Traffic API
   ├─ Air Quality API
   └─ Sunrise/Sunset API
   ↓
6. Calculate danger multiplier
   ↓
7. Build dynamic graph with adjusted weights
   ↓
8. Run A* algorithm (safe mode)
   ↓
9. Run A* algorithm (fast mode)
   ↓
10. Calculate metrics for both routes
   ↓
11. Generate GeoJSON with hazard markers
   ↓
12. Return response with performance proof
   ↓
13. Frontend renders routes on map
   ↓
14. User views comparison and AI proof
```

### Live Conditions Update Flow

```
1. Timer triggers every 5 minutes
   ↓
2. Frontend calls /api/live-conditions
   ↓
3. Backend fetches from all APIs (parallel)
   ↓
4. Aggregate and calculate multiplier
   ↓
5. Return conditions + warnings
   ↓
6. Frontend updates UI
   ↓
7. If route exists, recalculate with new conditions
```

---

## Graph Processing

### Graph Structure

```python
G = nx.MultiDiGraph()

# Node attributes
node = {
    'y': latitude,
    'x': longitude,
    'osmid': node_id
}

# Edge attributes
edge = {
    'length': distance_meters,
    'highway': road_type,
    'maxspeed': speed_limit,
    'safety_weight': danger_score,
    'dynamic_weight': adjusted_score,
    'geometry': LineString,
    'bridge': boolean,
    'tunnel': boolean
}
```

### Edge Weight Computation

```python
# Base weight from ML model
base_weight = predict_danger(
    road_features,
    hazard_counts,
    historical_crashes
)

# Apply live conditions
dynamic_weight = base_weight * danger_multiplier

# Apply edge-specific factors
if is_bridge and rain > 2:
    dynamic_weight *= 1.4
if is_residential and is_night:
    dynamic_weight *= 1.25
if is_highway and wind > 30:
    dynamic_weight *= 1.2
```

### Graph Optimization

1. **Preprocessing:**
   - Remove non-driveable edges (footways, paths)
   - Keep only largest connected component
   - Precompute edge weights
   - Cache in JSON for fast loading

2. **Runtime:**
   - Load graph once at startup
   - Copy graph for dynamic weighting
   - Use A* with heuristic for efficiency

---

## Routing Algorithm

### A* Implementation

```python
def astar_path(G, source, target, weight='safety_weight'):
    """
    A* pathfinding with custom weight function
    
    Heuristic: Euclidean distance
    Weight: safety_weight or length
    """
    return nx.astar_path(G, source, target, weight=weight)
```

### Performance Optimization

1. **Node Snapping:**
   - Find nearest driveable node
   - Prefer nodes with preferred road types
   - Search within 30 nearest nodes

2. **Path Caching:**
   - Cache common routes
   - Invalidate on condition changes
   - TTL: 5 minutes

3. **Parallel Processing:**
   - Fetch live conditions in parallel
   - Calculate both routes concurrently (future)

### Algorithm Complexity

- **Time:** O(E log V) where E = edges, V = nodes
- **Space:** O(V) for visited nodes
- **Typical:** 200-500ms for 10km route

---

## Live Conditions Integration

### API Integration Architecture

```python
# Parallel execution with ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=4) as executor:
    weather_future = executor.submit(fetch_weather)
    traffic_future = executor.submit(fetch_traffic, route_coords)
    air_future = executor.submit(fetch_air_quality)
    sun_future = executor.submit(fetch_sunrise_sunset)
    
    # Wait for all to complete
    weather = weather_future.result()
    traffic = traffic_future.result()
    air = air_future.result()
    sun = sun_future.result()
```

### Fallback Strategy

```python
try:
    data = fetch_from_api()
except Exception:
    data = get_default_values()
    log_error()
```

### Caching Strategy

```python
# Cache live conditions for 5 minutes
cache_key = "live_conditions"
cache_ttl = 300  # seconds

if cache.exists(cache_key) and not cache.expired(cache_key):
    return cache.get(cache_key)
else:
    data = fetch_all_live_conditions()
    cache.set(cache_key, data, ttl=cache_ttl)
    return data
```

---

## Frontend Architecture

### Component Hierarchy

```
App
├── MapPage
│   ├── Mapbox Map
│   ├── RouteStatsPanel
│   │   └── AI Proof Modal
│   ├── Origin Marker
│   ├── Destination Marker
│   ├── Route Layers (safe, fast)
│   └── Hazard Markers
└── (Future: Header, Sidebar, Settings)
```

### State Management

```javascript
// Global state (future: Redux/Context)
const AppState = {
  map: mapboxgl.Map,
  origin: { lat, lng },
  destination: { lat, lng },
  routeData: {
    safe_route: {...},
    fast_route: {...},
    safety_improvement: {...}
  },
  liveConditions: {...},
  loading: boolean,
  error: string | null
}
```

### Map Layers

```javascript
// Route layers
map.addLayer({
  id: 'safe-route',
  type: 'line',
  source: 'safe-route-source',
  paint: {
    'line-color': '#00e676',
    'line-width': 4
  }
});

// Hazard markers
map.addLayer({
  id: 'hazards',
  type: 'circle',
  source: 'hazards-source',
  paint: {
    'circle-radius': 6,
    'circle-color': [
      'case',
      ['>', ['get', 'danger_probability'], 0.5], '#ff5252',
      ['>', ['get', 'danger_probability'], 0.3], '#ff9800',
      '#ffc107'
    ]
  }
});
```

---

## Database Schema

### Current: File-based Storage

```
panvel_weighted_graph.graphml    # Graph structure
edge_features_enriched.csv       # Edge features
edge_weights_cache.json          # Precomputed weights
danger_model.json                # ML model config
```

### Future: PostgreSQL Schema

```sql
-- Nodes table
CREATE TABLE nodes (
    id BIGINT PRIMARY KEY,
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    osmid BIGINT
);

-- Edges table
CREATE TABLE edges (
    id SERIAL PRIMARY KEY,
    u BIGINT REFERENCES nodes(id),
    v BIGINT REFERENCES nodes(id),
    length DOUBLE PRECISION,
    highway VARCHAR(50),
    maxspeed DOUBLE PRECISION,
    safety_weight DOUBLE PRECISION,
    geometry GEOMETRY(LineString, 4326)
);

-- Hazards table
CREATE TABLE hazards (
    id SERIAL PRIMARY KEY,
    edge_id INTEGER REFERENCES edges(id),
    type VARCHAR(20),  -- pothole, crash, blackspot
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    severity DOUBLE PRECISION,
    reported_at TIMESTAMP,
    verified BOOLEAN
);

-- Routes cache
CREATE TABLE route_cache (
    id SERIAL PRIMARY KEY,
    origin_node BIGINT,
    dest_node BIGINT,
    mode VARCHAR(10),
    path JSONB,
    conditions_hash VARCHAR(64),
    created_at TIMESTAMP,
    expires_at TIMESTAMP
);
```

---

## Scalability Considerations

### Horizontal Scaling

1. **Backend:**
   - Stateless API servers
   - Load balancer (Railway/Nginx)
   - Shared graph data via Redis

2. **Frontend:**
   - CDN for static assets (Vercel)
   - Edge caching
   - Service workers for offline

### Vertical Scaling

1. **Graph Loading:**
   - Lazy load graph sections
   - Partition by geographic area
   - Use graph database (Neo4j)

2. **Caching:**
   - Redis for live conditions
   - Route cache with TTL
   - Edge weight cache

### Performance Targets

- API response time: < 500ms (p95)
- Route calculation: < 300ms
- Live conditions fetch: < 2s
- Frontend load time: < 2s
- Map interaction: 60 FPS

---

## Security

### API Security

1. **Input Validation:**
   ```python
   def validate_coordinates(lat, lng):
       if not (-90 <= lat <= 90):
           raise ValueError("Invalid latitude")
       if not (-180 <= lng <= 180):
           raise ValueError("Invalid longitude")
   ```

2. **Rate Limiting:**
   ```python
   from slowapi import Limiter
   
   limiter = Limiter(key_func=get_remote_address)
   
   @app.get("/api/route-comparison")
   @limiter.limit("100/minute")
   async def compare_routes(...):
       ...
   ```

3. **CORS Configuration:**
   ```python
   allow_origins=[
       "https://argusai.vercel.app",
       "http://localhost:3000"
   ]
   ```

### Data Security

1. **Environment Variables:**
   - Never commit `.env` files
   - Use secrets management (Railway/Vercel)
   - Rotate API keys regularly

2. **HTTPS Only:**
   - Enforce HTTPS in production
   - HSTS headers
   - Secure cookies

3. **SQL Injection Prevention:**
   - Use parameterized queries
   - ORM (SQLAlchemy)
   - Input sanitization

---

## Monitoring & Logging

### Logging Strategy

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Route calculated: {origin} -> {dest}")
logger.warning(f"API call failed: {api_name}")
logger.error(f"Graph loading error: {error}")
```

### Metrics to Track

- Request count by endpoint
- Response times (p50, p95, p99)
- Error rates
- Cache hit rates
- External API latency
- Graph loading time

---

## Future Enhancements

1. **Real-time Updates:**
   - WebSocket for live rerouting
   - Push notifications for hazards

2. **Machine Learning:**
   - Online learning for danger prediction
   - User feedback integration
   - Traffic prediction

3. **Multi-modal Routing:**
   - Walking + transit
   - Bike routes
   - EV charging stations

4. **Social Features:**
   - User-reported hazards
   - Route sharing
   - Community safety ratings

---

**Last Updated:** 2026-04-14  
**Version:** 1.0.0
