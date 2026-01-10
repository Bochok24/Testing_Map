"""
CitizenLink - Synthetic Test Data Generator
============================================
Generates mock complaint records for testing the Generalized DBSCAN clustering algorithm.
Uses actual Digos City barangay boundaries for realistic geographic distribution.

Author: CitizenLink Development Team
Date: January 2026

This script creates 15 specific test scenarios across 3 groups:

Group A: Spatial Logic
- S-01 (Redundancy): 3x "Pothole" at exact same lat/lng (0m diff)
- S-03 (Discrete): 2x "No Water" exactly 15m apart (should NOT merge)
- S-07 (Precision Edge): Center="Pothole", Point A=24.9m, Point B=25.1m (tests math boundary)
- S-09 (GPS Drift): 5x "Streetlight" from same user scattered in 7m radius
- S-13 (Moving Hazard): "Stray Dog" at (0,0) and (0, 60m) reported 5 mins apart

Group B: Semantic Logic
- S-02 (Causal): 1x "Pipe Leak", 1x "Flood" (10m away)
- S-05 (False Correl): 1x "Stray Dog", 1x "Pothole" (1m away - unrelated)
- S-06 (Domino Chain): Pipe (0m) -> Flood (10m) -> Traffic (20m)
- S-10 (Conflict): 1x "Fire", 1x "Pothole" at EXACT same coordinates
- S-11 (Synonyms): Pt A: "Baha" (Flood), Pt B: "Rising Water" (Flood), Dist: 5m

Group C: Data Integrity
- S-04 (Time Decay): 2x "Trash" at same loc, Time A: Today, Time B: 90 Days Ago
- S-08 (Mass Panic): 20x "Fire" in 10m radius within 60 seconds
- S-12 (Spam Bot): 50 complaints, random locs, identical timestamp (to ms)
- S-14 (Default Pin): 10 complaints stacked at map center (0,0)
- S-15 (Null Data): 1 record lat: null, 1 record category: null
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
    "Fire": 30.0,
    "Traffic": 20.0,
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
    "Fire": [
        "May sunog dito!",
        "Fire emergency, need help!",
        "Nasusunog ang bahay!",
        "Smoke and flames visible here",
        "Fire outbreak sa area namin",
        "Sunog! Tawag na ng fire truck!",
    ],
    "Traffic": [
        "Traffic jam dito",
        "Road blocked, hindi madaanan",
        "Massive traffic sa intersection",
        "Bumper to bumper ang sasakyan",
        "Traffic buildup dahil sa aksidente",
    ],
}

# Keyword dictionary for text analysis - maps keywords to categories
KEYWORD_DICTIONARY = {
    # Water-related
    "tubig": ["Pipe Leak", "Flooding", "No Water"],
    "water": ["Pipe Leak", "Flooding", "No Water"],
    "tulo": ["Pipe Leak"],
    "leak": ["Pipe Leak"],
    "leaking": ["Pipe Leak"],
    "butas": ["Pipe Leak", "Pothole"],
    "pipe": ["Pipe Leak"],
    "burst": ["Pipe Leak"],
    "baha": ["Flooding"],
    "flood": ["Flooding"],
    "flooded": ["Flooding"],
    "lubog": ["Flooding"],
    "flash": ["Flooding"],
    "outage": ["No Water"],
    "walang": ["No Water", "Broken Streetlight"],
    "interrupted": ["No Water"],
    "supply": ["No Water"],
    
    # Road-related
    "lubak": ["Pothole"],
    "pothole": ["Pothole"],
    "hole": ["Pothole"],
    "butas": ["Pothole", "Pipe Leak"],
    "kalsada": ["Pothole", "Road Damage"],
    "road": ["Pothole", "Road Damage"],
    "daan": ["Pothole", "Road Damage"],
    "sira": ["Road Damage", "Broken Streetlight"],
    "crack": ["Road Damage"],
    "damage": ["Road Damage"],
    "repair": ["Road Damage", "Pipe Leak"],
    
    # Trash-related
    "basura": ["Trash", "Illegal Dumping"],
    "trash": ["Trash", "Illegal Dumping"],
    "garbage": ["Trash"],
    "dumi": ["Trash"],
    "mabaho": ["Trash", "Illegal Dumping"],
    "dump": ["Illegal Dumping"],
    "dumping": ["Illegal Dumping"],
    "tapon": ["Illegal Dumping"],
    "illegal": ["Illegal Dumping"],
    
    # Animal-related
    "aso": ["Stray Dog"],
    "dog": ["Stray Dog"],
    "dogs": ["Stray Dog"],
    "stray": ["Stray Dog"],
    "gala": ["Stray Dog"],
    "aggressive": ["Stray Dog"],
    "nangangagat": ["Stray Dog"],
    
    # Light-related
    "ilaw": ["Broken Streetlight"],
    "streetlight": ["Broken Streetlight"],
    "light": ["Broken Streetlight"],
    "dark": ["Broken Streetlight"],
    "madilim": ["Broken Streetlight"],
    "poste": ["Broken Streetlight"],
    "busted": ["Broken Streetlight"],
    
    # Noise-related
    "ingay": ["Noise Complaint"],
    "maingay": ["Noise Complaint"],
    "noise": ["Noise Complaint"],
    "loud": ["Noise Complaint"],
    "videoke": ["Noise Complaint"],
    "construction": ["Noise Complaint"],
    
    # Fire-related
    "sunog": ["Fire"],
    "fire": ["Fire"],
    "flames": ["Fire"],
    "smoke": ["Fire"],
    "burning": ["Fire"],
    "nasusunog": ["Fire"],
    
    # Traffic-related
    "traffic": ["Traffic"],
    "jam": ["Traffic"],
    "blocked": ["Traffic"],
    "bumper": ["Traffic"],
    "congestion": ["Traffic"],
    
    # Flood synonyms
    "baha": ["Flooding"],
    "rising water": ["Flooding"],
    "tubig tumataas": ["Flooding"],
    
    # Urgency keywords (boost relevance)
    "emergency": [],
    "urgent": [],
    "asap": [],
    "help": [],
    "grabe": [],
    "delikado": [],
    "dangerous": [],
    "mapanganib": [],
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


# ==================== KEYWORD EXTRACTION ====================

def extract_keywords(description: str, category: str) -> Dict:
    """
    Extract keywords from complaint description for text-based similarity analysis.
    
    Args:
        description: The complaint text description
        category: The complaint category
        
    Returns:
        Dict containing:
        - keywords: List of matched keywords
        - matched_categories: Categories suggested by keywords
        - relevance_score: How well keywords match the assigned category (0.0-1.0)
        - urgency_level: Detected urgency from keywords (low/medium/high)
    """
    # Normalize text: lowercase and split into words
    words = description.lower().replace(',', ' ').replace('.', ' ').replace('!', ' ').split()
    
    matched_keywords = []
    matched_categories = set()
    urgency_keywords = []
    
    # Urgency indicators
    urgency_words = {"emergency", "urgent", "asap", "help", "grabe", "delikado", "dangerous", "mapanganib"}
    
    for word in words:
        # Check if word is in our keyword dictionary
        if word in KEYWORD_DICTIONARY:
            categories = KEYWORD_DICTIONARY[word]
            if categories:  # Has category mappings
                matched_keywords.append(word)
                matched_categories.update(categories)
            elif word in urgency_words:
                urgency_keywords.append(word)
    
    # Calculate relevance score: how well do extracted keywords match the assigned category?
    relevance_score = 0.0
    if matched_categories:
        if category in matched_categories:
            # Category matches - calculate based on how many keywords point to this category
            category_matches = sum(1 for kw in matched_keywords 
                                   if category in KEYWORD_DICTIONARY.get(kw, []))
            relevance_score = min(1.0, category_matches / max(len(matched_keywords), 1) + 0.3)
        else:
            # Keywords suggest different category - lower score
            relevance_score = 0.2
    else:
        # No keywords matched - neutral score
        relevance_score = 0.5
    
    # Determine urgency level
    urgency_level = "low"
    if len(urgency_keywords) >= 2:
        urgency_level = "high"
    elif len(urgency_keywords) == 1 or any(word in description.lower() for word in ["please", "paki", "need"]):
        urgency_level = "medium"
    
    return {
        "keywords": matched_keywords,
        "matched_categories": list(matched_categories),
        "relevance_score": round(relevance_score, 2),
        "urgency_level": urgency_level
    }


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
    """Create a complaint record with keyword extraction."""
    # Extract keywords from description
    keyword_data = extract_keywords(description, category)
    
    record = {
        "id": complaint_id,
        "user_id": user_id,
        "timestamp": timestamp,
        "category": category,
        "description": description,
        "keywords": keyword_data["keywords"],
        "keyword_categories": keyword_data["matched_categories"],
        "keyword_relevance": keyword_data["relevance_score"],
        "urgency": keyword_data["urgency_level"],
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

# ==================== GROUP A: SPATIAL LOGIC ====================

def generate_scenario_S01_redundancy(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-01 (Redundancy): 3x "Pothole" at exact same lat/lng (0m diff).
    
    Tests: Exact duplicate detection at identical coordinates
    Expected: Should MERGE all into one cluster (redundant reports)
    """
    complaints = []
    
    brgy = random.choice(barangays)
    exact_lat, exact_lng = random_point_in_barangay(brgy)
    
    print(f"📍 S-01 (Redundancy): 3x Pothole at exact same location")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Location: ({exact_lat:.6f}, {exact_lng:.6f})")
    
    for i in range(3):
        complaint = create_complaint(
            complaint_id=generate_id(),
            user_id=generate_user_id(),  # Different users
            timestamp=random_timestamp(base_time, 1.0),
            category="Pothole",
            description=random.choice(DESCRIPTIONS["Pothole"]),
            latitude=exact_lat,  # EXACT same coordinates
            longitude=exact_lng,
            barangay=brgy['name'],
            scenario_tag="S01_redundancy"
        )
        complaints.append(complaint)
    
    print(f"   ✓ Created 3 Pothole complaints at EXACT same location (0m apart)")
    print(f"   Expected Result: MERGE (Direct redundancy)")
    
    return complaints


