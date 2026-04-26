# ArgusAI - Organized Folder Structure

## 📁 Current Project Structure

```
argusai/
├── backend/                      # Backend API (FastAPI)
│   ├── route_api.py             # Main API routes (750 lines)
│   ├── database.py              # Database models
│   ├── requirements.txt         # Python dependencies
│   ├── Procfile                 # Railway deployment config
│   ├── railway.json             # Railway settings
│   ├── .env.example             # Environment template
│   ├── utils/                   # Utility modules
│   │   └── __init__.py
│   ├── ROUTE_API_README.md      # API documentation
│   └── SETUP_GUIDE.md           # Setup instructions
│
├── frontend/                     # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapPage.jsx      # Main map component
│   │   │   ├── MapPage.css
│   │   │   ├── RouteStatsPanel.jsx  # Route comparison panel
│   │   │   └── RouteStatsPanel.css
│   │   ├── App.jsx              # Main app
│   │   ├── App.css
│   │   └── index.js             # Entry point
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── package.json             # Node dependencies
│   ├── package-lock.json
│   ├── .env.example             # Environment template
│   ├── .gitignore
│   └── README.md
│
├── data_files/                   # Essential Data Files (Push to GitHub)
│   ├── panvel_weighted_graph.graphml    # Road network graph (~5MB)
│   ├── panvel_graph.graphml             # Original graph
│   ├── edge_features_enriched.csv       # Edge features (~2MB)
│   ├── edge_features.csv                # Original features
│   ├── edge_weights_cache.json          # Precomputed weights (~1MB)
│   ├── danger_model.json                # ML model config
│   ├── junction_types.json              # Junction data
│   ├── dead_end_nodes.json              # Dead end nodes
│   ├── model_features.json              # Model features
│   └── panvel_graph_preview.png         # Graph preview image
│
├── scripts/                      # Data Processing Scripts
│   ├── A1_download_graph.py     # Download OSM graph
│   ├── A2_extract_features.py   # Extract road features
│   ├── A3_seed_demo_data.py     # Generate demo hazards
│   ├── A4_map_hazards_to_edges.py   # Map hazards to edges
│   ├── A5_build_training_dataset.py # Create training data
│   ├── A6_train_danger_model.py     # Train ML model
│   └── A7_compute_weights.py        # Compute edge weights
│
├── docs/                         # Documentation
│   ├── API_DOCUMENTATION.md     # Complete API reference
│   ├── ARCHITECTURE.md          # System architecture
│   ├── DEPLOYMENT_GUIDE.md      # Deployment instructions
│   ├── QUICK_DEPLOY.md          # 5-minute quick start
│   ├── TEST_ROUTES.md           # Test coordinates
│   ├── GITHUB_PUSH_CHECKLIST.md # Pre-push checklist
│   ├── PROJECT_SUMMARY.md       # Project overview
│   ├── FINAL_DEPLOYMENT_SUMMARY.md  # Deployment summary
│   └── old_docs/                # Old documentation (archived)
│       ├── ARGUSAI_FULL_CONTEXT.md
│       ├── ArgusAI_Product_README.md
│       ├── DATABASE_SCHEMA.md
│       └── (other old docs)
│
├── cache/                        # ❌ DO NOT PUSH (211 JSON files, ~50MB)
├── data/                         # ❌ DO NOT PUSH (Training data, ~2GB)
│   ├── merged/
│   │   ├── test/                # 2134 test images
│   │   ├── train/               # Training images
│   │   └── valid/               # Validation images
│   └── raw_downloads/           # Raw data
│
├── runs/                         # ❌ DO NOT PUSH (Training runs, ~200MB)
├── Frontend_Add/                 # ❌ DO NOT PUSH (Duplicate frontend)
├── files/                        # ❌ DO NOT PUSH (Backup files)
├── model/                        # ❌ DO NOT PUSH (Empty folder)
│
├── .env                          # ❌ DO NOT PUSH (Contains secrets)
├── .env.example                  # ✅ Push (Template)
├── .gitignore                    # ✅ Push (Git exclusions)
├── README.md                     # ✅ Push (Main documentation)
├── FOLDER_STRUCTURE.md           # ✅ Push (This file)
│
├── road_features.db              # ❌ DO NOT PUSH (~50MB)
├── training_data.csv             # ❌ DO NOT PUSH (~10MB)
├── yolo26n.pt                    # ❌ DO NOT PUSH (YOLO weights, ~5MB)
└── yolov10n.pt                   # ❌ DO NOT PUSH (YOLO weights, ~5MB)
```

---

## 📊 Size Summary

### ✅ Files to Push (~20MB)
- Backend code: ~500KB
- Frontend code: ~2MB
- Data files: ~15MB
- Documentation: ~500KB
- Scripts: ~200KB

### ❌ Files to Exclude (~2.5GB)
- cache/: ~50MB
- data/merged/: ~2GB
- runs/: ~200MB
- *.pt files: ~10MB
- *.db files: ~50MB
- node_modules/: ~200MB (auto-excluded)
- build/: ~5MB (auto-excluded)

---

## 🎯 What Each Folder Contains

### `/backend` - Backend API
- FastAPI application
- Route calculation logic
- Live conditions integration
- Database models
- Deployment configs

### `/frontend` - React Frontend
- Map visualization
- Route comparison UI
- AI proof modal
- Live conditions display

### `/data_files` - Essential Data
- Graph files (road network)
- Edge features (ML predictions)
- Model configurations
- Precomputed weights

### `/scripts` - Data Pipeline
- Graph download and processing
- Feature extraction
- Hazard mapping
- Model training
- Weight computation

### `/docs` - Documentation
- API reference
- Architecture guide
- Deployment instructions
- Test routes
- Project summaries

### `/cache` - ❌ Excluded
- Temporary API response cache
- Not needed for deployment

### `/data` - ❌ Excluded
- Training images
- Raw downloads
- Too large for GitHub

### `/runs` - ❌ Excluded
- YOLO training artifacts
- Not needed for deployment

---

## 🚀 For Deployment

### Push to GitHub:
```bash
# These folders/files will be pushed:
✅ backend/
✅ frontend/
✅ data_files/
✅ scripts/
✅ docs/
✅ .gitignore
✅ .env.example
✅ README.md
✅ FOLDER_STRUCTURE.md
```

### Excluded by .gitignore:
```bash
# These will NOT be pushed:
❌ cache/
❌ data/merged/
❌ runs/
❌ Frontend_Add/
❌ files/
❌ model/
❌ .env
❌ *.pt
❌ *.db
❌ node_modules/
❌ __pycache__/
```

---

## 📝 Notes

1. **data_files/** contains only essential files needed for the app to run
2. **Large training data** is excluded - can be regenerated using scripts
3. **Model weights (.pt)** are excluded - too large for GitHub
4. **Old documentation** moved to docs/old_docs/ for reference
5. **Duplicate folders** (Frontend_Add, files) should be deleted before push

---

## 🧹 Cleanup Commands

Before pushing to GitHub, run:

```bash
# Remove duplicate folders
rm -rf Frontend_Add/
rm -rf files/
rm -rf model/

# Remove large data (optional - already in .gitignore)
rm -rf cache/
rm -rf data/merged/
rm -rf runs/
rm *.pt
rm *.db
rm training_data.csv

# Remove build artifacts
rm -rf frontend/build/
rm -rf frontend/node_modules/
rm -rf backend/__pycache__/
```

---

**Last Updated:** 2026-04-14  
**Total Size (with exclusions):** ~20MB  
**Total Size (without exclusions):** ~2.5GB
