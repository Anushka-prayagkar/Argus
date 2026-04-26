# 🛡️ ArgusAI - Safe Route Intelligence System

> AI-powered route optimization system that prioritizes safety over speed using real-time hazard detection, live conditions, and intelligent pathfinding.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.0+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

ArgusAI is an intelligent routing system designed for the Panvel-Vashi corridor that calculates the safest route between two points by analyzing:

- **Road hazards** (potholes, crash sites, blackspots)
- **Live weather conditions** (rain, visibility, wind)
- **Real-time traffic** (congestion, delays)
- **Environmental factors** (air quality, time of day)
- **Road characteristics** (surface quality, lighting, width)

Unlike traditional navigation systems that optimize for speed or distance, ArgusAI prioritizes rider safety while providing transparent AI decision-making through performance metrics.

---

## ✨ Key Features

### 🧠 Intelligent Route Planning
- **Dual-mode routing:** Compare safe route vs. fast route
- **A* pathfinding** with custom safety-weighted edges
- **Dynamic weight adjustment** based on live conditions
- **Hazard avoidance** with configurable penalties

### 🌦️ Live Conditions Integration
- **Weather data** from Open-Meteo (temperature, precipitation, wind, visibility)
- **Air quality** monitoring (PM2.5, PM10, AQI, haze detection)
- **Traffic flow** from TomTom API (congestion levels, delays)
- **Sunrise/sunset** tracking for night visibility adjustments

### 🗺️ Interactive Map Interface
- **3D visualization** with Mapbox GL JS
- **Real-time hazard markers** (potholes, crashes, blackspots)
- **Route comparison** with color-coded danger levels
- **Live condition display** with safety warnings
- **Google Maps integration** for turn-by-turn navigation

### 📊 AI Transparency
- **Performance proof modal** showing:
  - Nodes analyzed by A* algorithm
  - Search time and path weight
  - ML model predictions
  - Dynamic penalties applied
- **Safety metrics:**
  - Danger reduction percentage
  - Hazards avoided
  - Extra distance/time trade-off

### 🔄 Real-time Updates
- **Automatic condition refresh** every 5 minutes
- **Dynamic route recalculation** based on conditions
- **Live danger multiplier** (1.0x - 2.5x)
- **Contextual safety warnings**

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Map View    │  │ Route Stats  │  │ AI Proof     │      │
│  │  (Mapbox)    │  │  Panel       │  │  Modal       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Route API    │  │ Live         │  │ Graph        │      │
│  │ Endpoints    │  │ Conditions   │  │ Engine       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Open-Meteo   │  │   TomTom     │  │  OSM Graph   │
│  Weather     │  │   Traffic    │  │   + ML       │
│   + AQ       │  │     API      │  │  Features    │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Data Flow

1. **User Input:** Origin and destination coordinates
2. **Graph Loading:** OSM road network with enriched features
3. **Live Conditions:** Parallel API calls to weather, traffic, AQ services
4. **Dynamic Weighting:** Apply condition multipliers to edge weights
5. **A* Pathfinding:** Calculate safe and fast routes
6. **Metrics Calculation:** Analyze hazards, distance, time, danger scores
7. **Response:** GeoJSON routes + performance proof + live conditions
8. **Visualization:** Render routes on map with hazard markers

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **OSMnx** - OpenStreetMap graph processing
- **NetworkX** - Graph algorithms (A* pathfinding)
- **Pandas** - Data manipulation
- **Requests** - HTTP client for external APIs
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI framework
- **Mapbox GL JS** - Interactive maps
- **Axios** - HTTP client
- **CSS3** - Styling with animations

### Data Sources
- **OpenStreetMap** - Road network data
- **Open-Meteo** - Weather and air quality
- **TomTom Traffic API** - Real-time traffic
- **Sunrise-Sunset.org** - Day/night detection
- **Custom ML Model** - Danger prediction

### Deployment
- **Railway** - Backend hosting
- **Vercel** - Frontend hosting
- **GitHub** - Version control

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Git
- TomTom API key (free tier)
- Mapbox token (optional, for frontend)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/argusai.git
cd argusai
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your TOMTOM_API_KEY

# Run backend
uvicorn route_api:app --reload --port 8001
```

Backend will be available at `http://localhost:8001`

### 3. Frontend Setup

```bash
# Navigate to frontend (in new terminal)
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# Edit .env and add:
# REACT_APP_API_URL=http://localhost:8001
# REACT_APP_MAPBOX_TOKEN=your_token_here

# Run frontend
npm start
```

Frontend will open at `http://localhost:3000`

### 4. Test the System

1. Open `http://localhost:3000`
2. Click on the map to set origin
3. Click again to set destination
4. Click "FIND SAFE ROUTE"
5. Review route comparison
6. Click "View Core AI Routing Proof" to see performance metrics

Use coordinates from `TEST_ROUTES.md` for testing.

---

## 📁 Project Structure