def generate_scenario_S03_discrete(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-03 (Discrete): 2x "No Water" exactly 15m apart.
    
    Tests: Epsilon threshold - "No Water" has 5m epsilon
    Expected: Should NOT merge (15m > 5m epsilon)
    """
    complaints = []
    
    brgy = random.choice(barangays)
    lat_a, lng_a = random_point_in_barangay(brgy)
    lat_b, lng_b = offset_coordinates(lat_a, lng_a, 15.0, bearing=90)  # Exactly 15m
    
    print(f"\n📍 S-03 (Discrete): 2x No Water exactly 15m apart")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Location A: ({lat_a:.6f}, {lng_a:.6f})")
    print(f"   Location B: ({lat_b:.6f}, {lng_b:.6f})")
    print(f"   Distance: 15m | Epsilon for No Water: 5m")
    
    complaint_a = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="No Water",
        description=random.choice(DESCRIPTIONS["No Water"]),
        latitude=lat_a,
        longitude=lng_a,
        barangay=brgy['name'],
        scenario_tag="S03_discrete_a"
    )
    complaints.append(complaint_a)
    
    complaint_b = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=random_timestamp(base_time, 0.5),
        category="No Water",
        description=random.choice(DESCRIPTIONS["No Water"]),
        latitude=lat_b,
        longitude=lng_b,
        barangay=brgy['name'],
        scenario_tag="S03_discrete_b"
    )
    complaints.append(complaint_b)
    
    print(f"   ✓ Created 2 No Water complaints (exactly 15m apart)")
    print(f"   Expected Result: KEEP SEPARATE (15m > 5m epsilon)")
    
    return complaints


def generate_scenario_S07_precision_edge(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-07 (Precision Edge): Center="Pothole". Point A=24.9m away. Point B=25.1m away.
    
    Tests: Math boundary precision for Flooding epsilon (25m)
    Expected: Point A should MERGE (24.9m < 25m), Point B should NOT merge (25.1m > 25m)
    """
    complaints = []
    
    brgy = random.choice(barangays)
    center_lat, center_lng = random_point_in_barangay(brgy)
    
    # Point A: 24.9m away (just inside boundary)
    lat_a, lng_a = offset_coordinates(center_lat, center_lng, 24.9, bearing=0)
    # Point B: 25.1m away (just outside boundary)
    lat_b, lng_b = offset_coordinates(center_lat, center_lng, 25.1, bearing=180)
    
    print(f"\n📍 S-07 (Precision Edge): Testing 25m epsilon boundary")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Center: ({center_lat:.6f}, {center_lng:.6f})")
    print(f"   Point A: 24.9m away (should merge)")
    print(f"   Point B: 25.1m away (should NOT merge)")
    
    # Center complaint - Flooding (epsilon = 25m)
    center_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Flooding",
        description=random.choice(DESCRIPTIONS["Flooding"]),
        latitude=center_lat,
        longitude=center_lng,
        barangay=brgy['name'],
        scenario_tag="S07_precision_center"
    )
    complaints.append(center_complaint)
    
    # Point A: 24.9m away
    complaint_a = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=random_timestamp(base_time, 0.5),
        category="Flooding",
        description=random.choice(DESCRIPTIONS["Flooding"]),
        latitude=lat_a,
        longitude=lng_a,
        barangay=brgy['name'],
        scenario_tag="S07_precision_inside"
    )
    complaints.append(complaint_a)
    
    # Point B: 25.1m away
    complaint_b = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=random_timestamp(base_time, 0.5),
        category="Flooding",
        description=random.choice(DESCRIPTIONS["Flooding"]),
        latitude=lat_b,
        longitude=lng_b,
        barangay=brgy['name'],
        scenario_tag="S07_precision_outside"
    )
    complaints.append(complaint_b)
    
    print(f"   ✓ Created 3 Flooding complaints (center + 24.9m + 25.1m)")
    print(f"   Expected: Center+A merge, B separate")
    
    return complaints


