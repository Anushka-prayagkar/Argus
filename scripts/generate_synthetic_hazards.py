"""
Generate synthetic road hazard data for the hazards table.
Ensures hazards are placed on actual roads from the graph.
"""
import json
import random
from datetime import datetime, timedelta
import osmnx as ox
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent
GRAPH_FILE = BASE_DIR / "data_files" / "pune_graph.graphml"
OUTPUT_FILE = BASE_DIR / "data_files" / "synthetic_hazards.json"

# Hazard distribution (total 250)
HAZARD_DISTRIBUTION = {
    "pothole": 120,      # 48% - Major contributor
    "road_crack": 80,    # 32% - Major contributor
    "obstacle": 25,      # 10%
    "debris": 15,        # 6%
    "water_logging": 10  # 4%
}

# Device IDs for variety
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
    print(f"Loaded graph with {len(G.nodes)} nodes and {len(G.edges)} edges")
    return G

def get_random_road_point(G):
    """Get a random point on a driveable road edge."""
    # Get all edges
    edges = list(G.edges(keys=True, data=True))
    
    # Filter for driveable roads
    driveable_edges = []
    for u, v, key, data in edges:
        highway = data.get("highway", "")
        if isinstance(highway, list):
            highway = highway[0]
        
        # Include major driveable road types
        if highway in ["residential", "secondary", "tertiary", "primary", 
                       "unclassified", "secondary_link", "tertiary_link", 
                       "primary_link", "living_street", "service", "trunk"]:
            driveable_edges.append((u, v, key, data))
    
    print(f"Found {len(driveable_edges)} driveable edges")
    
    # Pick a random edge
    u, v, key, data = random.choice(driveable_edges)
    
    # Get node coordinates
    u_lat = G.nodes[u]['y']
    u_lng = G.nodes[u]['x']
    v_lat = G.nodes[v]['y']
    v_lng = G.nodes[v]['x']
    
    # Interpolate a random point along the edge
    t = random.uniform(0.1, 0.9)  # Avoid exact endpoints
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
            "source": "device",
            "created_at": generate_timestamp()
        }
        
        hazards.append(hazard)
    
    return hazards

def main():
    print("=" * 60)
    print("  SYNTHETIC HAZARD DATA GENERATOR")
    print("=" * 60)
    
    # Load graph
    G = load_graph()
    
    # Generate hazards for each class
    all_hazards = []
    
    for hazard_class, count in HAZARD_DISTRIBUTION.items():
        print(f"\nGenerating {count} {hazard_class} hazards...")
        hazards = generate_hazards(G, count, hazard_class)
        all_hazards.extend(hazards)
        print(f"  ✓ Generated {len(hazards)} records")
    
    # Shuffle to mix timestamps
    random.shuffle(all_hazards)
    
    # Save to JSON
    print(f"\nSaving {len(all_hazards)} hazards to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_hazards, f, indent=2)
    
    print(f"✓ Saved to {OUTPUT_FILE}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total hazards: {len(all_hazards)}")
    for hazard_class, count in HAZARD_DISTRIBUTION.items():
        percentage = (count / len(all_hazards)) * 100
        print(f"  {hazard_class}: {count} ({percentage:.1f}%)")
    
    # Print sample SQL insert
    print("\n" + "=" * 60)
    print("SAMPLE SQL INSERT (first 3 records)")
    print("=" * 60)
    for hazard in all_hazards[:3]:
        print(f"INSERT INTO hazards (device_id, lat, lng, hazard_class, confidence, source, created_at)")
        print(f"VALUES ('{hazard['device_id']}', {hazard['lat']}, {hazard['lng']}, '{hazard['hazard_class']}', {hazard['confidence']}, '{hazard['source']}', '{hazard['created_at']}');")
        print()

if __name__ == "__main__":
    main()
