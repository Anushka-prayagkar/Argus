"""
A5_generate_synthetic_road_data.py
──────────────────────────────────
Generates synthetic data for  crashes · cluster_alerts · blackspots
and inserts them into the Supabase tables.

★  Every generated coordinate is STRICTLY on a road segment.
   We load the Pune road graph, convert edges to GeoDataFrame,
   and use Shapely interpolation to sample lat/lng from real
   road geometries — no random land points.

Usage:
    python scripts/A5_generate_synthetic_road_data.py
"""

import os
import random
from datetime import datetime, timedelta
from collections import Counter

import osmnx as ox
import numpy as np
from shapely.geometry import LineString
from dotenv import load_dotenv

try:
    from supabase import create_client
except ImportError:
    create_client = None

# ── Config ──────────────────────────────────────────────────────────
GRAPH_FILE = "data_files/pune_graph.graphml"

# Pune centre & radius (same as A1_download_graph.py)
CENTER = (18.5308, 73.8475)
RADIUS_M = 15_000

# Record counts
N_CRASHES         = 150
N_CLUSTER_ALERTS  = 40
N_BLACKSPOTS      = 25

# ── High-accident road types (weighted sampling) ────────────────────
# Major roads are more accident-prone; we bias sampling towards them.
HIGHWAY_WEIGHTS = {
    "primary":         8,
    "primary_link":    6,
    "secondary":       7,
    "secondary_link":  5,
    "tertiary":        5,
    "tertiary_link":   4,
    "trunk":           9,
    "trunk_link":      7,
    "motorway":        6,
    "motorway_link":   5,
    "residential":     3,
    "unclassified":    2,
    "living_street":   1,
    "service":         1,
}
DEFAULT_WEIGHT = 2

# ── Blackspot metadata pools ───────────────────────────────────────
BLACKSPOT_REASONS = [
    "Sharp curve with no warning signs",
    "Uncontrolled intersection — high pedestrian volume",
    "Narrow bridge with no median divider",
    "Poor visibility due to blind turn",
    "High-speed corridor with frequent lane merges",
    "Missing streetlights on 4-lane road",
    "School zone with no speed calming measures",
    "Waterlogging-prone stretch during monsoon",
    "Frequent wrong-way driving near flyover exit",
    "Steep gradient with loose gravel shoulder",
    "Unmarked speed breakers on highway",
    "Heavy truck mixing with two-wheeler traffic",
    "Narrow underpass with poor drainage",
    "Construction zone without proper barriers",
    "Frequent U-turns on undivided road",
]

PUNE_ZONE_NAMES = [
    "Shivajinagar", "Kothrud", "Hadapsar", "Kharadi", "Hinjewadi",
    "Baner", "Wakad", "Pimpri", "Chinchwad", "Aundh",
    "Katraj", "Kondhwa", "Viman Nagar", "Yerwada", "Magarpatta",
    "Swargate", "Deccan", "Model Colony", "Pashan", "SB Road",
    "Pune Station", "Koregaon Park", "Camp", "Wanowrie", "Bibwewadi",
]


# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════

def random_date(days_back=180):
    """Random datetime within the last `days_back` days."""
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    return (datetime.now() - delta).isoformat()


def _first(val):
    """If val is a list, return the first element."""
    if isinstance(val, list):
        return val[0] if val else None
    return val


def sample_point_on_edge(geom):
    """
    Given a Shapely LineString, pick a uniformly random point along it.
    Returns (lat, lng) — note: Shapely uses (x=lng, y=lat).
    """
    if geom is None or geom.is_empty:
        return None
    frac = random.random()
    pt = geom.interpolate(frac, normalized=True)
    return (round(pt.y, 7), round(pt.x, 7))   # (lat, lng)


def build_edge_pool(G):
    """
    Convert the graph to a GeoDataFrame of edges and build a
    weighted sampling pool biased towards major road types.

    Returns: list[ (geometry, highway_type, road_name) ]  +  weights
    """
    _, edges_gdf = ox.graph_to_gdfs(G)

    pool = []
    weights = []

    for _, row in edges_gdf.iterrows():
        geom = row.get("geometry")
        if geom is None or geom.is_empty:
            continue
        if not isinstance(geom, LineString):
            continue

        hw = _first(row.get("highway", "unclassified")) or "unclassified"
        name = _first(row.get("name")) or "Unnamed Road"

        w = HIGHWAY_WEIGHTS.get(hw, DEFAULT_WEIGHT)
        pool.append((geom, hw, name))
        weights.append(w)

    return pool, weights