def generate_scenario_S09_gps_drift(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-09 (GPS Drift): 5x "Streetlight" from Same User ID scattered in a 7m radius.
    
    Tests: Same user, same issue, GPS inaccuracy causing scatter
    Expected: Should MERGE (same user, within reasonable drift)
    """
    complaints = []
    
    brgy = random.choice(barangays)
    center_lat, center_lng = random_point_in_barangay(brgy)
    drift_user = "u_GPS_DRIFT_001"
    
    print(f"\n📍 S-09 (GPS Drift): 5x Streetlight from same user in 7m radius")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Center: ({center_lat:.6f}, {center_lng:.6f})")
    print(f"   User ID: {drift_user}")
    
    for i in range(5):
        # Random offset within 7m radius
        drift_distance = random.uniform(0, 7)
        drift_bearing = random.uniform(0, 360)
        lat, lng = offset_coordinates(center_lat, center_lng, drift_distance, drift_bearing)
        
        complaint = create_complaint(
            complaint_id=generate_id(),
            user_id=drift_user,  # SAME user
            timestamp=random_timestamp(base_time, 0.1),  # Within ~6 minutes
            category="Broken Streetlight",
            description=random.choice(DESCRIPTIONS["Broken Streetlight"]),
            latitude=lat,
            longitude=lng,
            barangay=brgy['name'],
            scenario_tag="S09_gps_drift"
        )
        complaints.append(complaint)
    
    print(f"   ✓ Created 5 Streetlight complaints (same user, scattered in 7m radius)")
    print(f"   Expected Result: MERGE (GPS drift from same user)")
    
    return complaints


def generate_scenario_S13_moving_hazard(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-13 (Moving Hazard): "Stray Dog" at (0,0) and another at (0, 60m) reported 5 mins later.
    
    Tests: Mobile hazard detection - same type, far apart, short time
    Expected: Could be same pack moving - depends on implementation
    """
    complaints = []
    
    brgy = random.choice(barangays)
    lat_a, lng_a = random_point_in_barangay(brgy)
    lat_b, lng_b = offset_coordinates(lat_a, lng_a, 60.0, bearing=0)  # 60m north
    
    print(f"\n📍 S-13 (Moving Hazard): Stray Dog at 2 locations 60m apart, 5 mins gap")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Location A: ({lat_a:.6f}, {lng_a:.6f})")
    print(f"   Location B: ({lat_b:.6f}, {lng_b:.6f}) - 60m away")
    
    # First sighting
    complaint_a = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Stray Dog",
        description="May aggressive stray dog dito sa kanto",
        latitude=lat_a,
        longitude=lng_a,
        barangay=brgy['name'],
        scenario_tag="S13_moving_hazard_a"
    )
    complaints.append(complaint_a)
    
    # Second sighting - 5 minutes later, 60m away
    time_b = base_time + timedelta(minutes=5)
    complaint_b = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),  # Different user
        timestamp=time_b.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Stray Dog",
        description="Stray dogs roaming the street, moving fast",
        latitude=lat_b,
        longitude=lng_b,
        barangay=brgy['name'],
        scenario_tag="S13_moving_hazard_b"
    )
    complaints.append(complaint_b)
    
    print(f"   ✓ Created 2 Stray Dog complaints (60m apart, 5 mins interval)")
    print(f"   Expected Result: Consider mobile hazard pattern")
    
    return complaints


