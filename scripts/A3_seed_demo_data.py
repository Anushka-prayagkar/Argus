import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

try:
    from supabase import create_client
except ImportError:
    create_client = None

def get_random_date(days_back=60):
    now = datetime.now()
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    return now - delta

def delete_all_demo_data(supabase):
    """Delete all existing demo data from all tables."""
    tables = ['hazards', 'crashes', 'cluster_alerts', 'blackspots']
    for table in tables:
        try:
            supabase.table(table).delete().neq('id', '').execute()
            print(f"  Deleted existing data from {table}")
        except Exception:
            try:
                supabase.table(table).delete().not_.is_('created_at', None).execute()
                print(f"  Deleted existing data from {table}")
            except Exception as e2:
                print(f"  Note: Could not delete from {table}: {e2}")

def seed_hazards(supabase):
    """Seed 200 hazard records across 6 zones with specific type mixes."""
    zones = [
        (18.5308, 73.8475, 40, ['pothole', 'waterlogging', 'debris']),
        (18.5074, 73.8077, 40, ['pothole', 'broken_road']),
        (18.5089, 73.9260, 30, ['pothole', 'waterlogging', 'debris', 'broken_road']),
        (18.5679, 73.9143, 30, ['pothole', 'debris']),
        (18.5590, 73.7869, 30, ['pothole', 'waterlogging', 'debris', 'broken_road']),
        (18.4529, 73.8498, 30, ['pothole', 'waterlogging']),
    ]
    records = []
    for base_lat, base_lng, count, types in zones:
        for _ in range(count):
            r_lat = base_lat + random.uniform(-0.003, 0.003)
            r_lng = base_lng + random.uniform(-0.003, 0.003)
            h_type = random.choice(types)
            records.append({
                "lat": r_lat,
                "lng": r_lng,
                "hazard_class": h_type,
                "created_at": get_random_date(60).isoformat(),
                "device_id": "demo-seeder"
            })
    try:
        res = supabase.table('hazards').insert(records).execute()
        print(f"  Hazards inserted: {len(res.data)}")
        return len(res.data)
    except Exception as e:
        print(f"  Error seeding 'hazards': {e}")
        return 0


def seed_crashes(supabase):
    """Seed 60 crash records across first 3 zones (20 per zone)."""
    zones = [
        (18.5308, 73.8475),
        (18.5074, 73.8077),
        (18.5089, 73.9260),
    ]
    records = []
    for base_lat, base_lng in zones:
        for _ in range(20):
            r_lat = base_lat + random.uniform(-0.003, 0.003)
            r_lng = base_lng + random.uniform(-0.003, 0.003)
            records.append({
                "crash_lat": r_lat,
                "crash_lon": r_lng,
                "created_at": get_random_date(60).isoformat(),
                "device_id": "demo-seeder"
            })
    try:
        res = supabase.table('crashes').insert(records).execute()
        print(f"  Crashes inserted: {len(res.data)}")
        return len(res.data)
    except Exception as e:
        print(f"  Error seeding 'crashes': {e}")
        return 0


def seed_clusters(supabase):
    """Seed 20 cluster alert records across 5 zones (4 per zone)."""
    zones = [
        (18.5308, 73.8475),
        (18.5074, 73.8077),
        (18.5089, 73.9260),
        (18.5679, 73.9143),
        (18.5590, 73.7869),
    ]
    records = []
    severities = ['high', 'medium', 'high', 'medium']
    for base_lat, base_lng in zones:
        for i, sev in enumerate(severities):
            r_lat = base_lat + random.uniform(-0.003, 0.003)
            r_lng = base_lng + random.uniform(-0.003, 0.003)
            records.append({
                "lat": r_lat,
                "lng": r_lng,
                "severity": sev,
                "created_at": get_random_date(60).isoformat()
            })
    try:
        res = supabase.table('cluster_alerts').insert(records).execute()
        print(f"  Cluster alerts inserted: {len(res.data)}")
        return len(res.data)
    except Exception as e:
        print(f"  Error seeding 'cluster_alerts': {e}")
        return 0


def seed_blackspots(supabase):
    """Seed 10 blackspot records (2 per zone) across 5 zones."""
    zones = [
        (18.5308, 73.8475),
        (18.5074, 73.8077),
        (18.5089, 73.9260),
        (18.5679, 73.9143),
        (18.5590, 73.7869),
    ]
    zone_names = ["Shivajinagar Zone", "Kothrud Zone", "Hadapsar Zone", "Viman Nagar Zone", "Baner Zone"]
    records = []
    for idx, (base_lat, base_lng) in enumerate(zones):
        for j in range(2):
            offset = 0.001 if j == 0 else -0.001
            r_lat = base_lat + offset + random.uniform(-0.0005, 0.0005)
            r_lng = base_lng + offset + random.uniform(-0.0005, 0.0005)
            name = f"{zone_names[idx]} Blackspot {j + 1}"
            records.append({
                "black_lat": r_lat,
                "black_lon": r_lng,
                "name": name,
                "created_at": get_random_date(60).isoformat()
            })
    try:
        res = supabase.table('blackspots').insert(records).execute()
        print(f"  Blackspots inserted: {len(res.data)}")
        return len(res.data)
    except Exception as e:
        print(f"  Error seeding 'blackspots': {e}")
        return 0


def main():
    load_dotenv()
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        print("[ERROR] Missing SUPABASE_URL or SUPABASE_KEY in environment variables.")
        return
        
    if not create_client:
        print("[ERROR] supabase-py is not installed. Run 'pip install supabase'.")
        return
        
    supabase = create_client(url, key)
    print("=" * 55)
    print("  SEEDING DEMO DATA TO SUPABASE")
    print("=" * 55)

    # Step 1: Delete all existing demo data
    print("\n[1] Deleting existing demo data...")
    delete_all_demo_data(supabase)

    # Step 2: Seed new data
    print("\n[2] Inserting new demo data...")
    counts = {
        'hazards': seed_hazards(supabase),
        'crashes': seed_crashes(supabase),
        'cluster_alerts': seed_clusters(supabase),
        'blackspots': seed_blackspots(supabase)
    }

    # Step 3: Print summary
    print("\n" + "=" * 55)
    print("  SEED COMPLETE - ROW COUNTS")
    print("=" * 55)
    for table, count in counts.items():
        print(f"  {table:20}: {count} rows")
    print("=" * 55)

if __name__ == "__main__":
    main()