# ═══════════════════════════════════════════════════════════════════
#  GENERATORS
# ═══════════════════════════════════════════════════════════════════

def generate_crashes(pool, weights, n):
    """
    crashes table:  device_id, sms_sent, lat, lng, created_at
    """
    device_ids = [f"argus-v{i}" for i in range(1, 16)]
    records = []

    edges = random.choices(pool, weights=weights, k=n)

    for geom, hw, name in edges:
        pt = sample_point_on_edge(geom)
        if pt is None:
            continue
        lat, lng = pt
        records.append({
            "device_id":  random.choice(device_ids),
            "sms_sent":   random.choice([True, False]),
            "lat":        lat,
            "lng":        lng,
            "created_at": random_date(days_back=180),
        })

    return records


def generate_cluster_alerts(pool, weights, n):
    """
    cluster_alerts table:  lat, lng, severity, created_at

    Clusters are groups of incidents — so we pick a road segment,
    then place a small cluster of 1-4 nearby points on the same edge.
    """
    severities = ["low", "medium", "high", "critical"]
    severity_weights = [15, 35, 35, 15]

    records = []

    while len(records) < n:
        # Pick a road edge and place a small cluster on it
        edge = random.choices(pool, weights=weights, k=1)[0]
        geom, hw, name = edge
        cluster_size = random.randint(2, 5)
        sev = random.choices(severities, weights=severity_weights, k=1)[0]

        for _ in range(cluster_size):
            if len(records) >= n:
                break
            pt = sample_point_on_edge(geom)
            if pt is None:
                continue
            lat, lng = pt
            records.append({
                "lat":        lat,
                "lng":        lng,
                "severity":   sev,
                "created_at": random_date(days_back=120),
            })

    return records[:n]


def generate_blackspots(pool, weights, n):
    """
    blackspots table:  name, fatalities_3yr, reason, created_at, black_lon, black_lat

    Blackspots are placed on high-weight (major) road edges.
    We boost weights² so they're even more biased to major roads.
    """
    boosted = [w ** 2 for w in weights]
    edges = random.choices(pool, weights=boosted, k=n)

    used_names = set()
    records = []

    for geom, hw, road_name in edges:
        pt = sample_point_on_edge(geom)
        if pt is None:
            continue
        lat, lng = pt

        # Build a unique descriptive name
        zone = random.choice(PUNE_ZONE_NAMES)
        suffix = random.choice(["Junction", "Stretch", "Curve", "Crossing", "Flyover Exit"])
        candidate = f"{zone} {suffix}"
        # Ensure uniqueness
        attempt = 0
        while candidate in used_names and attempt < 10:
            zone = random.choice(PUNE_ZONE_NAMES)
            candidate = f"{zone} {suffix}"
            attempt += 1
        used_names.add(candidate)

        records.append({
            "name":           candidate,
            "fatalities_3yr": random.randint(1, 18),
            "reason":         random.choice(BLACKSPOT_REASONS),
            "created_at":     random_date(days_back=365),
            "black_lon":      lng,
            "black_lat":      lat,
        })

    return records


# ═══════════════════════════════════════════════════════════════════
#  SUPABASE  INSERT
# ═══════════════════════════════════════════════════════════════════

def get_supabase():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")

    if not url or not key:
        print("[ERROR] Missing SUPABASE_URL or SUPABASE_KEY in .env")
        return None
    if not create_client:
        print("[ERROR] supabase-py not installed.  pip install supabase")
        return None

    return create_client(url, key)


def upsert_batch(supabase, table, records, batch_size=50):
    """Insert records in batches. Returns total inserted count."""
    total = 0
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        try:
            res = supabase.table(table).insert(batch).execute()
            total += len(res.data) if hasattr(res, "data") and res.data else len(batch)
        except Exception as e:
            print(f"  [WARN] Batch {i // batch_size + 1} for '{table}' failed: {e}")
    return total


def delete_existing(supabase, tables):
    """Clear old data from the specified tables."""
    for table in tables:
        try:
            supabase.table(table).delete().neq("id", "").execute()
            print(f"  Cleared '{table}'")
        except Exception:
            try:
                supabase.table(table).delete().not_.is_("created_at", None).execute()
                print(f"  Cleared '{table}'")
            except Exception as e2:
                print(f"  [WARN] Could not clear '{table}': {e2}")


# ═══════════════════════════════════════════════════════════════════
#  PRETTY PRINT
# ═══════════════════════════════════════════════════════════════════