# ==================== GROUP B: SEMANTIC LOGIC ====================

def generate_scenario_S02_causal(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-02 (Causal): 1x "Pipe Leak", 1x "Flood" (10m away).
    
    Tests: Semantic correlation between cause and effect
    Expected: Should MERGE (Pipe Leak causes Flooding)
    """
    complaints = []
    
    brgy = random.choice(barangays)
    pipe_lat, pipe_lng = random_point_in_barangay(brgy)
    flood_lat, flood_lng = offset_coordinates(pipe_lat, pipe_lng, 10.0, bearing=135)
    
    print(f"\n📍 S-02 (Causal): Pipe Leak + Flood 10m apart")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Pipe Leak: ({pipe_lat:.6f}, {pipe_lng:.6f})")
    print(f"   Flood: ({flood_lat:.6f}, {flood_lng:.6f})")
    
    # Pipe Leak (cause)
    pipe_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Pipe Leak",
        description=random.choice(DESCRIPTIONS["Pipe Leak"]),
        latitude=pipe_lat,
        longitude=pipe_lng,
        barangay=brgy['name'],
        scenario_tag="S02_causal_pipe"
    )
    complaints.append(pipe_complaint)
    
    # Flooding (effect)
    flood_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=random_timestamp(base_time, 1.0, "after"),
        category="Flooding",
        description=random.choice(DESCRIPTIONS["Flooding"]),
        latitude=flood_lat,
        longitude=flood_lng,
        barangay=brgy['name'],
        scenario_tag="S02_causal_flood"
    )
    complaints.append(flood_complaint)
    
    print(f"   ✓ Created Pipe Leak + Flooding (10m apart)")
    print(f"   Expected Result: MERGE (Causal correlation)")
    
    return complaints


def generate_scenario_S05_false_correlation(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-05 (False Correl): 1x "Stray Dog", 1x "Pothole" (1m away - Unrelated).
    
    Tests: Semantic rejection of unrelated categories
    Expected: Should KEEP SEPARATE (no semantic relationship)
    """
    complaints = []
    
    brgy = random.choice(barangays)
    lat_a, lng_a = random_point_in_barangay(brgy)
    lat_b, lng_b = offset_coordinates(lat_a, lng_a, 1.0, bearing=45)  # Only 1m away
    
    print(f"\n📍 S-05 (False Correlation): Stray Dog + Pothole 1m apart")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Distance: 1m (very close but unrelated)")
    
    # Stray Dog
    dog_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Stray Dog",
        description=random.choice(DESCRIPTIONS["Stray Dog"]),
        latitude=lat_a,
        longitude=lng_a,
        barangay=brgy['name'],
        scenario_tag="S05_false_correl_dog"
    )
    complaints.append(dog_complaint)
    
    # Pothole
    pothole_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=random_timestamp(base_time, 0.5),
        category="Pothole",
        description=random.choice(DESCRIPTIONS["Pothole"]),
        latitude=lat_b,
        longitude=lng_b,
        barangay=brgy['name'],
        scenario_tag="S05_false_correl_pothole"
    )
    complaints.append(pothole_complaint)
    
    print(f"   ✓ Created Stray Dog + Pothole (1m apart)")
    print(f"   Expected Result: KEEP SEPARATE (no semantic correlation)")
    
    return complaints