```
argusai/
├── backend/                      # FastAPI backend
│   ├── route_api.py             # Main API routes
│   ├── database.py              # Database models
│   ├── requirements.txt         # Python dependencies
│   ├── Procfile                 # Railway deployment
│   ├── railway.json             # Railway config
│   └── utils/                   # Utility modules
│
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── MapPage.jsx     # Main map interface
│   │   │   └── RouteStatsPanel.jsx  # Route comparison
│   │   ├── pages/              # Page components
│   │   ├── App.jsx             # Main app
│   │   └── index.js            # Entry point
│   ├── public/                 # Static assets
│   └── package.json            # Node dependencies
│
├── scripts/                     # Data processing
│   ├── A1_download_graph.py    # Download OSM graph
│   ├── A2_extract_features.py  # Extract road features
│   ├── A3_seed_demo_data.py    # Generate demo hazards
│   ├── A4_map_hazards_to_edges.py  # Map hazards to edges
│   ├── A5_build_training_dataset.py  # Create training data
│   ├── A6_train_danger_model.py  # Train ML model
│   └── A7_compute_weights.py   # Compute edge weights
│
├── docs/                        # Documentation
│   ├── DEPLOYMENT_GUIDE.md     # Deployment instructions
│   ├── TEST_ROUTES.md          # Test coordinates
│   └── API.md                  # API documentation
│
├── panvel_weighted_graph.graphml  # Road network graph
├── edge_features_enriched.csv     # Edge features
├── edge_weights_cache.json        # Precomputed weights
├── danger_model.json              # ML model config
├── .gitignore                     # Git exclusions
└── README.md                      # This file
```

---

## 📡 API Documentation

### Base URL
```
Production: https://your-app.railway.app
Development: http://localhost:8001
```

### Endpoints

#### 1. Get Live Conditions
```http
GET /api/live-conditions
```

**Response:**
```json
{
  "conditions": {
    "weather": {
      "temperature_c": 28.5,
      "precipitation_mm": 0.0,
      "windspeed_kmh": 12.3,
      "visibility_km": 10.0
    },
    "traffic": {
      "congestion_level": "FREE_FLOW",
      "avg_speed_kmh": 45.2
    },
    "air_quality": {
      "aqi": 65,
      "aqi_level": "MODERATE"
    },
    "sun": {
      "is_night": false,
      "sunrise": "06:30 IST",
      "sunset": "18:45 IST"
    }
  },
  "danger_multiplier": 1.15,
  "warnings": ["Moderate traffic expected"]
}
```

#### 2. Compare Routes
```http
GET /api/route-comparison?origin_lat=18.9894&origin_lng=73.1175&dest_lat=19.0771&dest_lng=72.9988
```

**Response:**
```json
{
  "status": "ok",
  "safe_route": {
    "distance_km": 9.82,
    "time_min": 18.2,
    "avg_danger": 0.156,
    "hazard_count": 7,
    "geojson": {...}
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
      "ml_model_prediction": "ArgusVision-DeepRoute v3.1"
    }
  },
  "live_conditions": {...},
  "danger_multiplier": 1.15
}
```

#### 3. Get Single Route
```http
GET /api/safe-route?origin_lat=18.9894&origin_lng=73.1175&dest_lat=19.0220&dest_lng=73.0297&mode=safe
```

**Parameters:**
- `mode`: `safe` or `fast`

**Response:** Similar to route comparison but single route only

---

## 🚀 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

### Quick Deploy

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy ArgusAI"
   git push origin main
   ```

2. **Deploy Backend (Railway):**
   - Connect GitHub repo
   - Add `TOMTOM_API_KEY` environment variable
   - Deploy automatically

3. **Deploy Frontend (Vercel):**
   - Connect GitHub repo
   - Set root directory to `frontend`
   - Add `REACT_APP_API_URL` environment variable
   - Deploy automatically

---

## 🧪 Testing

### Test Routes

Use coordinates from `TEST_ROUTES.md`:

```bash
# Short route (5-10 km)
Origin: 18.9894, 73.1175
Destination: 19.0220, 73.0297

# Medium route (10-15 km)
Origin: 18.9750, 73.1200
Destination: 19.0650, 73.0200

# Long route (15+ km)
Origin: 18.9700, 73.1150
Destination: 19.0771, 72.9988
```

### API Testing

```bash
# Test live conditions
curl http://localhost:8001/api/live-conditions

# Test route comparison
curl "http://localhost:8001/api/route-comparison?origin_lat=18.9894&origin_lng=73.1175&dest_lat=19.0771&dest_lng=72.9988"
```

### Frontend Testing

1. Open browser console
2. Check for errors
3. Test all features:
   - Route finding
   - Safe vs Fast comparison
   - AI Proof modal
   - Google Maps navigation
   - Live conditions display

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write descriptive commit messages
- Add tests for new features
- Update documentation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenStreetMap** for road network data
- **Open-Meteo** for free weather and air quality APIs
- **TomTom** for traffic data
- **Mapbox** for mapping platform
- **FastAPI** and **React** communities

---

## 📞 Contact

- **Project Link:** https://github.com/yourusername/argusai
- **Issues:** https://github.com/yourusername/argusai/issues
- **Documentation:** https://github.com/yourusername/argusai/wiki

---

## 🗺️ Roadmap

- [ ] Multi-city support
- [ ] Mobile app (React Native)
- [ ] Offline mode
- [ ] User-reported hazards
- [ ] Historical route analysis
- [ ] Integration with ride-sharing apps
- [ ] Advanced ML models for danger prediction
- [ ] Real-time rerouting during navigation

---

**Made with ❤️ for safer roads**

**Last Updated:** 2026-04-14  
**Version:** 1.0.0