def print_summary(crashes, clusters, blackspots):
    print("\n" + "=" * 60)
    print("  GENERATION SUMMARY")
    print("=" * 60)

    print(f"\n  {'Table':<20} {'Count':>6}")
    print(f"  {'-' * 20} {'-' * 6}")
    print(f"  {'crashes':<20} {len(crashes):>6}")
    print(f"  {'cluster_alerts':<20} {len(clusters):>6}")
    print(f"  {'blackspots':<20} {len(blackspots):>6}")
    print(f"  {'-' * 20} {'-' * 6}")
    print(f"  {'TOTAL':<20} {len(crashes) + len(clusters) + len(blackspots):>6}")

    # Crash device distribution
    if crashes:
        dev_counts = Counter(r["device_id"] for r in crashes)
        print(f"\n  Crash device distribution (top 5):")
        for dev, cnt in dev_counts.most_common(5):
            bar = "#" * (cnt // 2)
            print(f"    {dev:<14} {cnt:>3}  {bar}")

    # Cluster severity distribution
    if clusters:
        sev_counts = Counter(r["severity"] for r in clusters)
        print(f"\n  Cluster severity distribution:")
        for sev in ["critical", "high", "medium", "low"]:
            cnt = sev_counts.get(sev, 0)
            bar = "#" * cnt
            print(f"    {sev:<10} {cnt:>3}  {bar}")

    # Blackspot fatality stats
    if blackspots:
        fats = [r["fatalities_3yr"] for r in blackspots]
        print(f"\n  Blackspot fatalities (3yr):")
        print(f"    min={min(fats)}  max={max(fats)}  "
              f"avg={sum(fats)/len(fats):.1f}  total={sum(fats)}")

    print("\n" + "=" * 60)


# ═══════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  Argus — Synthetic Road Data Generator")
    print(f"  Centre : {CENTER}  (Pune / Shivajinagar)")
    print(f"  Graph  : {GRAPH_FILE}")
    print(f"  Target : crashes={N_CRASHES}  clusters={N_CLUSTER_ALERTS}  "
          f"blackspots={N_BLACKSPOTS}")
    print("=" * 60)

    # ── Step 1: Load road network ───────────────────────────────────
    print(f"\n[1/5] Loading road graph from '{GRAPH_FILE}' ...")
    if not os.path.exists(GRAPH_FILE):
        print(f"[ERROR] Graph file not found: {GRAPH_FILE}")
        print("        Run A1_download_graph.py first.")
        return

    G = ox.load_graphml(GRAPH_FILE)
    print(f"[OK]  {G.number_of_nodes():,} nodes · {G.number_of_edges():,} edges")

    # ── Step 2: Build weighted edge pool ────────────────────────────
    print("\n[2/5] Building weighted edge pool (biased to major roads) ...")
    pool, weights = build_edge_pool(G)
    print(f"[OK]  {len(pool):,} edges with valid geometry")

    if len(pool) == 0:
        print("[ERROR] No edges with geometry found. Aborting.")
        return

    # ── Step 3: Generate synthetic records ──────────────────────────
    print("\n[3/5] Generating synthetic records ...")
    crashes  = generate_crashes(pool, weights, N_CRASHES)
    clusters = generate_cluster_alerts(pool, weights, N_CLUSTER_ALERTS)
    blacks   = generate_blackspots(pool, weights, N_BLACKSPOTS)

    print(f"  crashes        : {len(crashes)} records")
    print(f"  cluster_alerts : {len(clusters)} records")
    print(f"  blackspots     : {len(blacks)} records")

    print_summary(crashes, clusters, blacks)

    # ── Step 4: Connect to Supabase ─────────────────────────────────
    print("\n[4/5] Connecting to Supabase ...")
    supabase = get_supabase()
    if not supabase:
        print("[SKIP] Supabase not available. Records generated but NOT inserted.")
        return

    # Clear old data from these 3 tables
    print("\n  Clearing old data ...")
    delete_existing(supabase, ["crashes", "cluster_alerts", "blackspots"])

    # ── Step 5: Insert ──────────────────────────────────────────────
    print("\n[5/5] Inserting into Supabase ...")

    c1 = upsert_batch(supabase, "crashes", crashes)
    print(f"  crashes        : {c1} rows inserted")

    c2 = upsert_batch(supabase, "cluster_alerts", clusters)
    print(f"  cluster_alerts : {c2} rows inserted")

    c3 = upsert_batch(supabase, "blackspots", blacks)
    print(f"  blackspots     : {c3} rows inserted")

    print(f"\n{'=' * 60}")
    print(f"  ALL DONE — {c1 + c2 + c3} total rows inserted")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