def generate_scenario_S06_domino_chain(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-06 (Domino Chain): Pipe (0m) -> Flood (10m) -> Traffic (20m).
    
    Tests: Multi-step causal chain
    Expected: Should recognize cascade effect
    """
    complaints = []
    
    brgy = random.choice(barangays)
    pipe_lat, pipe_lng = random_point_in_barangay(brgy)
    flood_lat, flood_lng = offset_coordinates(pipe_lat, pipe_lng, 10.0, bearing=90)
    traffic_lat, traffic_lng = offset_coordinates(pipe_lat, pipe_lng, 20.0, bearing=90)
    
    print(f"\n📍 S-06 (Domino Chain): Pipe -> Flood -> Traffic")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Pipe (0m) -> Flood (10m) -> Traffic (20m)")
    
    # Step 1: Pipe Leak (origin)
    pipe_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Pipe Leak",
        description="Nabutas yung water pipe, malakas ang agos!",
        latitude=pipe_lat,
        longitude=pipe_lng,
        barangay=brgy['name'],
        scenario_tag="S06_domino_pipe"
    )
    complaints.append(pipe_complaint)
    
    # Step 2: Flooding (10m away, 30 mins later)
    time_flood = base_time + timedelta(minutes=30)
    flood_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=time_flood.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Flooding",
        description="Baha na dito dahil sa busted pipe!",
        latitude=flood_lat,
        longitude=flood_lng,
        barangay=brgy['name'],
        scenario_tag="S06_domino_flood"
    )
    complaints.append(flood_complaint)
    
    # Step 3: Traffic (20m away, 1 hour later)
    time_traffic = base_time + timedelta(hours=1)
    traffic_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=time_traffic.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Traffic",
        description="Traffic jam dahil sa baha, hindi madaanan!",
        latitude=traffic_lat,
        longitude=traffic_lng,
        barangay=brgy['name'],
        scenario_tag="S06_domino_traffic"
    )
    complaints.append(traffic_complaint)
    
    print(f"   ✓ Created Pipe -> Flood -> Traffic domino chain")
    print(f"   Expected Result: Recognize cascade effect")
    
    return complaints


def generate_scenario_S10_conflict(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-10 (Conflict): 1x "Fire", 1x "Pothole" at EXACT same coordinates.
    
    Tests: Conflicting categories at same location
    Expected: Should KEEP SEPARATE (incompatible categories)
    """
    complaints = []
    
    brgy = random.choice(barangays)
    exact_lat, exact_lng = random_point_in_barangay(brgy)
    
    print(f"\n📍 S-10 (Conflict): Fire + Pothole at EXACT same location")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Location: ({exact_lat:.6f}, {exact_lng:.6f})")
    
    # Fire
    fire_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Fire",
        description=random.choice(DESCRIPTIONS["Fire"]),
        latitude=exact_lat,
        longitude=exact_lng,
        barangay=brgy['name'],
        scenario_tag="S10_conflict_fire"
    )
    complaints.append(fire_complaint)
    
    # Pothole - same exact location
    pothole_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=random_timestamp(base_time, 0.5),
        category="Pothole",
        description=random.choice(DESCRIPTIONS["Pothole"]),
        latitude=exact_lat,  # EXACT same coordinates
        longitude=exact_lng,
        barangay=brgy['name'],
        scenario_tag="S10_conflict_pothole"
    )
    complaints.append(pothole_complaint)
    
    print(f"   ✓ Created Fire + Pothole at EXACT same location")
    print(f"   Expected Result: KEEP SEPARATE (incompatible categories)")
    
    return complaints


