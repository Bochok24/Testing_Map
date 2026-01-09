"""
CitizenLink - Synthetic Test Data Generator
============================================
Generates mock complaint records for testing the Generalized DBSCAN clustering algorithm.
Uses actual Digos City barangay boundaries for realistic geographic distribution.

Author: CitizenLink Development Team
Date: January 2026

This script creates 5 specific test scenarios:
1. Main Event (Flooding + Leak) - Tests semantic correlation
2. Duplicate Spammer - Tests redundancy detection
3. Neighbors (Discrete Issue) - Tests epsilon threshold per category
4. Old News (Time Decay) - Tests temporal window filtering
5. False Positive - Tests semantic rejection
"""

import json
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import uuid

# ==================== CONFIGURATION ====================

# Boundary files
CITY_BOUNDARY_FILE = "digos-city-boundary.json"
BARANGAY_BOUNDARY_FILE = "brgy_boundaries_location.json"

# Output file
OUTPUT_FILE = "mock_complaints.json"

# Categories with their adaptive epsilon values (in meters)
CATEGORY_EPSILON = {
    "Pipe Leak": 15.0,
    "Flooding": 25.0,
    "Pothole": 10.0,
    "No Water": 5.0,
    "Trash": 8.0,
    "Stray Dog": 20.0,
    "Broken Streetlight": 12.0,
    "Illegal Dumping": 15.0,
    "Noise Complaint": 10.0,
    "Road Damage": 12.0,
}

# Taglish descriptions by category
DESCRIPTIONS = {
    "Pipe Leak": [
        "May tulo ng tubig dito sa kanto",
        "Nabutas yung pipe, malakas ang agos",
        "Water pipe is leaking badly here",
        "Sobrang lakas ng tulo ng tubig sa harap ng bahay namin",
        "Pipe burst dito sa street namin",
        "May sira yung water pipe, need repair ASAP",
        "Tubig everywhere dahil sa butas na pipe",
    ],
    "Flooding": [
        "Baha na dito!",
        "Flooded street, hindi na madaanan",
        "Tubig sa daan, tuhod-deep na",
        "Grabe ang baha, need help",
        "Flooded area near the intersection",
        "Lubog na ang kalye dito",
        "Flash flood warning dito sa area namin",
        "Ang taas na ng tubig, di na makalabas",
    ],
    "Pothole": [
        "Malaking butas sa kalsada",
        "Pothole na delikado sa mga motor",
        "May lubak dito, mapanganib",
        "Big hole on the road, very dangerous",
        "Sira ang daan, malaki ang butas",
        "Napakalaking lubak, naaksidente na ako dito",
    ],
    "No Water": [
        "Walang tubig for 3 days na",
        "No water supply sa area namin",
        "Interrupted ang water, kailan babalik?",
        "Wala kaming tubig since yesterday",
        "Water outage dito, please check",
    ],
    "Trash": [
        "Napakaraming basura dito",
        "Garbage pile-up, need collection",
        "Di na nakokolekta ang basura for a week",
        "Sobrang dumi na dito, puno ng basura",
        "Trash everywhere, mabaho na",
        "Hindi na dumadaan ang garbage truck",
    ],
    "Stray Dog": [
        "May mga stray dogs na aggressive dito",
        "Pack of dogs roaming the street",
        "Mapanganib na aso, nangangagat",
        "Maraming gala na aso sa area",
        "Stray dogs blocking the road",
    ],
    "Broken Streetlight": [
        "Sira ang ilaw sa kanto",
        "Streetlight not working, madilim",
        "No light here for weeks",
        "Busted streetlight, very dark at night",
        "Paki-ayos ang poste ng ilaw dito",
    ],
    "Illegal Dumping": [
        "May nagtatapon ng basura illegally dito",
        "Illegal dump site discovered",
        "Someone is dumping trash here at night",
        "Bawal magtapon pero may nagtapon pa rin",
    ],
    "Noise Complaint": [
        "Sobrang ingay ng construction dito",
        "Noise pollution from the videoke next door",
        "Too loud, can't sleep",
        "Maingay na kapitbahay, every night",
    ],
    "Road Damage": [
        "Sira ang kalsada dito",
        "Road is cracked and damaged",
        "Need road repair ASAP",
        "Delikado ang daan, maraming crack",
    ],
}

