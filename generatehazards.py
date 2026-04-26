"""
generate_hazards.py  —  Generates 300+ synthetic road hazards around Shivajinagar, Pune
and inserts them into Supabase  (columns: device_id, lat, lng, hazard_class, confidence, source)
"""

import random
import math
import os
from supabase import create_client

# ── Supabase config ─────────────────────────────────────────────────
SUPABASE_URL = "https://zvobatlihkponymuvgqs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp2b2JhdGxpaGtwb255bXV2Z3FzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQxOTUwOTIsImV4cCI6MjA4OTc3MTA5Mn0.bTp1kZp_EwYXK3UqvNNTsLTdy65ApnGl8IZ-CshgbBg"
TABLE_NAME   = "hazards"          # change if your table name differs

# ── Area config ─────────────────────────────────────────────────────
CENTER_LAT = 18.5308
CENTER_LON = 73.8475
RADIUS_KM  = 15.0
TOTAL      = 350   # generate a few extra so we always clear 300 after any filtering

# ── Hazard class weights (potholes + cracks get the most) ───────────
HAZARD_CLASSES = [
    ("pothole",             30),   # highest weight
    ("road_crack",          25),   # second highest
    ("waterlogging",        12),
    ("broken_divider",      10),
    ("missing_manhole",      8),
    ("debris",               6),
    ("damaged_signage",      5),
    ("speed_breaker",        4),   # unmarked / broken speed breakers
]

# ── Source options ───────────────────────────────────────────────────
SOURCES = ["device", "community_report", "municipal_feed", "sensor"]
SOURCE_WEIGHTS = [40, 35, 15, 10]

# ── Device ID pool ───────────────────────────────────────────────────
DEVICE_IDS = [f"argus-v{i}" for i in range(1, 13)]   # argus-v1 … argus-v12


# ── Helpers ──────────────────────────────────────────────────────────

def weighted_choice(options):
    """Pick an item from [(value, weight), ...] list."""
    values, weights = zip(*options)
    return random.choices(values, weights=weights, k=1)[0]


def random_point_in_circle(center_lat, center_lon, radius_km):
    """
    Uniform random point inside a circle using rejection sampling.
    Returns (lat, lon) rounded to 7 decimal places.
    """
    lat_deg = radius_km / 111.0
    lon_deg = radius_km / (111.0 * math.cos(math.radians(center_lat)))

    while True:
        dlat = random.uniform(-lat_deg, lat_deg)
        dlon = random.uniform(-lon_deg, lon_deg)
        # Check it's inside the circle
        dist = math.sqrt((dlat / lat_deg) ** 2 + (dlon / lon_deg) ** 2)
        if dist <= 1.0:
            return (
                round(center_lat + dlat, 7),
                round(center_lon + dlon, 7),
            )


def confidence_for(hazard_class):
    """
    Return a realistic confidence score per hazard type.
    Potholes/cracks detected by device have higher confidence.
    """
    base_ranges = {
        "pothole":          (0.72, 0.98),
        "road_crack":       (0.68, 0.95),
        "waterlogging":     (0.60, 0.90),
        "broken_divider":   (0.55, 0.88),
        "missing_manhole":  (0.65, 0.93),
        "debris":           (0.50, 0.85),
        "damaged_signage":  (0.45, 0.80),
        "speed_breaker":    (0.55, 0.87),
    }
    lo, hi = base_ranges.get(hazard_class, (0.50, 0.90))
    return round(random.uniform(lo, hi), 2)


# ── Generate records ─────────────────────────────────────────────────

def generate_records(n):
    records = []
    for _ in range(n):
        hazard = weighted_choice(HAZARD_CLASSES)
        lat, lng = random_point_in_circle(CENTER_LAT, CENTER_LON, RADIUS_KM)
        records.append({
            "device_id":    random.choice(DEVICE_IDS),
            "lat":          lat,
            "lng":          lng,
            "hazard_class": hazard,
            "confidence":   confidence_for(hazard),
            "source":       random.choices(SOURCES, weights=SOURCE_WEIGHTS, k=1)[0],
        })
    return records


# ── Insert into Supabase ─────────────────────────────────────────────

def insert_records(records):
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    BATCH = 50   # Supabase handles 50 rows per insert comfortably
    total_inserted = 0

    for i in range(0, len(records), BATCH):
        batch = records[i : i + BATCH]
        resp  = client.table(TABLE_NAME).insert(batch).execute()
        total_inserted += len(batch)
        print(f"[OK] Inserted batch {i // BATCH + 1}  —  "
              f"{total_inserted}/{len(records)} rows")

    return total_inserted


# ── Summary printer ──────────────────────────────────────────────────

def print_summary(records):
    from collections import Counter
    counts = Counter(r["hazard_class"] for r in records)
    print()
    print("=" * 45)
    print("  HAZARD CLASS DISTRIBUTION")
    print("=" * 45)
    for cls, cnt in counts.most_common():
        bar = "█" * (cnt // 3)
        print(f"  {cls:<22} {cnt:>4}  {bar}")
    print(f"\n  Total records : {len(records)}")
    print("=" * 45)


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("=" * 45)
    print("  Argus — Synthetic Hazard Generator")
    print(f"  Center  : {CENTER_LAT}, {CENTER_LON}  (Shivajinagar)")
    print(f"  Radius  : {RADIUS_KM} km")
    print(f"  Records : {TOTAL}")
    print(f"  Table   : {TABLE_NAME}")
    print("=" * 45)

    print("\n[>>] Generating records ...")
    records = generate_records(TOTAL)
    print(f"[OK] {len(records)} records generated")

    print_summary(records)

    print("\n[>>] Inserting into Supabase ...")
    inserted = insert_records(records)
    print(f"\n[OK] Done — {inserted} rows inserted into '{TABLE_NAME}'\n")


if __name__ == "__main__":
    main()