def generate_scenario_S11_synonyms(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-11 (Synonyms): Pt A: "Baha" (Flood). Pt B: "Rising Water" (Flood). Dist: 5m.
    
    Tests: Synonym recognition in descriptions
    Expected: Should MERGE (same meaning, close proximity)
    """
    complaints = []
    
    brgy = random.choice(barangays)
    lat_a, lng_a = random_point_in_barangay(brgy)
    lat_b, lng_b = offset_coordinates(lat_a, lng_a, 5.0, bearing=180)
    
    print(f"\n📍 S-11 (Synonyms): 'Baha' vs 'Rising Water' (5m apart)")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Distance: 5m")
    
    # Complaint A: Uses "Baha" (Tagalog for flood)
    complaint_a = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Flooding",
        description="Baha na dito sa amin! Ang taas na ng tubig!",
        latitude=lat_a,
        longitude=lng_a,
        barangay=brgy['name'],
        scenario_tag="S11_synonym_baha"
    )
    complaints.append(complaint_a)
    
    # Complaint B: Uses "Rising Water" (English)
    complaint_b = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=random_timestamp(base_time, 0.5),
        category="Flooding",
        description="Rising water level here, need immediate help!",
        latitude=lat_b,
        longitude=lng_b,
        barangay=brgy['name'],
        scenario_tag="S11_synonym_rising"
    )
    complaints.append(complaint_b)
    
    print(f"   ✓ Created 'Baha' + 'Rising Water' complaints (5m apart)")
    print(f"   Expected Result: MERGE (synonyms detected)")
    
    return complaints


# ==================== GROUP C: DATA INTEGRITY ====================

def generate_scenario_S04_time_decay(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-04 (Time Decay): 2x "Trash" at same loc. Time A: Today. Time B: 90 Days Ago.
    
    Tests: Temporal window filtering
    Expected: Should IGNORE old data (90 days is beyond typical window)
    """
    complaints = []
    
    brgy = random.choice(barangays)
    exact_lat, exact_lng = random_point_in_barangay(brgy)
    
    print(f"\n📍 S-04 (Time Decay): 2x Trash, Today vs 90 Days Ago")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Location: ({exact_lat:.6f}, {exact_lng:.6f})")
    
    # Today's complaint
    today_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Trash",
        description=random.choice(DESCRIPTIONS["Trash"]),
        latitude=exact_lat,
        longitude=exact_lng,
        barangay=brgy['name'],
        scenario_tag="S04_decay_today"
    )
    complaints.append(today_complaint)
    
    # 90 days ago
    old_time = base_time - timedelta(days=90)
    old_complaint = create_complaint(
        complaint_id=generate_id(),
        user_id=generate_user_id(),
        timestamp=old_time.strftime("%Y-%m-%dT%H:%M:%S"),
        category="Trash",
        description=random.choice(DESCRIPTIONS["Trash"]),
        latitude=exact_lat,
        longitude=exact_lng,
        barangay=brgy['name'],
        status="RESOLVED",
        scenario_tag="S04_decay_old"
    )
    complaints.append(old_complaint)
    
    print(f"   ✓ Created 2 Trash complaints (today + 90 days ago)")
    print(f"   Expected Result: IGNORE old data in clustering")
    
    return complaints