# User names for authenticity
USER_NAMES = [
    "Juan Dela Cruz", "Maria Santos", "Pedro Reyes", "Ana Garcia",
    "Jose Rizal Jr.", "Carmen Lopez", "Miguel Torres", "Rosa Mendoza",
    "Luis Bautista", "Elena Ramos", "Carlos Cruz", "Teresa Aquino",
    "Roberto Flores", "Linda Gonzales", "Antonio Morales", "Patricia Diaz"
]


# ==================== GEOMETRY FUNCTIONS ====================

def load_barangay_boundaries() -> List[Dict]:
    """Load barangay boundaries from JSON file."""
    with open(BARANGAY_BOUNDARY_FILE, 'r') as f:
        return json.load(f)


def load_city_boundary() -> Dict:
    """Load city boundary from JSON file."""
    with open(CITY_BOUNDARY_FILE, 'r') as f:
        return json.load(f)


def get_polygon_bounds(coordinates: List) -> Tuple[float, float, float, float]:
    """Get bounding box of a polygon. Returns (min_lng, min_lat, max_lng, max_lat)."""
    # Flatten nested coordinates
    flat_coords = []
    
    def flatten(coords):
        if isinstance(coords[0], (int, float)):
            flat_coords.append(coords)
        else:
            for c in coords:
                flatten(c)
    
    flatten(coordinates)
    
    lngs = [c[0] for c in flat_coords]
    lats = [c[1] for c in flat_coords]
    
    return (min(lngs), min(lats), max(lngs), max(lats))


def point_in_polygon(point: Tuple[float, float], polygon: List) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm.
    Point: (lng, lat)
    Polygon: list of [lng, lat] coordinates
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside


def get_outer_ring(geojson_coords) -> List:
    """Extract the outer ring from GeoJSON coordinates (handles MultiPolygon and Polygon)."""
    # For MultiPolygon: coordinates[0][0] is the outer ring of the first polygon
    # For Polygon: coordinates[0] is the outer ring
    if isinstance(geojson_coords[0][0][0], list):
        # MultiPolygon - get first polygon's outer ring
        return geojson_coords[0][0]
    else:
        # Polygon - get outer ring
        return geojson_coords[0]


def random_point_in_barangay(barangay: Dict) -> Tuple[float, float]:
    """Generate a random point inside a barangay boundary."""
    geojson = barangay['geojson']
    coords = geojson['coordinates']
    
    # Get the outer ring of the polygon
    outer_ring = get_outer_ring(coords)
    
    # Get bounding box
    min_lng, min_lat, max_lng, max_lat = get_polygon_bounds(outer_ring)
    
    # Try to find a point inside the polygon (with max attempts)
    for _ in range(100):
        lng = random.uniform(min_lng, max_lng)
        lat = random.uniform(min_lat, max_lat)
        
        if point_in_polygon((lng, lat), outer_ring):
            return (lat, lng)  # Return as (lat, lng)
    
    # Fallback: return centroid approximation
    centroid_lng = (min_lng + max_lng) / 2
    centroid_lat = (min_lat + max_lat) / 2
    return (centroid_lat, centroid_lng)


def get_barangay_centroid(barangay: Dict) -> Tuple[float, float]:
    """Get the approximate centroid of a barangay."""
    geojson = barangay['geojson']
    coords = geojson['coordinates']
    outer_ring = get_outer_ring(coords)
    min_lng, min_lat, max_lng, max_lat = get_polygon_bounds(outer_ring)
    return ((min_lat + max_lat) / 2, (min_lng + max_lng) / 2)


# ==================== HELPER FUNCTIONS ====================

def generate_id(prefix: str = "C") -> str:
    """Generate a unique complaint ID."""
    return f"{prefix}-{random.randint(1000, 9999)}"


def generate_user_id() -> str:
    """Generate a user ID."""
    return f"u_{random.randint(100, 999)}"


