import os
import json
import requests
import numpy as np
import pandas as pd
import osmnx as ox
from datetime import datetime
from tqdm import tqdm

try:
    import xgboost as xgb
except ImportError:
    xgb = None

# ── Config ──────────────────────────────────────────────────────────
GRAPH_FILE = 'data_files/pune_graph.graphml'
EDGE_CSV = 'data_files/pune_edges_features_enriched.csv'
JUNCTION_FILE = 'data_files/junction_types.json'
DEAD_END_FILE = 'data_files/dead_end_nodes.json'
MODEL_FILE = 'data_files/danger_model.json'
FEATURES_FILE = 'data_files/model_features.json'
OUTPUT_GRAPH = '../data_files/pune_weighted_graph.graphml'
WEIGHTS_CACHE = 'data_files/edge_weights_cache.json'


def main():
    print("=" * 60)
    print("  COMPUTE EDGE WEIGHTS")
    print("=" * 60)

    # ── SETUP ──────────────────────────────────────────────────────────
    print("\n[>>] Loading graph...")
    G = ox.load_graphml(GRAPH_FILE)
    print(f"  [OK] Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    print(f"\n[>>] Loading edge features from '{EDGE_CSV}'...")
    df = pd.read_csv(EDGE_CSV)
    print(f"  [OK] Loaded {len(df)} edges")

    print(f"\n[>>] Loading model from '{MODEL_FILE}'...")
    if xgb is None:
        print("[ERROR] xgboost not installed. Run 'pip install xgboost'.")
        return
    model = xgb.XGBClassifier()
    model.load_model(MODEL_FILE)
    print("  [OK] Model loaded")

    print(f"\n[>>] Loading feature order from '{FEATURES_FILE}'...")
    with open(FEATURES_FILE, 'r') as f:
        feature_config = json.load(f)

    # Handle both dict and list formats
    if isinstance(feature_config, dict):
        feature_columns = feature_config.get('feature_columns', [])
    elif isinstance(feature_config, list):
        feature_columns = feature_config
    else:
        feature_columns = []

    if not feature_columns:
        # Fallback to default order if not in JSON
        feature_columns = [
            "highway_encoded", "maxspeed", "lanes", "oneway_encoded", "surface_encoded",
            "is_dead_end", "junction_complexity", "length", "bridge_encoded", "tunnel_encoded",
            "pothole_count", "crash_count", "cluster_present", "blackspot_present",
            "hour_of_day", "day_of_week", "is_rush_hour", "is_night",
            "precipitation_mm", "visibility_km", "windspeed_kmh"
        ]
    print(f"  [OK] Features: {len(feature_columns)} columns")

    # ── Load Junction and Dead End Data ──────────────────────────────
    print(f"\n[>>] Loading junction data from '{JUNCTION_FILE}'...")
    try:
        with open(JUNCTION_FILE, 'r') as f:
            j_types = json.load(f)
    except FileNotFoundError:
        print(f"  [WARNING] {JUNCTION_FILE} missing, using simple junctions")
        j_types = {}

    print(f"\n[>>] Loading dead end data from '{DEAD_END_FILE}'...")
    try:
        with open(DEAD_END_FILE, 'r') as f:
            dead_ends = set([str(n) for n in json.load(f)])
    except FileNotFoundError:
        print(f"  [WARNING] {DEAD_END_FILE} missing, assuming no dead ends")
        dead_ends = set()

    # ── Fetch Live Weather ────────────────────────────────────────────
    print("\n[>>] Fetching live weather from Open-Meteo...")
    weather_url = "https://api.open-meteo.com/v1/forecast?latitude=18.5308&longitude=73.8475&current=precipitation,visibility,windspeed_10m"

    precip_mm = 0.0
    vis_km = 10.0
    wind_kmh = 0.0

    try:
        r = requests.get(weather_url, timeout=10)
        if r.status_code == 200:
            current = r.json().get('current', {})
            precip_mm = float(current.get('precipitation', 0.0))
            vis_metric = float(current.get('visibility', 10000))
            if vis_metric > 200:
                vis_km = vis_metric / 1000.0
            else:
                vis_km = vis_metric
            wind_kmh = float(current.get('windspeed_10m', 0.0))
            print(f"  [OK] Weather: {precip_mm}mm rain, {vis_km:.1f}km vis, {wind_kmh:.1f}km/h wind")
        else:
            print(f"  [WARNING] API returned {r.status_code}, using defaults")
    except Exception as e:
        print(f"  [WARNING] Weather fetch failed: {e}, using defaults")

    # ── PART 1: Build Inference Feature Matrix ───────────────────────
    print("\n[>>] PART 1: Building inference feature matrix...")

    now = datetime.now()
    hour = now.hour
    dow = now.weekday()
    is_rush = 1 if hour in [8, 9, 10, 17, 18, 19, 20] else 0
    is_night = 1 if (hour < 6 or hour > 21) else 0

    # Highway encoding map
    highway_map = {
        'living_street': 1, 'unclassified': 2, 'residential': 3, 'tertiary_link': 4,
        'tertiary': 5, 'secondary_link': 6, 'secondary': 7, 'primary_link': 8,
        'primary': 9, 'trunk_link': 10, 'trunk': 11, 'motorway_link': 12, 'motorway': 13
    }

    # Surface encoding
    def encode_surface(s):
        s = str(s).lower()
        if s in ['paved', 'asphalt', 'concrete']:
            return 0
        if s in ['unpaved', 'gravel', 'dirt', 'mud']:
            return 2
        return 1

    # Bool encoding
    def encode_bool(b):
        b = str(b).lower()
        return 1 if b in ['true', 'yes', '1'] else 0

    # Junction encoding
    j_map = {'dead_end': 0, 'simple': 1, 't_junction': 2, 'complex': 3}

    # Build features for all edges
    feature_rows = []
    edge_ids = []  # (u, v, key) for each row

    for _, row in tqdm(df.iterrows(), total=len(df), desc="  Building features", ncols=80):
        u, v, key = str(row['u']), str(row['v']), str(row.get('key', 0))
        edge_ids.append((u, v, key))

        # Highway encoded
        highway = str(row.get('highway', 'unclassified'))
        highway_encoded = highway_map.get(highway, 2)

        # Surface encoded
        surface_encoded = encode_surface(row.get('surface', 'unknown'))

        # Bool features
        oneway_encoded = encode_bool(row.get('oneway', 'false'))
        bridge_encoded = encode_bool(row.get('bridge', 'false'))
        tunnel_encoded = encode_bool(row.get('tunnel', 'false'))

        # Dead end flag
        is_dead_end = 1 if str(row.get('v', '')) in dead_ends else 0

        # Junction complexity
        junc_label = j_types.get(str(row.get('u', '')), 'simple')
        junction_complexity = j_map.get(junc_label, 1)

        # Numeric features with defaults
        maxspeed = float(row.get('maxspeed', 30)) if pd.notna(row.get('maxspeed')) else 30.0
        lanes = float(row.get('lanes', 1)) if pd.notna(row.get('lanes')) else 1.0
        length = float(row.get('length', 0)) if pd.notna(row.get('length')) else 0.0

        # Hazard counts
        pothole_count = int(row.get('pothole_count', 0)) if pd.notna(row.get('pothole_count')) else 0
        crash_count = int(row.get('crash_count', 0)) if pd.notna(row.get('crash_count')) else 0
        cluster_present = int(row.get('cluster_present', 0)) if pd.notna(row.get('cluster_present')) else 0
        blackspot_present = int(row.get('blackspot_present', 0)) if pd.notna(row.get('blackspot_present')) else 0

        feature_row = [
            highway_encoded,
            maxspeed,
            lanes,
            oneway_encoded,
            surface_encoded,
            is_dead_end,
            junction_complexity,
            length,
            bridge_encoded,
            tunnel_encoded,
            pothole_count,
            crash_count,
            cluster_present,
            blackspot_present,
            hour,
            dow,
            is_rush,
            is_night,
            precip_mm,
            vis_km,
            wind_kmh
        ]
        feature_rows.append(feature_row)

    X = np.array(feature_rows)
    print(f"  [OK] Feature matrix shape: {X.shape}")

    # ── PART 2: Run Model Inference ──────────────────────────────────
    print("\n[>>] PART 2: Running model inference (batch)...")
    danger_probs = model.predict_proba(X)[:, 1]
    print(f"  [OK] Predicted {len(danger_probs)} danger probabilities")
    print(f"       Range: {danger_probs.min():.3f} to {danger_probs.max():.3f}")

    # ── PART 3: Compute Final Edge Weights ─────────────────────────────
    print("\n[>>] PART 3: Computing final edge weights...")

    weights_cache = {}
    edge_danger = []  # Store for reporting

    for i, (u, v, key) in enumerate(edge_ids):
        row = df.iloc[i]

        # Get raw values
        length = float(row.get('length', 0)) if pd.notna(row.get('length')) else 0.0
        maxspeed = float(row.get('maxspeed', 30)) if pd.notna(row.get('maxspeed')) else 30.0
        highway = str(row.get('highway', 'unclassified'))
        v_node = str(row.get('v', ''))

        # Travel time (seconds) = length / (maxspeed * 0.2778)
        # 0.2778 converts km/h to m/s
        if maxspeed > 0:
            travel_time = length / (maxspeed * 0.2778)
        else:
            travel_time = length / (30.0 * 0.2778)  # Default to 30 km/h

        # Danger penalty
        danger_prob = danger_probs[i]
        danger_penalty = danger_prob * 1200.0

        # Dead end penalty
        is_dead_end = 1 if v_node in dead_ends else 0
        dead_end_penalty = 1200.0 if is_dead_end == 1 else 0.0

        # Construction penalty
        construction_penalty = 400.0 if highway == 'construction' else 0.0

        # Rain multiplier
        rain_multiplier = 1.0 + (precip_mm * 0.15)

        # Final weight
        base_weight = travel_time + danger_penalty + dead_end_penalty + construction_penalty
        final_weight = base_weight * rain_multiplier

        # Store for cache (convert to Python float for JSON serialization)
        cache_key = f"{u}_{v}_{key}"
        weights_cache[cache_key] = float(final_weight)

        # Store for top dangerous report
        edge_danger.append({
            'u': u,
            'v': v,
            'key': key,
            'highway': highway,
            'danger_prob': danger_prob,
            'travel_time': travel_time,
            'final_weight': final_weight
        })

    print(f"  [OK] Computed {len(weights_cache)} edge weights")

    # ── PART 3.5: Save danger_probability to CSV and Database ────────
    print("\n[>>] PART 3.5: Saving danger_probability to edge_features_enriched.csv...")

    # Add danger_probability column to DataFrame
    df['danger_probability'] = danger_probs

    # Save updated CSV
    df.to_csv(EDGE_CSV, index=False)
    print("  danger_probability column saved to edge_features_enriched.csv ✓")

    # Update SQLite database if it exists
    try:
        import sqlite3
        db_path = 'road_features.db'
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check if danger_probability column exists
            cursor.execute("PRAGMA table_info(edges)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'danger_probability' not in columns:
                cursor.execute("ALTER TABLE edges ADD COLUMN danger_probability REAL")
                print("  Added danger_probability column to edges table")

            # Update each edge with its danger probability
            for i, row in df.iterrows():
                u_val = row['u']
                v_val = row['v']
                prob = float(row['danger_probability'])
                cursor.execute(
                    "UPDATE edges SET danger_probability = ? WHERE u = ? AND v = ?",
                    (prob, u_val, v_val)
                )

            conn.commit()
            conn.close()
            print("  danger_probability saved to road_features.db ✓")
    except Exception as e:
        print(f"  [WARNING] Could not update database: {e}")

    # ── PART 4: Apply Weights to Graph ───────────────────────────────
    print("\n[>>] PART 4: Applying weights to graph...")

    # Count edges updated vs not found
    updated = 0
    not_found = 0
    default_weights = 0

    for u, v, key in tqdm(G.edges(keys=True), total=G.number_of_edges(), desc="  Applying weights", ncols=80):
        u_str, v_str, key_str = str(u), str(v), str(key)
        cache_key = f"{u_str}_{v_str}_{key_str}"

        if cache_key in weights_cache:
            G[u][v][key]['safety_weight'] = weights_cache[cache_key]
            updated += 1
        else:
            # Set default weight (travel time only)
            edge_data = G[u][v][key]
            length = edge_data.get('length', 0)
            maxspeed = 30.0  # Default speed
            if length:
                travel_time = float(length) / (maxspeed * 0.2778)
            else:
                travel_time = 0.0
            G[u][v][key]['safety_weight'] = travel_time
            default_weights += 1
            not_found += 1

    print(f"  [OK] Updated {updated} edges with computed weights")
    if default_weights > 0:
        print(f"  [INFO] Set {default_weights} edges to default travel-time weights")

    # ── PART 5: Save Outputs ───────────────────────────────────────────
    print("\n[>>] PART 5: Saving outputs...")

    # Save weighted graph
    ox.save_graphml(G, OUTPUT_GRAPH)
    print(f"  [OK] Saved weighted graph to '{OUTPUT_GRAPH}'")

    # Save weights cache
    with open(WEIGHTS_CACHE, 'w') as f:
        json.dump(weights_cache, f, indent=2)
    print(f"  [OK] Saved weights cache to '{WEIGHTS_CACHE}'")

    # ── SUMMARY ──────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)

    print(f"\n  Weather conditions used:")
    print(f"    - Precipitation: {precip_mm} mm")
    print(f"    - Visibility: {vis_km:.1f} km")
    print(f"    - Wind speed: {wind_kmh:.1f} km/h")
    print(f"    - Rain multiplier: {1.0 + (precip_mm * 0.15):.2f}x")

    all_weights = list(weights_cache.values())
    print(f"\n  Edge weight statistics:")
    print(f"    - Min: {min(all_weights):.1f} seconds")
    print(f"    - Max: {max(all_weights):.1f} seconds")
    print(f"    - Mean: {np.mean(all_weights):.1f} seconds")
    print(f"    - Median: {np.median(all_weights):.1f} seconds")

    # Top 10 most dangerous edges
    print(f"\n  Top 10 most dangerous edges (by danger_probability):")
    top_danger = sorted(edge_danger, key=lambda x: x['danger_prob'], reverse=True)[:10]
    print("  " + "-" * 56)
    print(f"  {'Rank':<5} {'Edge (u_v_key)':<25} {'Danger %':<12} {'Weight (s)':<12}")
    print("  " + "-" * 56)
    for rank, ed in enumerate(top_danger, 1):
        edge_key = f"{ed['u']}_{ed['v']}_{ed['key']}"
        print(f"  {rank:<5} {edge_key:<25} {ed['danger_prob']*100:>6.1f}%      {ed['final_weight']:>8.1f}")

    print("\n" + "=" * 60)
    print("  Edge weights computed and cached successfully ✓")
    print("=" * 60)


if __name__ == "__main__":
    main()
