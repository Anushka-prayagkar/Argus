"""
Generate and insert synthetic road hazard data directly into Supabase.
"""
import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
import osmnx as ox

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

try:
    from database import supabase
    print("✓ Successfully imported Supabase client")
except ImportError as e:
    print(f"✗ Failed to import Supabase client: {e}")
    print("Make sure you're running from the project root and backend/database.py exists")
    sys.exit(1)

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent
GRAPH_FILE = BASE_DIR / "data_files" / "pune_graph.graphml"

# Hazard distribution (total 250)
HAZARD_DISTRIBUTION = {
    "pothole": 120,      # 48% - Major contributor
    "road_crack": 80,    # 32% - Major contributor
    "obstacle": 25,      # 10%
    "debris": 15,        # 6%
    "water_logging": 10  # 4%
}

DEVICE_IDS = [
    "argus-device-01",
    "argus-device-02", 
    "argus-device-03",
    "argus-device-04",
    "argus-device-05"
]

def load_graph():
    """Load the road network graph."""
    print(f"Loading graph from {GRAPH_FILE}...")
    G = ox.load_graphml(str(GRAPH_FILE))
    print(f"✓ Loaded graph with {len(G.nodes)} nodes and {len(G.edges)} edges")
    return G

def get_random_road_point(G):
    """Get a random point on a driveable road edge."""
    edges = list(G.edges(keys=True, data=True))
    
    # Filter for driveable roads
    driveable_edges = []
    for u, v, key, data in edges:
        highway = data.get("highway", "")
        if isinstance(highway, list):
            highway = highway[0]
        
        if highway in ["residential", "secondary", "tertiary", "primary", 
                       "unclassified", "secondary_link", "tertiary_link", 
                       "primary_link", "living_street", "service", "trunk"]:
            driveable_edges.append((u, v, key, data))
    
    # Pick a random edge
    u, v, key, data = random.choice(driveable_edges)
    
    # Get node coordinates
    u_lat = G.nodes[u]['y']
    u_lng = G.nodes[u]['x']
    v_lat = G.nodes[v]['y']
    v_lng = G.nodes[v]['x']
    
    # Interpolate a random point along the edge
    t = random.uniform(0.1, 0.9)
    lat = u_lat + t * (v_lat - u_lat)
    lng = u_lng + t * (v_lng - u_lng)
    
    return round(lat, 6), round(lng, 6)

def generate_timestamp():
    """Generate a random timestamp within the last 30 days."""
    now = datetime.now()
    days_ago = random.randint(0, 30)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    
    timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
    return timestamp.isoformat()

def generate_hazards(G, count, hazard_class):
    """Generate hazard records for a specific class."""
    hazards = []
    
    for i in range(count):
        lat, lng = get_random_road_point(G)
        
        # Confidence varies by hazard type
        if hazard_class in ["pothole", "road_crack"]:
            confidence = round(random.uniform(0.75, 0.98), 2)
        else:
            confidence = round(random.uniform(0.65, 0.95), 2)
        
        hazard = {
            "device_id": random.choice(DEVICE_IDS),
            "lat": lat,
            "lng": lng,
            "hazard_class": hazard_class,
            "confidence": confidence,
            "source": "device"
        }
        
        hazards.append(hazard)
    
    return hazards

def insert_hazards_batch(hazards, batch_size=50):
    """Insert hazards in batches to avoid timeout."""
    total = len(hazards)
    inserted = 0
    failed = 0
    
    for i in range(0, total, batch_size):
        batch = hazards[i:i + batch_size]
        try:
            result = supabase.table("hazards").insert(batch).execute()
            inserted += len(batch)
            print(f"  ✓ Inserted batch {i//batch_size + 1}: {len(batch)} records ({inserted}/{total})")
        except Exception as e:
            failed += len(batch)
            print(f"  ✗ Failed to insert batch {i//batch_size + 1}: {e}")
    
    return inserted, failed

def main():
    print("=" * 70)
    print("  SYNTHETIC HAZARD DATA GENERATOR & INSERTER")
    print("=" * 70)
    
    # Load graph
    G = load_graph()
    
    # Generate hazards for each class
    all_hazards = []
    
    print("\nGenerating hazards...")
    for hazard_class, count in HAZARD_DISTRIBUTION.items():
        print(f"  → {hazard_class}: {count} records...", end=" ")
        hazards = generate_hazards(G, count, hazard_class)
        all_hazards.extend(hazards)
        print("✓")
    
    # Shuffle to mix different types
    random.shuffle(all_hazards)
    
    print(f"\n✓ Generated {len(all_hazards)} total hazards")
    
    # Insert into database
    print("\nInserting into Supabase...")
    inserted, failed = insert_hazards_batch(all_hazards, batch_size=50)
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total generated: {len(all_hazards)}")
    print(f"Successfully inserted: {inserted}")
    print(f"Failed: {failed}")
    print()
    
    for hazard_class, count in HAZARD_DISTRIBUTION.items():
        percentage = (count / len(all_hazards)) * 100
        print(f"  {hazard_class}: {count} ({percentage:.1f}%)")
    
    print("\n✓ Done!")

if __name__ == "__main__":
    main()