def offset_coordinates(lat: float, lng: float, meters: float, bearing: float = None) -> Tuple[float, float]:
    """
    Offset coordinates by a given distance in meters.
    """
    if bearing is None:
        bearing = random.uniform(0, 360)
    
    R = 6371000  # Earth's radius in meters
    lat_rad = math.radians(lat)
    lng_rad = math.radians(lng)
    bearing_rad = math.radians(bearing)
    
    d = meters / R
    
    new_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(d) +
        math.cos(lat_rad) * math.sin(d) * math.cos(bearing_rad)
    )
    
    new_lng_rad = lng_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(d) * math.cos(lat_rad),
        math.cos(d) - math.sin(lat_rad) * math.sin(new_lat_rad)
    )
    
    return (math.degrees(new_lat_rad), math.degrees(new_lng_rad))


def random_timestamp(base: datetime, hours_range: float = 2.0, direction: str = "both") -> str:
    """Generate a random timestamp within a range of the base time."""
    if direction == "before":
        delta = timedelta(hours=random.uniform(0, hours_range))
        ts = base - delta
    elif direction == "after":
        delta = timedelta(hours=random.uniform(0, hours_range))
        ts = base + delta
    else:
        delta = timedelta(hours=random.uniform(-hours_range, hours_range))
        ts = base + delta
    
    return ts.strftime("%Y-%m-%dT%H:%M:%S")


def create_complaint(
    complaint_id: str,
    user_id: str,
    timestamp: str,
    category: str,
    description: str,
    latitude: float,
    longitude: float,
    barangay: str = None,
    status: str = "PENDING",
    scenario_tag: str = None
) -> Dict:
    """Create a complaint record."""
    record = {
        "id": complaint_id,
        "user_id": user_id,
        "timestamp": timestamp,
        "category": category,
        "description": description,
        "latitude": round(latitude, 6),
        "longitude": round(longitude, 6),
        "status": status
    }
    
    if barangay:
        record["barangay"] = barangay
    
    if scenario_tag:
        record["_scenario"] = scenario_tag
    
    return record


# ==================== SCENARIO GENERATORS ====================