def generate_scenario_S08_mass_panic(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-08 (Mass Panic): 20x "Fire" in 10m radius within 60 seconds.
    
    Tests: Mass event detection (viral panic reporting)
    Expected: Should MERGE into single major incident
    """
    complaints = []
    
    brgy = random.choice(barangays)
    center_lat, center_lng = random_point_in_barangay(brgy)
    
    print(f"\n📍 S-08 (Mass Panic): 20x Fire in 10m radius, 60 seconds")
    print(f"   Barangay: {brgy['name']}")
    print(f"   Center: ({center_lat:.6f}, {center_lng:.6f})")
    
    for i in range(20):
        # Random position within 10m radius
        distance = random.uniform(0, 10)
        bearing = random.uniform(0, 360)
        lat, lng = offset_coordinates(center_lat, center_lng, distance, bearing)
        
        # Random time within 60 seconds
        seconds_offset = random.uniform(0, 60)
        timestamp = base_time + timedelta(seconds=seconds_offset)
        
        complaint = create_complaint(
            complaint_id=generate_id(),
            user_id=generate_user_id(),  # Different users (panic)
            timestamp=timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
            category="Fire",
            description=random.choice(DESCRIPTIONS["Fire"]),
            latitude=lat,
            longitude=lng,
            barangay=brgy['name'],
            scenario_tag="S08_mass_panic"
        )
        complaints.append(complaint)
    
    print(f"   ✓ Created 20 Fire complaints (10m radius, 60s window)")
    print(f"   Expected Result: MERGE (mass event detection)")
    
    return complaints


def generate_scenario_S12_spam_bot(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-12 (Spam Bot): 50 complaints. Random locs. Identical Timestamp (down to the ms).
    
    Tests: Bot/spam detection via impossible timing
    Expected: Should FLAG as suspicious (humanly impossible)
    """
    complaints = []
    
    # Exact timestamp down to millisecond
    exact_timestamp = base_time.strftime("%Y-%m-%dT%H:%M:%S.000")
    bot_user = "u_BOT_SPAM_001"
    categories = list(CATEGORY_EPSILON.keys())
    
    print(f"\n📍 S-12 (Spam Bot): 50 complaints with IDENTICAL timestamp")
    print(f"   Timestamp: {exact_timestamp}")
    print(f"   User: {bot_user}")
    
    for i in range(50):
        brgy = random.choice(barangays)
        lat, lng = random_point_in_barangay(brgy)
        category = random.choice(categories)
        
        complaint = create_complaint(
            complaint_id=generate_id(),
            user_id=bot_user,  # Same suspicious user
            timestamp=exact_timestamp,  # EXACT same timestamp (impossible)
            category=category,
            description=random.choice(DESCRIPTIONS.get(category, ["Test complaint"])),
            latitude=lat,
            longitude=lng,
            barangay=brgy['name'],
            scenario_tag="S12_spam_bot"
        )
        complaints.append(complaint)
    
    print(f"   ✓ Created 50 complaints with IDENTICAL timestamp")
    print(f"   Expected Result: FLAG as spam/bot activity")
    
    return complaints


def generate_scenario_S14_default_pin(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-14 (Default Pin): 10 complaints stacked at map center (0,0) or city center.
    
    Tests: Default/unset coordinates detection
    Expected: Should FLAG as invalid location data
    """
    complaints = []
    
    # Get city center as "default" location (could also use 0,0)
    all_centroids = [get_barangay_centroid(b) for b in barangays]
    default_lat = sum(c[0] for c in all_centroids) / len(all_centroids)
    default_lng = sum(c[1] for c in all_centroids) / len(all_centroids)
    
    print(f"\n📍 S-14 (Default Pin): 10 complaints at map center")
    print(f"   Default Location: ({default_lat:.6f}, {default_lng:.6f})")
    
    categories = list(CATEGORY_EPSILON.keys())
    
    for i in range(10):
        category = random.choice(categories)
        
        complaint = create_complaint(
            complaint_id=generate_id(),
            user_id=generate_user_id(),
            timestamp=random_timestamp(base_time, 48.0),  # Random over 2 days
            category=category,
            description=random.choice(DESCRIPTIONS.get(category, ["Test complaint"])),
            latitude=default_lat,  # All at default center
            longitude=default_lng,
            barangay="Unknown",  # No valid barangay
            scenario_tag="S14_default_pin"
        )
        complaints.append(complaint)
    
    print(f"   ✓ Created 10 complaints at default map center")
    print(f"   Expected Result: FLAG as default/unset location")
    
    return complaints


def generate_scenario_S15_null_data(base_time: datetime, barangays: List[Dict]) -> List[Dict]:
    """
    S-15 (Null Data): 1 record lat: null. 1 record category: null.
    
    Tests: Null/missing data handling
    Expected: Should handle gracefully without crashing
    """
    complaints = []
    
    brgy = random.choice(barangays)
    valid_lat, valid_lng = random_point_in_barangay(brgy)
    
    print(f"\n📍 S-15 (Null Data): Testing null values handling")
    
    # Record with null latitude
    null_lat_complaint = {
        "id": generate_id(),
        "user_id": generate_user_id(),
        "timestamp": base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "category": "Pothole",
        "description": "May lubak dito sa daan",
        "keywords": ["lubak"],
        "keyword_categories": ["Pothole"],
        "keyword_relevance": 0.8,
        "urgency": "medium",
        "latitude": None,  # NULL latitude
        "longitude": valid_lng,
        "status": "PENDING",
        "barangay": brgy['name'],
        "_scenario": "S15_null_lat"
    }
    complaints.append(null_lat_complaint)
    print(f"   ✓ Created complaint with NULL latitude")
    
    # Record with null category
    null_cat_complaint = {
        "id": generate_id(),
        "user_id": generate_user_id(),
        "timestamp": base_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "category": None,  # NULL category
        "description": "May problema dito pero di ko alam kung ano",
        "keywords": [],
        "keyword_categories": [],
        "keyword_relevance": 0.0,
        "urgency": "low",
        "latitude": valid_lat,
        "longitude": valid_lng,
        "status": "PENDING",
        "barangay": brgy['name'],
        "_scenario": "S15_null_cat"
    }
    complaints.append(null_cat_complaint)
    print(f"   ✓ Created complaint with NULL category")
    
    print(f"   Expected Result: Handle gracefully (no crash)")
    
    return complaints
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
    print("  CitizenLink - Synthetic Test Data Generator v3.0")
    print("  15 Test Scenarios + Random Complaints")
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
    base_time = datetime(2026, 1, 11, 10, 0, 0)
    
    all_complaints = []
    
    # ==================== GROUP A: SPATIAL LOGIC ====================
    print("\n" + "=" * 60)
    print("  GROUP A: SPATIAL LOGIC")
    print("=" * 60)
    
    all_complaints.extend(generate_scenario_S01_redundancy(base_time, barangays))
    all_complaints.extend(generate_scenario_S03_discrete(base_time + timedelta(hours=1), barangays))
    all_complaints.extend(generate_scenario_S07_precision_edge(base_time + timedelta(hours=2), barangays))
    all_complaints.extend(generate_scenario_S09_gps_drift(base_time + timedelta(hours=3), barangays))
    all_complaints.extend(generate_scenario_S13_moving_hazard(base_time + timedelta(hours=4), barangays))
    
    # ==================== GROUP B: SEMANTIC LOGIC ====================
    print("\n" + "=" * 60)
    print("  GROUP B: SEMANTIC LOGIC")
    print("=" * 60)
    
    all_complaints.extend(generate_scenario_S02_causal(base_time + timedelta(hours=5), barangays))
    all_complaints.extend(generate_scenario_S05_false_correlation(base_time + timedelta(hours=6), barangays))
    all_complaints.extend(generate_scenario_S06_domino_chain(base_time + timedelta(hours=7), barangays))
    all_complaints.extend(generate_scenario_S10_conflict(base_time + timedelta(hours=8), barangays))
    all_complaints.extend(generate_scenario_S11_synonyms(base_time + timedelta(hours=9), barangays))
    
    # ==================== GROUP C: DATA INTEGRITY ====================
    print("\n" + "=" * 60)
    print("  GROUP C: DATA INTEGRITY")
    print("=" * 60)
    
    all_complaints.extend(generate_scenario_S04_time_decay(base_time + timedelta(hours=10), barangays))
    all_complaints.extend(generate_scenario_S08_mass_panic(base_time + timedelta(hours=11), barangays))
    all_complaints.extend(generate_scenario_S12_spam_bot(base_time + timedelta(hours=12), barangays))
    all_complaints.extend(generate_scenario_S14_default_pin(base_time + timedelta(hours=13), barangays))
    all_complaints.extend(generate_scenario_S15_null_data(base_time + timedelta(hours=14), barangays))
    
    # Generate random complaints to pad the dataset
    scenario_count = len(all_complaints)
    random_count = random.randint(800, 1200) - scenario_count
    if random_count > 0:
        all_complaints.extend(generate_random_complaints(base_time, barangays, random_count))
    
    # Shuffle to mix scenarios with random data
    random.shuffle(all_complaints)
    
    # Re-assign sequential IDs for cleaner output
    for i, complaint in enumerate(all_complaints, 1):
        complaint["id"] = f"C-{i:04d}"
    
    # Calculate city center from all barangay centroids
    all_centroids = [get_barangay_centroid(b) for b in barangays]
    city_center_lat = sum(c[0] for c in all_centroids) / len(all_centroids)
    city_center_lng = sum(c[1] for c in all_centroids) / len(all_centroids)
    
    # Create output structure
    output = {
        "metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "generator": "CitizenLink Synthetic Data Generator v3.0",
            "total_records": len(all_complaints),
            "base_location": {
                "city": "Digos City",
                "latitude": round(city_center_lat, 6),
                "longitude": round(city_center_lng, 6)
            },
            "barangays": [b['name'] for b in barangays],
            "barangay_count": len(barangays),
            "test_scenarios": {
                "group_a_spatial": {
                    "S01_redundancy": "3x Pothole at exact same location (0m diff)",
                    "S03_discrete": "2x No Water exactly 15m apart (should NOT merge)",
                    "S07_precision_edge": "Center + 24.9m (merge) + 25.1m (no merge)",
                    "S09_gps_drift": "5x Streetlight from same user in 7m radius",
                    "S13_moving_hazard": "Stray Dog at 0m and 60m, 5 mins apart"
                },
                "group_b_semantic": {
                    "S02_causal": "Pipe Leak + Flood 10m apart (cause-effect)",
                    "S05_false_correlation": "Stray Dog + Pothole 1m apart (unrelated)",
                    "S06_domino_chain": "Pipe -> Flood -> Traffic cascade",
                    "S10_conflict": "Fire + Pothole at EXACT same location",
                    "S11_synonyms": "'Baha' vs 'Rising Water' 5m apart"
                },
                "group_c_integrity": {
                    "S04_time_decay": "2x Trash, today vs 90 days ago",
                    "S08_mass_panic": "20x Fire in 10m radius, 60 seconds",
                    "S12_spam_bot": "50 complaints with identical timestamp",
                    "S14_default_pin": "10 complaints at map center",
                    "S15_null_data": "Records with null lat/category"
                },
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
        cat = c.get("category") or "NULL"  # Handle null categories
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