def generate_scenario_1_main_event(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    Scenario 1: Main Event (Flooding + Leak)
    - 1 Broken Pipe complaint
    - 4 Flooding complaints surrounding it (within 10-25 meters)
    - Timestamps within 2 hours
    
    Tests: Semantic correlation between Pipe Leak → Flooding
    Expected: Should MERGE all into one cluster
    """
    complaints = []
    
    # Pick a random barangay for this scenario
    brgy = random.choice(barangays)
    event_lat, event_lng = random_point_in_barangay(brgy)
    
    print(f"📍 Scenario 1: Main Event (Flooding + Leak)")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Location: ({event_lat:.6f}, {event_lng:.6f})")
    
    # Source complaint: Pipe Leak
    source_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Pipe Leak",
        description=random.choice(DESCRIPTIONS["Pipe Leak"]),
        latitude=event_lat,
        longitude=event_lng,
        barangay=brgy['name'],
        scenario_tag="scenario_1_source"
    )
    complaints.append(source_complaint)
    print(f"   ✓ Created source: Pipe Leak")
    
    # Surrounding flood complaints (4 within 10-25 meters)
    for i in range(4):
        offset_meters = random.uniform(10, 25)
        flood_lat, flood_lng = offset_coordinates(event_lat, event_lng, offset_meters)
        
        flood_complaint = create_complaint(
            complaint_id=generate_id(),
            user_id=generate_user_id(),
            timestamp=random_timestamp(base_time, 2.0, "after"),
            category="Flooding",
            description=random.choice(DESCRIPTIONS["Flooding"]),
            latitude=flood_lat,
            longitude=flood_lng,
            barangay=brgy['name'],
            scenario_tag="scenario_1_flood"
        )
        complaints.append(flood_complaint)
    
    print(f"   ✓ Created 4 surrounding flood complaints")
    print(f"   Expected Result: MERGE (Causal correlation)")
    
    return complaints


def generate_scenario_2_duplicate_spammer(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    Scenario 2: Duplicate Spammer
    - 3 complaints from SAME user
    - SAME location (exact coordinates)
    - Within 1 minute of each other
    
    Tests: Redundancy detection
    Expected: Should MERGE into single report
    """
    complaints = []
    
    brgy = random.choice(barangays)
    spam_lat, spam_lng = random_point_in_barangay(brgy)
    spammer_id = "u_SPAM_001"
    
    print(f"\n📍 Scenario 2: Duplicate Spammer")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Location: ({spam_lat:.6f}, {spam_lng:.6f})")
    print(f"   User: {spammer_id}")
    
    for i in range(3):
        timestamp = base_time + timedelta(seconds=i * 20)
        
        complaint = create_complaint(
            complaint_id=generate_id(),
            user_id=spammer_id,
            timestamp=timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
            category="Trash",
            description=random.choice(DESCRIPTIONS["Trash"]),
            latitude=spam_lat,
            longitude=spam_lng,
            barangay=brgy['name'],
            scenario_tag="scenario_2_spam"
        )
        complaints.append(complaint)
    
    print(f"   ✓ Created 3 duplicate complaints (20s apart)")
    print(f"   Expected Result: MERGE (Direct redundancy)")
    
    return complaints


def generate_scenario_3_discrete_neighbors(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    Scenario 3: Discrete Neighbors (No Water)
    - 2 complaints of same category
    - Distance: 15 meters apart
    - Epsilon for "No Water": 5 meters
    
    Tests: Epsilon threshold per category
    Expected: Should KEEP SEPARATE (15m > 5m epsilon)
    """
    complaints = []
    
    brgy = random.choice(barangays)
    lat_a, lng_a = random_point_in_barangay(brgy)
    lat_b, lng_b = offset_coordinates(lat_a, lng_a, 15, bearing=45)
    
    print(f"\n📍 Scenario 3: Discrete Neighbors (No Water)")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Location A: ({lat_a:.6f}, {lng_a:.6f})")
    print(f"   Location B: ({lat_b:.6f}, {lng_b:.6f})")
    print(f"   Distance: 15 meters | Epsilon: 5 meters")
    
    complaint_a = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="No Water",
        description=random.choice(DESCRIPTIONS["No Water"]),
        latitude=lat_a,
        longitude=lng_a,
        barangay=brgy['name'],
        scenario_tag="scenario_3_a"
    )
    complaints.append(complaint_a)
    
    complaint_b = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=random_timestamp(base_time, 1.0),
        category="No Water",
        description=random.choice(DESCRIPTIONS["No Water"]),
        latitude=lat_b,
        longitude=lng_b,
        barangay=brgy['name'],
        scenario_tag="scenario_3_b"
    )
    complaints.append(complaint_b)
    
    print(f"   ✓ Created 2 No Water complaints (15m apart)")
    print(f"   Expected Result: KEEP SEPARATE (15m > 5m epsilon)")
    
    return complaints


def generate_scenario_4_old_news(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    Scenario 4: Old News (Time Decay)
    - 2 complaints at SAME location
    - One from TODAY, one from 35 DAYS AGO
    
    Tests: Temporal window filtering
    Expected: Should IGNORE old data in clustering
    """
    complaints = []
    
    brgy = random.choice(barangays)
    event_lat, event_lng = random_point_in_barangay(brgy)
    
    print(f"\n📍 Scenario 4: Old News (Time Decay)")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Location: ({event_lat:.6f}, {event_lng:.6f})")
    
    # Today's complaint
    new_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Pothole",
        description=random.choice(DESCRIPTIONS["Pothole"]),
        latitude=event_lat,
        longitude=event_lng,
        barangay=brgy['name'],
        scenario_tag="scenario_4_new"
    )
    complaints.append(new_complaint)
    print(f"   ✓ Created TODAY complaint: {base_time.strftime('%Y-%m-%d')}")
    
    # Old complaint (35 days ago)
    old_time = base_time - timedelta(days=35)
    old_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=old_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Pothole",
        description=random.choice(DESCRIPTIONS["Pothole"]),
        latitude=event_lat,
        longitude=event_lng,
        barangay=brgy['name'],
        status="RESOLVED",
        scenario_tag="scenario_4_old"
    )
    complaints.append(old_complaint)
    print(f"   ✓ Created OLD complaint: {old_time.strftime('%Y-%m-%d')} (35 days ago)")
    print(f"   Expected Result: IGNORE old data in clustering")
    
    return complaints


def generate_scenario_5_false_positive(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    Scenario 5: False Positive (Unrelated Categories)
    - 2 complaints at SAME location (2m apart)
    - Categories: Stray Dog + Pothole (no semantic relation)
    
    Tests: Semantic rejection
    Expected: Should KEEP SEPARATE (no correlation)
    """
    complaints = []
    
    brgy = random.choice(barangays)
    lat_a, lng_a = random_point_in_barangay(brgy)
    lat_b, lng_b = offset_coordinates(lat_a, lng_a, 2, bearing=90)
    
    print(f"\n📍 Scenario 5: False Positive (Unrelated Categories)")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Location A: ({lat_a:.6f}, {lng_a:.6f})")
    print(f"   Location B: ({lat_b:.6f}, {lng_b:.6f})")
    print(f"   Distance: 2 meters | Categories: Stray Dog vs Pothole")
    
    dog_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Stray Dog",
        description=random.choice(DESCRIPTIONS["Stray Dog"]),
        latitude=lat_a,
        longitude=lng_a,
        barangay=brgy['name'],
        scenario_tag="scenario_5_dog"
    )
    complaints.append(dog_complaint)
    
    pothole_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=random_timestamp(base_time, 0.5),
        category="Pothole",
        description=random.choice(DESCRIPTIONS["Pothole"]),
        latitude=lat_b,
        longitude=lng_b,
        barangay=brgy['name'],
        scenario_tag="scenario_5_pothole"
    )
    complaints.append(pothole_complaint)
    
    print(f"   ✓ Created Stray Dog + Pothole (2m apart)")
    print(f"   Expected Result: KEEP SEPARATE (no semantic correlation)")
    
    return complaints


def generate_random_complaints(base_time: datetime, barangays: List[Dict], count: int = 50) -> List[Dict]:
    """
    Generate additional random complaints distributed across all barangays.
    Some complaints will share exact coordinates to test stacking feature.
    """
    complaints = []
    categories = list(CATEGORY_EPSILON.keys())
    
    print(f"\n📍 Generating {count} Random Complaints across {len(barangays)} barangays...")
    
    # Create hotspots (same coordinates for stacking)
    num_hotspots = random.randint(15, 25)
    hotspots = []
    for _ in range(num_hotspots):
        brgy = random.choice(barangays)
        lat, lng = random_point_in_barangay(brgy)
        hotspots.append({
            'lat': round(lat, 6),
            'lng': round(lng, 6),
            'barangay': brgy['name']
        })
    
    stacked_count = 0
    brgy_distribution = {}
    
    for i in range(count):
        category = random.choice(categories)
        
        # 30% chance to use a hotspot location (creates stacked complaints)
        if random.random() < 0.30 and hotspots:
            hotspot = random.choice(hotspots)
            lat = hotspot['lat']
            lng = hotspot['lng']
            barangay_name = hotspot['barangay']
            stacked_count += 1
        else:
            # Random barangay and location
            brgy = random.choice(barangays)
            lat, lng = random_point_in_barangay(brgy)
            lat = round(lat, 6)
            lng = round(lng, 6)
            barangay_name = brgy['name']
        
        # Track distribution
        brgy_distribution[barangay_name] = brgy_distribution.get(barangay_name, 0) + 1
        
        # Random time within the past week
        random_hours = random.uniform(0, 168)
        timestamp = base_time - timedelta(hours=random_hours)
        
        complaint = create_complaint(
            complaint_id=generate_id(),
            user_id=generate_user_id(),
            timestamp=timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
            category=category,
            description=random.choice(DESCRIPTIONS[category]),
            latitude=lat,
            longitude=lng,
            barangay=barangay_name,
            status=random.choice(["PENDING", "IN_PROGRESS", "RESOLVED"]),
            scenario_tag="random"
        )
        complaints.append(complaint)
    
    print(f"   ✓ Created {count} random complaints")
    print(f"   ✓ ~{stacked_count} complaints placed at hotspot locations (will be stacked)")
    print(f"   ✓ Distribution across {len(brgy_distribution)} barangays")
    
    # Show top 5 barangays
    sorted_brgy = sorted(brgy_distribution.items(), key=lambda x: x[1], reverse=True)[:5]
    for brgy_name, cnt in sorted_brgy:
        print(f"      - {brgy_name}: {cnt} complaints")
    
    return complaints


# ==================== MAIN EXECUTION ====================

def main():
    """Main function to generate all mock data."""
    
    print("=" * 60)
    print("  CitizenLink - Synthetic Test Data Generator")
    print("  Using actual Digos City barangay boundaries")
    print("=" * 60)
    
    # Load boundaries
    print("\n📂 Loading boundary files...")
    barangays = load_barangay_boundaries()
    city_boundary = load_city_boundary()
    
    print(f"   ✓ Loaded {len(barangays)} barangays:")
    for brgy in barangays:
        print(f"      - {brgy['name']}")
    
    # Base timestamp: Today
    base_time = datetime(2026, 1, 8, 10, 0, 0)
    
    all_complaints = []
    
    # Generate each scenario
    all_complaints.extend(generate_scenario_1_main_event(base_time, barangays))
    all_complaints.extend(generate_scenario_2_duplicate_spammer(base_time + timedelta(hours=1), barangays))
    all_complaints.extend(generate_scenario_3_discrete_neighbors(base_time + timedelta(hours=2), barangays))
    all_complaints.extend(generate_scenario_4_old_news(base_time + timedelta(hours=3), barangays))
    all_complaints.extend(generate_scenario_5_false_positive(base_time + timedelta(hours=4), barangays))
    
    # Generate random complaints to reach 500-600 total
    scenario_count = len(all_complaints)
    random_count = random.randint(500, 600) - scenario_count
    if random_count > 0:
        all_complaints.extend(generate_random_complaints(base_time, barangays, random_count))
    
    # Shuffle to mix scenarios with random data
    random.shuffle(all_complaints)
    
    # Re-assign sequential IDs for cleaner output
    for i, complaint in enumerate(all_complaints, 1):
        complaint["id"] = f"C-{i:03d}"
    
    # Calculate city center from all barangay centroids
    all_centroids = [get_barangay_centroid(b) for b in barangays]
    city_center_lat = sum(c[0] for c in all_centroids) / len(all_centroids)
    city_center_lng = sum(c[1] for c in all_centroids) / len(all_centroids)
    
    # Create output structure
    output = {
        "metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "generator": "CitizenLink Synthetic Data Generator v2.0",
            "total_records": len(all_complaints),
            "base_location": {
                "city": "Digos City",
                "latitude": round(city_center_lat, 6),
                "longitude": round(city_center_lng, 6)
            },
            "barangays": [b['name'] for b in barangays],
            "barangay_count": len(barangays),
            "scenarios": {
                "scenario_1": "Main Event (Pipe + Flooding) - 5 records",
                "scenario_2": "Duplicate Spammer - 3 records",
                "scenario_3": "Discrete Neighbors (No Water) - 2 records",
                "scenario_4": "Old News (Time Decay) - 2 records",
                "scenario_5": "False Positive - 2 records",
                "random": f"Random complaints - {random_count} records"
            },
            "category_epsilon": CATEGORY_EPSILON
        },
        "complaints": all_complaints
    }
    
    # Write to JSON file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"  ✅ SUCCESS: Generated {len(all_complaints)} complaints")
    print(f"  📁 Output file: {OUTPUT_FILE}")
    print("=" * 60)
    
    # Summary statistics
    print("\n📊 Summary by Scenario:")
    scenario_counts = {}
    for c in all_complaints:
        tag = c.get("_scenario", "unknown")
        scenario_counts[tag] = scenario_counts.get(tag, 0) + 1
    for tag, cnt in sorted(scenario_counts.items()):
        print(f"   • {tag}: {cnt} records")
    
    print("\n📊 Summary by Category:")
    category_counts = {}
    for c in all_complaints:
        cat = c["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    for cat, cnt in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {cat}: {cnt} records")
    
    print("\n📊 Summary by Barangay:")
    brgy_counts = {}
    for c in all_complaints:
        brgy = c.get("barangay", "Unknown")
        brgy_counts[brgy] = brgy_counts.get(brgy, 0) + 1
    for brgy, cnt in sorted(brgy_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   • {brgy}: {cnt} records")
    if len(brgy_counts) > 10:
        print(f"   ... and {len(brgy_counts) - 10} more barangays")


if __name__ == "__main__":
    main()
