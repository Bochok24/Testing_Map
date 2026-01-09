# CitizenLink: System Simulation & Validation Dashboard
## Complete Technical Documentation v3.0

**Author:** CitizenLink Development Team  
**Date:** January 8, 2026  
**Purpose:** Thesis Defense Demonstration - Generalized DBSCAN Clustering Algorithm  
**Location:** Digos City, Philippines (6.7490°N, 125.3572°E)

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Core Algorithms](#3-core-algorithms)
4. [File Structure](#4-file-structure)
5. [Configuration Parameters](#5-configuration-parameters)
6. [Data Models](#6-data-models)
7. [Component Documentation](#7-component-documentation)
8. [UI Components](#8-ui-components)
9. [Scenario Test Cases](#9-scenario-test-cases)
10. [Implementation Details](#10-implementation-details)
11. [Usage Guide](#11-usage-guide)
12. [Development Notes](#12-development-notes)

---

## 1. System Overview

### 1.1 Purpose

CitizenLink is a **geospatial clustering validation dashboard** designed to demonstrate and validate the effectiveness of a **Generalized DBSCAN (Density-Based Spatial Clustering of Applications with Noise)** algorithm for citizen-reported municipal complaints.

The system addresses the challenge of **duplicate detection and complaint correlation** in civic reporting systems where multiple citizens may report related incidents (e.g., a pipe leak causing flooding in adjacent areas).

### 1.2 Key Features

- ✅ **Full System Scan Visualization**: Displays all 65+ data points simultaneously on map load
- ✅ **Adaptive Epsilon**: Category-specific distance thresholds (5m - 25m range)
- ✅ **Semantic Relationship Matrix**: Causal correlation modeling between complaint types
- ✅ **Temporal Windowing**: 48-hour time decay for complaint relevance
- ✅ **Spotlight/Dimming Effects**: Professional big-data visualization during scenario analysis
- ✅ **Real-time Logic Validation**: Step-by-step algorithm decision logging
- ✅ **5 Comprehensive Test Scenarios**: Covering edge cases and expected behaviors

### 1.3 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | Vanilla JavaScript | ES6+ |
| **Mapping** | Leaflet.js | 1.9.4 |
| **Tiles** | CartoDB Dark Matter | - |
| **Icons** | Font Awesome | 6.5.1 |
| **Data Format** | JSON | - |
| **Geospatial Math** | Haversine Formula | Custom |
| **Backend (Optional)** | Python 3.9+ | For data generation |

---

## 2. Architecture

### 2.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     DASHBOARD.HTML                          │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Sidebar   │  │  Map Canvas  │  │ Inspector Panel  │   │
│  │  Controls  │  │  (Leaflet)   │  │  (Live Metrics)  │   │
│  └────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ DOM Manipulation
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     DASHBOARD.JS                            │
│  • Map Initialization                                       │
│  • Event Listeners (Button clicks, keyboard shortcuts)      │
│  • Callbacks: addLog(), updateInspector(), updateStats()    │
│  • UI State Management                                      │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ API Calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  SIMULATION-ENGINE.JS                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  SimulationEngine Class                             │   │
│  │  • initialize()         - Load data, render points  │   │
│  │  • runScenario()        - Execute test case         │   │
│  │  • checkLogic()         - DBSCAN decision logic     │   │
│  │  • dimBackgroundMarkers() - Spotlight effect        │   │
│  │  • fullReset()          - Restore global scan       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Core Algorithms:                                          │
│  • haversineDistance()    - Geospatial distance calc       │
│  • checkSemanticRelation() - Category correlation          │
│  • getAdaptiveEpsilon()   - Dynamic epsilon lookup         │
│  • getTimeDifferenceHours() - Temporal validation          │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Fetch API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  MOCK_COMPLAINTS.JSON                       │
│  • 65 synthetic citizen complaints                          │
│  • 5 pre-configured test scenarios                          │
│  • Metadata: dataset info, generation timestamp             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
Page Load
    │
    ├──> Initialize Map (Leaflet)
    │
    ├──> Create SimulationEngine instance
    │       └──> Fetch mock_complaints.json
    │            └──> Render ALL points as background markers (gray, semi-transparent)
    │                 └──> Update Dataset Overview stats (65 records, High density, etc.)
    │
    └──> Wait for user action
            │
            └──> User clicks Scenario Button
                    │
                    ├──> Filter data by scenario prefix
                    │
                    ├──> Dim background markers (opacity: 0.3)
                    │
                    ├──> Create spotlight markers for target cluster
                    │
                    ├──> Pan/zoom map to cluster center
                    │
                    ├──> Run DBSCAN logic for each point pair
                    │       └──> Calculate distance (Haversine)
                    │       └──> Check semantic relation
                    │       └──> Validate temporal window
                    │       └──> Log decision (MERGE/REJECT)
                    │
                    └──> Display batch processing stats
                            └──> User can reset to full scan view
```

---

## 3. Core Algorithms

### 3.1 Haversine Distance Formula

**Purpose:** Calculate the great-circle distance between two points on Earth's surface.

**Mathematical Formula:**
```
a = sin²(Δφ/2) + cos(φ₁) × cos(φ₂) × sin²(Δλ/2)
c = 2 × atan2(√a, √(1−a))
d = R × c
```

Where:
- φ = latitude in radians
- λ = longitude in radians
- R = Earth's radius (6,371,000 meters)

**Implementation:**
```javascript
function haversineDistance(lat1, lon1, lat2, lon2) {
    const R = 6371000; // Earth radius in meters
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Returns distance in meters
}
```

**Accuracy:** ±0.5% for distances up to 1000km

### 3.2 Generalized DBSCAN Algorithm

**Traditional DBSCAN vs. CitizenLink DBSCAN:**

| Feature | Traditional DBSCAN | CitizenLink DBSCAN |
|---------|-------------------|-------------------|
| **Epsilon (ε)** | Fixed value | Adaptive per category |
| **Semantic Awareness** | None | Relationship matrix |
| **Temporal Constraint** | None | 48-hour window |
| **Correlation Scoring** | None | 0.0 - 1.0 scoring |

**Decision Logic Flowchart:**

```
                        Point A + Point B
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Calculate Distance │
                    │   (Haversine)       │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │ Get Adaptive Epsilon│
                    │ εₐ = ADAPTIVE_EPSILON[A.category] │
                    │ εᵦ = ADAPTIVE_EPSILON[B.category] │
                    │ ε = max(εₐ, εᵦ)     │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Distance ≤ ε ?     │
                    └─────────────────────┘
                         ▼              ▼
                      [NO]            [YES]
                        │               │
                        │               ▼
                        │      ┌─────────────────────┐
                        │      │ Check Semantic      │
                        │      │ Relation            │
                        │      │ RELATIONSHIP_MATRIX[A] │
                        │      │ contains B.category? │
                        │      └─────────────────────┘
                        │               │
                        │               ▼
                        │      ┌─────────────────────┐
                        │      │ Correlation Score   │
                        │      │ ≥ 0.50 ?            │
                        │      └─────────────────────┘
                        │          ▼              ▼
                        │        [NO]           [YES]
                        │          │              │
                        │          │              ▼
                        │          │     ┌─────────────────────┐
                        │          │     │ Calculate Time Diff │
                        │          │     │ |t₂ - t₁|           │
                        │          │     └─────────────────────┘
                        │          │              │
                        │          │              ▼
                        │          │     ┌─────────────────────┐
                        │          │     │ Time Diff ≤ 48h ?   │
                        │          │     └─────────────────────┘
                        │          │          ▼              ▼
                        │          │        [NO]           [YES]
                        │          │          │              │
                        ▼          ▼          ▼              ▼
                    ┌────────────────────────────────────────┐
                    │          DECISION OUTPUT               │
                    │  • Distance: X.XX m                    │
                    │  • Epsilon: XX m                       │
                    │  • Semantic Score: 0.XX                │
                    │  • Time Diff: XX.X hours               │
                    │  • Verdict: MERGED / REJECTED          │
                    └────────────────────────────────────────┘
```

**MERGE Conditions (ALL must be TRUE):**
1. `distance ≤ max(εₐ, εᵦ)`
2. `A.category → B.category` exists in RELATIONSHIP_MATRIX
3. `CORRELATION_SCORE ≥ 0.50`
4. `|t₂ - t₁| ≤ 48 hours`

### 3.3 Semantic Relationship Matrix

**Purpose:** Model causal and correlational relationships between complaint categories.

**Example:** A pipe leak (source) can cause:
- Flooding (92% correlation)
- No Water (85% correlation)
- Road Damage (45% correlation)

**Implementation:**
```javascript
const RELATIONSHIP_MATRIX = {
    "Pipe Leak": ["Flooding", "No Water", "Road Damage"],
    "Flooding": ["Pipe Leak", "Road Damage", "Trash"],
    "Pothole": ["Road Damage"],
    "Road Damage": ["Pothole", "Flooding"],
    "No Water": ["Pipe Leak"],
    "Trash": ["Illegal Dumping", "Stray Dog"],
    "Illegal Dumping": ["Trash", "Stray Dog"],
    "Stray Dog": [],
    "Broken Streetlight": [],
    "Noise Complaint": []
};

const CORRELATION_SCORES = {
    "Pipe Leak->Flooding": 0.92,    // Strong causal
    "Pipe Leak->No Water": 0.85,    // Strong causal
    "Pipe Leak->Road Damage": 0.45, // Weak causal (below threshold)
    "Flooding->Road Damage": 0.60,  // Moderate causal
    "Trash->Stray Dog": 0.25,       // Weak correlation (below threshold)
    // ... 14 total correlations defined
};

const CORRELATION_THRESHOLD = 0.50; // Minimum score for MERGE eligibility
```

**Relationship Types:**
- **IDENTICAL**: Same category (score = 1.0)
- **CAUSAL**: Related + score ≥ 0.50
- **WEAK**: Related + score < 0.50
- **NONE**: Not related

### 3.4 Adaptive Epsilon Strategy

**Rationale:** Different complaint types have different spatial characteristics.

**Examples:**
- **No Water**: 5m radius (affects specific households)
- **Pothole**: 10m radius (small road section)
- **Pipe Leak**: 15m radius (affects nearby area)
- **Flooding**: 25m radius (water spreads over large area)

**Full Configuration:**
```javascript
const ADAPTIVE_EPSILON = {
    "Pipe Leak": 15.0,         // Medium area impact
    "Flooding": 25.0,          // Largest area impact
    "Pothole": 10.0,           // Small area impact
    "No Water": 5.0,           // Smallest - specific homes
    "Trash": 8.0,              // Very localized
    "Stray Dog": 20.0,         // Animal can roam
    "Broken Streetlight": 12.0, // Single pole
    "Illegal Dumping": 15.0,   // Dump site area
    "Noise Complaint": 10.0,   // Sound localization
    "Road Damage": 12.0        // Road section
};
```

**Epsilon Selection Logic:**
```javascript
function getAdaptiveEpsilon(category) {
    return ADAPTIVE_EPSILON[category] || 10.0; // Default fallback
}

// When comparing two points:
const epsilonA = getAdaptiveEpsilon(pointA.category);
const epsilonB = getAdaptiveEpsilon(pointB.category);
const effectiveEpsilon = Math.max(epsilonA, epsilonB); // Use larger radius
```

### 3.5 Temporal Windowing

**Purpose:** Prevent merging of complaints that occurred too far apart in time.

**Window Size:** 48 hours (2 days)

**Rationale:**
- Recent reports likely refer to the same incident
- Old reports may have been resolved or are unrelated
- 48h balances recency with weekend reporting delays

**Implementation:**
```javascript
const MAX_TIME_DIFF_HOURS = 48;

function getTimeDifferenceHours(timestamp1, timestamp2) {
    const t1 = new Date(timestamp1);
    const t2 = new Date(timestamp2);
    return Math.abs(t2 - t1) / (1000 * 60 * 60); // Convert ms to hours
}

// Usage:
const timeDiff = getTimeDifferenceHours(pointA.timestamp, pointB.timestamp);
const temporalValid = (timeDiff <= MAX_TIME_DIFF_HOURS);
```

**Edge Cases:**
- ✅ Reports 1 hour apart → Valid
- ✅ Reports 47 hours apart → Valid
- ❌ Reports 49 hours apart → Invalid (REJECT)
- ❌ Reports 35 days apart → Invalid (Scenario 4 test case)

---

## 4. File Structure

```
ground_truth_tool/
│
├── dashboard.html              # Main UI entry point (187 lines)
├── dashboard.css               # Dark theme styling (626 lines)
├── dashboard.js                # Controller/event handlers (281 lines)
├── simulation-engine.js        # Core DBSCAN logic (982 lines)
├── useSimulationEngine.js      # React hook version (optional)
│
├── mock_complaints.json        # 65 test records + metadata
├── generate_mock_data.py       # Python data generator
│
├── brgy_boundaries_location.json   # Barangay boundaries (unused)
├── digos-city-boundary.json        # City boundary (unused)
│
├── README.md                   # Quick start guide
└── DOCUMENTATION.md            # This file
```

### 4.1 File Responsibilities

#### **dashboard.html**
- Semantic HTML5 structure
- Sidebar with Dataset Overview + 5 scenario buttons
- Map container (Leaflet renders here)
- Inspector panel (live metrics during simulation)
- Log panel (algorithm decisions)
- External dependencies (CDN links)

#### **dashboard.css**
- Dark theme design (professional/scientific aesthetic)
- Responsive layout (Flexbox)
- Animation keyframes (marker drops, pulses, fades)
- Color-coded elements (success=green, warning=yellow, error=red)
- Monospace fonts for data display

#### **dashboard.js**
- Map initialization (Leaflet instance)
- Event listeners (scenario buttons, reset button, keyboard shortcuts)
- Callback functions: `addLog()`, `updateInspector()`, `updateStats()`
- SimulationEngine instance creation
- UI state management

#### **simulation-engine.js**
- SimulationEngine class (main orchestrator)
- Core algorithms (Haversine, DBSCAN logic, semantic checks)
- Marker creation/management (background + spotlight)
- Scenario-specific implementations (runScenario1-5)
- Animation/timing control

#### **mock_complaints.json**
- 65 synthetic citizen complaints
- 5 scenario groups (each with 2-5 related points)
- ~40 background noise points (unrelated)
- Metadata (dataset name, generation timestamp, record counts)

---

## 5. Configuration Parameters

### 5.1 DBSCAN Parameters

```javascript
// Adaptive Epsilon (meters)
const ADAPTIVE_EPSILON = { /* 10 categories, 5m-25m */ };

// Semantic Relationships
const RELATIONSHIP_MATRIX = { /* 10 categories */ };

// Correlation Scores (0.0 - 1.0)
const CORRELATION_SCORES = { /* 14 defined pairs */ };

// Thresholds
const CORRELATION_THRESHOLD = 0.50;  // Minimum for MERGE
const MAX_TIME_DIFF_HOURS = 48;      // Temporal window
```

### 5.2 Animation Timing (milliseconds)

```javascript
const ANIMATION_CONFIG = {
    STEP_DELAY: 800,         // Delay between major steps
    MARKER_DROP: 400,        // Marker appearance animation
    SCAN_DURATION: 1200,     // Epsilon circle drawing
    LINE_DRAW: 400,          // Connection line animation
    LOG_DELAY: 200,          // Log message stagger
    BATCH_SCAN_DELAY: 50     // Fast batch simulation
};
```

### 5.3 Visual Configuration

```javascript
// Category Icons (Font Awesome)
const CATEGORY_ICONS = {
    "Pipe Leak": "droplet",
    "Flooding": "water",
    "Pothole": "road",
    "No Water": "faucet-drip",
    "Trash": "trash",
    "Stray Dog": "dog",
    "Broken Streetlight": "lightbulb",
    "Illegal Dumping": "dumpster",
    "Noise Complaint": "volume-up",
    "Road Damage": "road-barrier"
};

// Scenario Colors
const SCENARIO_CONFIG = {
    1: { color: "#10b981" }, // Green - Semantic Chain
    2: { color: "#3b82f6" }, // Blue - Duplicate Detection
    3: { color: "#ef4444" }, // Red - Discrete Neighbors
    4: { color: "#f59e0b" }, // Orange - Temporal Decay
    5: { color: "#8b5cf6" }  // Purple - False Positive
};
```

### 5.4 Map Configuration

```javascript
// Initial View
const MAP_CENTER = [6.7490, 125.3572]; // Digos City
const MAP_ZOOM = 14;

// Tile Layer
const TILE_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
const MAX_ZOOM = 19;
```

---

## 6. Data Models

### 6.1 Complaint Record Structure

```json
{
    "id": "C-001",
    "category": "Pipe Leak",
    "description": "Broken water pipe leaking water",
    "latitude": 6.74923,
    "longitude": 125.35732,
    "timestamp": "2026-01-08T14:30:00Z",
    "barangay": "Zone 1",
    "user_id": "user_045",
    "_scenario": "scenario_1_source",
    "_test_label": "Source Point - Pipe Leak"
}
```

**Field Definitions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | String | Yes | Unique identifier (C-001 to C-065) |
| `category` | String | Yes | Complaint type (10 possible values) |
| `description` | String | Yes | Human-readable description |
| `latitude` | Number | Yes | WGS84 latitude (6.74xxx range) |
| `longitude` | Number | Yes | WGS84 longitude (125.35xxx range) |
| `timestamp` | ISO8601 | Yes | Report timestamp (UTC) |
| `barangay` | String | No | District name |
| `user_id` | String | No | Reporter identifier |
| `_scenario` | String | No | Test scenario tag (scenario_1_source, etc.) |
| `_test_label` | String | No | Human-readable test description |

### 6.2 Metadata Structure

```json
{
    "dataset_name": "CitizenLink Mock Dataset v1.0",
    "generated_at": "2026-01-08T10:30:00Z",
    "total_records": 65,
    "scenario_counts": {
        "scenario_1": 5,
        "scenario_2": 3,
        "scenario_3": 2,
        "scenario_4": 2,
        "scenario_5": 2
    },
    "background_noise": 51
}
```

### 6.3 Logic Check Result

```javascript
{
    shouldMerge: true,              // Final decision
    distance: 12.45,                // Meters
    epsilon: 15.0,                  // Adaptive epsilon used
    timeDiff: 2.5,                  // Hours
    semantic: {
        isRelated: true,
        score: 0.92,
        relationship: "CAUSAL"
    },
    reasons: [],                    // Empty if merge, populated if reject
    verdict: "MERGED"               // "MERGED" or "REJECTED"
}
```

### 6.4 Stats Update Object

```javascript
{
    datasetName: "CitizenLink Mock Dataset v1.0",
    totalRecords: 65,
    pendingValidation: 65,
    densityScore: "High",          // "High" | "Medium" | "Low"
    processingMode: "focused"      // "global" | "focused"
}
```

---

## 7. Component Documentation

### 7.1 SimulationEngine Class

#### Constructor
```javascript
constructor(mapInstance, logCallback, inspectorCallback, statsCallback)
```

**Parameters:**
- `mapInstance`: Leaflet Map object
- `logCallback`: Function to add log messages
- `inspectorCallback`: Function to update inspector panel
- `statsCallback`: Function to update dataset stats

**Example:**
```javascript
const engine = new SimulationEngine(
    map,
    (msg, type) => addLog(msg, type),
    (data) => updateInspector(data),
    (stats) => updateStats(stats)
);
```

#### Key Methods

##### `async initialize()`
Loads `mock_complaints.json`, renders all background markers, updates stats.

**Returns:** `boolean` (success/failure)

**Side Effects:**
- Populates `this.complaints` array
- Creates 65 gray background markers
- Calls `updateStats()` with dataset info
- Logs initialization messages

##### `async runScenario(scenarioNumber)`
Executes a test scenario (1-5).

**Parameters:** `scenarioNumber` (1-5)

**Process:**
1. Filter complaints by scenario prefix
2. Log batch processing header
3. Dim background markers
4. Create spotlight markers for target cluster
5. Pan/zoom map to cluster
6. Execute scenario-specific logic
7. Display batch indicator

**Returns:** `void` (async)

##### `checkLogic(pointA, pointB)`
Core DBSCAN decision function.

**Parameters:** Two complaint objects

**Returns:** Logic check result object (see Data Models)

**Algorithm:**
1. Calculate Haversine distance
2. Get adaptive epsilon (max of both points)
3. Check semantic relation
4. Calculate time difference
5. Validate all conditions
6. Return verdict + detailed metrics

##### `dimBackgroundMarkers(exceptIds)`
Reduces opacity of all markers except specified IDs.

**Parameters:** `exceptIds` (array of complaint IDs)

**Effect:** Sets opacity to 0.3 for background markers, removes scenario tags

##### `resetBackgroundMarkers()`
Restores all markers to normal visibility.

**Effect:** Sets opacity to 1.0, reapplies `background-marker` CSS class

##### `fullReset()`
Complete reset to initial state.

**Process:**
1. Clear scenario elements (markers, circles, lines)
2. Reset background markers
3. Update processing mode to "global"
4. Fit map to all points

##### `renderAllPoints()`
Creates initial gray markers for all complaints.

**Called By:** `initialize()`

**Creates:** 65 small semi-transparent circle markers

##### `createSpotlightMarker(complaint, color, scale)`
Creates a highlighted marker during scenario analysis.

**Parameters:**
- `complaint`: Complaint object
- `color`: Hex color code
- `scale`: Size multiplier (1.0 = normal)

**Returns:** Leaflet Marker instance

**Visual:** Pulsing animation, glow effect, Font Awesome icon

##### `createBackgroundMarker(complaint)`
Creates a small gray marker for full system scan.

**Parameters:** `complaint` object

**Returns:** Leaflet CircleMarker instance

**Visual:** 4px radius, 30% opacity, gray color

##### `showBatchIndicator(scanned, ignored, focused)`
Displays batch processing stats overlay.

**Parameters:**
- `scanned`: Total points scanned
- `ignored`: Points filtered out
- `focused`: Points in target cluster

**Visual:** Top-right overlay, auto-hides after scenario

---

### 7.2 Dashboard Controller Functions

#### `initMap()`
Initializes Leaflet map instance.

**Configuration:**
- Center: Digos City (6.7490, 125.3572)
- Zoom: 14
- Tiles: CartoDB Dark Matter
- Controls: Scale, Attribution

**Returns:** `void`

#### `addLog(message, type)`
Adds a log message to the log panel.

**Parameters:**
- `message`: String text
- `type`: 'info' | 'logic' | 'success' | 'warning' | 'error' | 'system'

**Effect:** Appends styled div to log content, auto-scrolls

#### `clearLog()`
Resets log panel to initial welcome messages.

#### `updateStats(stats)`
Updates Dataset Overview panel.

**Parameters:** Stats object (see Data Models)

**Updates:**
- Dataset Name
- Total Records (highlighted)
- Pending Validation
- Density Score (color-coded)
- Processing Mode (icon changes)

#### `updateInspector(data)`
Updates Inspector Panel with live metrics.

**Parameters:**
```javascript
{
    category: "Pipe Leak",
    epsilon: "15.0m",
    timeDiff: "2.5h",
    semantic: "0.92",
    verdict: "MERGED"
}
```

#### `resetSimulation()`
Resets entire dashboard to initial state.

**Actions:**
1. Call `engine.fullReset()`
2. Clear log panel
3. Hide inspector
4. Remove active states from buttons
5. Reset map view

#### `showStatus(message, duration)`
Shows temporary status overlay message.

**Parameters:**
- `message`: Status text
- `duration`: Display time in ms (default: 3000)

**Example:** `showStatus('✅ Full System Scan Active', 2500)`

---

## 8. UI Components

### 8.1 Sidebar Layout

```
┌─────────────────────────────────┐
│   📊 DATASET OVERVIEW          │
├─────────────────────────────────┤
│ 🗄️  Active Dataset             │
│     CitizenLink Mock Dataset    │
│                                 │
│ 📚 Total Records: 65            │
│ ⏳ Pending Validation: 65       │
│ 📈 Density Score: High          │
│                                 │
│ 🌐 Processing Mode:             │
│     Global Scan                 │
├─────────────────────────────────┤
│   🧪 TEST SCENARIOS            │
├─────────────────────────────────┤
│ 1️⃣  Semantic Chain              │
│     Pipe → Flood                │
│                                 │
│ 2️⃣  Duplicate Detection         │
│     Same user, same location    │
│                                 │
│ 3️⃣  Discrete Neighbors          │
│     Distance > epsilon          │
│                                 │
│ 4️⃣  Temporal Decay              │
│     35 days apart               │
│                                 │
│ 5️⃣  False Positive Block        │
│     Unrelated categories        │
├─────────────────────────────────┤
│      [🔄 RESET SIMULATION]     │
└─────────────────────────────────┘
```

### 8.2 Inspector Panel

```
┌─────────────────────────────────┐
│   🔍 CLUSTER INSPECTOR     [×]  │
├─────────────────────────────────┤
│   Point Information             │
│   • Category: Pipe Leak         │
│   • Epsilon: 15.0m              │
│   • Time Diff: 2.5h             │
│   • Semantic: 0.92              │
├─────────────────────────────────┤
│   Logic Verdict                 │
│   ✅ MERGED                     │
└─────────────────────────────────┘
```

### 8.3 Log Panel

```
┌─────────────────────────────────┐
│   📝 SIMULATION LOG            │
├─────────────────────────────────┤
│ [SYSTEM] CitizenLink Ready      │
│ [INFO] 65 points rendered       │
│ ═════════════════════════        │
│ [SCAN] Processing Batch #347    │
│ [SCAN] Scanned 65 points        │
│ [FILTER] Ignored 60 points      │
│ [FOCUS] Analyzing C-001, C-023  │
│ ─────────────────────────        │
│ [CALC] Distance: 12.45m         │
│ [CALC] Semantic: 0.92           │
│ [DECISION] ✅ MERGED            │
└─────────────────────────────────┘
```

### 8.4 Map Visualizations

#### Background Markers (Full System Scan)
- **Appearance:** Small gray circles (4px radius)
- **Opacity:** 30%
- **Purpose:** Show dataset scope

#### Spotlight Markers (Scenario Analysis)
- **Appearance:** Large colored icons (40px)
- **Animation:** Pulsing glow effect
- **Colors:** Scenario-specific (green, blue, red, orange, purple)
- **Icon:** Category-specific Font Awesome icon

#### Epsilon Circles
- **Appearance:** Dashed circle border
- **Fill:** Semi-transparent (12% opacity)
- **Color:** Matches marker color
- **Purpose:** Visualize search radius

#### Connection Lines
- **Appearance:** Solid or dashed lines
- **Color:** Green (MERGE) or Red (REJECT)
- **Weight:** 3px
- **Purpose:** Show point relationships

#### Batch Indicator
```
┌──────────────────────────┐
│  BATCH PROCESSING       │
│  Scanned: 65            │
│  Ignored: 60            │
│  Focused: 5             │
└──────────────────────────┘
```

---

## 9. Scenario Test Cases

### 9.1 Scenario 1: Semantic Chain (Pipe → Flood)

**Objective:** Validate causal correlation detection

**Setup:**
- 1 source point: C-001 [Pipe Leak] at (6.74923, 125.35732)
- 4 flood points: C-023, C-034, C-041, C-054 [Flooding]
- All within 15m radius
- All within 1-4 hours

**Expected Result:** All floods MERGE with source

**Validation:**
- ✅ Distance ≤ 15m (Pipe Leak epsilon)
- ✅ Semantic: Pipe Leak → Flooding = 0.92
- ✅ Time: < 48 hours

**Visual:**
```
     [Pipe]
    /  |  \  \
   /   |   \  \
[Flood][Flood][Flood][Flood]
```

**Log Output:**
```
[CALC] Distance: 12.45m | Threshold: 15m
[CALC] Semantic: Pipe Leak → Flooding = 0.92
[DECISION] ✅ MERGED (Causal correlation detected)
```

---

### 9.2 Scenario 2: Duplicate Detection

**Objective:** Identify spam/redundant reports

**Setup:**
- 3 identical reports from same user: C-002, C-011, C-026
- Same category: Pothole
- Same location: (6.74891, 125.35768)
- Within 15 minutes

**Expected Result:** All three MERGE (duplicates)

**Validation:**
- ✅ Distance = 0m
- ✅ Same category (semantic score = 1.0)
- ✅ Time: < 48 hours

**Visual:**
```
   [Pothole]
   [Pothole]  ← Same location
   [Pothole]
```

**Use Case:** Prevent multiple tickets for same issue

---

### 9.3 Scenario 3: Discrete Neighbors

**Objective:** Reject points beyond epsilon threshold

**Setup:**
- 2 trash reports: C-003, C-013
- Distance: 22 meters apart
- Epsilon for Trash: 8m
- Within 1 hour

**Expected Result:** REJECT (distance too great)

**Validation:**
- ❌ Distance 22m > epsilon 8m
- ✅ Same category
- ✅ Time valid

**Visual:**
```
[Trash] ←──── 22m ────→ [Trash]
        (Epsilon: 8m)
```

**Log Output:**
```
[CALC] Distance: 22.0m | Threshold: 8m
[REASON] Distance exceeds epsilon
[DECISION] ❌ REJECTED
```

---

### 9.4 Scenario 4: Temporal Decay

**Objective:** Reject old reports (> 48h)

**Setup:**
- 2 streetlight reports: C-004, C-016
- Distance: 5m (well within epsilon)
- Same category: Broken Streetlight
- Time difference: **35 days** (840 hours)

**Expected Result:** REJECT (too old)

**Validation:**
- ✅ Distance valid
- ✅ Semantic valid (same category)
- ❌ Time: 840h > 48h

**Visual:**
```
[Streetlight]           [Streetlight]
Jan 1, 2026            Feb 5, 2026
     ←──── 35 days ────→
```

**Rationale:** Old reports likely resolved or unrelated

---

### 9.5 Scenario 5: False Positive Block

**Objective:** Prevent merging unrelated categories

**Setup:**
- 2 points: C-005 [Stray Dog], C-018 [Noise Complaint]
- Distance: 8m (within typical epsilon)
- Within 2 hours

**Expected Result:** REJECT (no semantic relation)

**Validation:**
- ✅ Distance valid
- ❌ No semantic relation (score = 0.0)
- ✅ Time valid

**Visual:**
```
[Stray Dog] ←── 8m ──→ [Noise Complaint]
   (No causal relationship)
```

**Log Output:**
```
[CALC] Semantic: Stray Dog → Noise Complaint = 0.00
[REASON] No semantic correlation
[DECISION] ❌ REJECTED
```

---

## 10. Implementation Details

### 10.1 Marker Management

**Two-Layer System:**

1. **Background Layer** (persistent):
   - 65 gray circle markers
   - Created once on page load
   - Remain on map during all scenarios
   - Dimmed during analysis (opacity: 0.3)

2. **Spotlight Layer** (temporary):
   - Created per scenario
   - Large colored icons with animations
   - Cleared on reset
   - Overlay background markers

**Memory Management:**
```javascript
// Background markers stored in Map
this.backgroundMarkers = new Map(); // id -> marker

// Scenario markers in array (cleared after each scenario)
this.scenarioMarkers = []; // [marker1, marker2, ...]
this.circles = [];          // [circle1, circle2, ...]
this.lines = [];            // [line1, line2, ...]
```

### 10.2 Animation Sequencing

**Example: Scenario 1 Timeline**

```
0ms     ═══════════════════════════════════════
        [LOG] Batch processing initiated

800ms   [LOG] Scanned 65 points
        
1100ms  [LOG] Ignored 60 points

1400ms  [LOG] Focus on target cluster

1600ms  [MAP] Dim background markers

2800ms  [MAP] Pan/zoom to cluster center
        [BATCH INDICATOR] Display stats

4000ms  [MARKER] Drop source marker
        [LOG] Source detected

4400ms  [CIRCLE] Draw epsilon circle

5600ms  [MARKER] Drop first flood marker

6000ms  [LINE] Draw connection line

6200ms  [LOG] Distance calculation
        [LOG] Semantic calculation
        [LOG] Decision: MERGED

6600ms  [MARKER] Drop second flood marker
        ...
```

**Implementation:**
```javascript
await this.delay(ANIMATION_CONFIG.STEP_DELAY);
```

### 10.3 Performance Optimization

**Strategies:**
1. **Lazy Loading**: Only fetch JSON once on init
2. **Efficient Filtering**: Use `.filter()` for scenario data
3. **Marker Reuse**: Background markers never destroyed
4. **CSS Transitions**: Hardware-accelerated animations
5. **Debouncing**: Prevent rapid scenario switching

**Bottlenecks:**
- ❌ Creating 65 new markers per scenario (old approach)
- ✅ Reusing 65 background markers, only adding 2-5 spotlights (new approach)

### 10.4 Error Handling

```javascript
// Data loading
async function loadMockData() {
    try {
        const response = await fetch('mock_complaints.json');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('[DATA LOADER] Failed:', error);
        throw error;
    }
}

// Initialization
const success = await simulationEngine.initialize();
if (success) {
    showStatus('✅ Full System Scan Active', 2500);
} else {
    showStatus('❌ Failed to Load Data - Check console', 4000);
}
```

### 10.5 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `1` | Run Scenario 1 |
| `2` | Run Scenario 2 |
| `3` | Run Scenario 3 |
| `4` | Run Scenario 4 |
| `5` | Run Scenario 5 |
| `R` | Reset simulation |
| `Esc` | Close inspector panel |

**Implementation:**
```javascript
document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    if (e.key >= '1' && e.key <= '5') {
        const btn = document.querySelector(`[data-scenario="${e.key}"]`);
        if (btn) btn.click();
    }
    
    if (e.key === 'r' || e.key === 'R') {
        resetSimulation();
    }
    
    if (e.key === 'Escape') {
        hideInspector();
    }
});
```

---

## 11. Usage Guide

### 11.1 Quick Start

1. **Open Dashboard:**
   ```bash
   # Navigate to project folder
   cd ground_truth_tool
   
   # Open in browser (use Live Server recommended)
   # Or double-click dashboard.html
   ```

2. **Initial View:**
   - Map displays 65 gray markers (full dataset)
   - Sidebar shows "Dataset Overview" stats
   - Processing Mode: "Global Scan"

3. **Run a Scenario:**
   - Click any scenario button (1-5) or press number key
   - Watch log panel for algorithm decisions
   - Observe map animations (dim, spotlight, zoom)

4. **Reset:**
   - Click "Reset Simulation" or press `R`
   - Returns to full scan view

### 11.2 Demo Script (Thesis Defense)

**Slide 1: Introduction (30 seconds)**
> "CitizenLink uses Generalized DBSCAN to detect duplicate and related complaints. This dashboard demonstrates 5 key test scenarios."

**Slide 2: Full System Scan (30 seconds)**
> "Initially, all 65 data points are visible—simulating a large municipal dataset. Gray markers represent the full complaint corpus."

**Action:** Point to map, show Dataset Overview stats

**Slide 3: Scenario 1 - Semantic Chain (2 minutes)**
> "Scenario 1 tests causal correlation. A pipe leak can cause flooding nearby."

**Action:** Press `1` or click Scenario 1 button

> "Notice: Background dims, spotlight highlights the cluster. The algorithm calculates Haversine distance, checks the semantic relationship matrix—Pipe Leak to Flooding has 0.92 correlation—validates temporal window, and merges all flood reports."

**Highlight:** Log panel showing calculations, Inspector panel showing metrics

**Slide 4: Scenario 3 - Discrete Neighbors (2 minutes)**
> "Scenario 3 demonstrates epsilon threshold rejection. Two trash reports are 22 meters apart, but the adaptive epsilon for trash is only 8 meters."

**Action:** Press `R` to reset, then press `3`

> "The algorithm rejects the merge despite being the same category, because distance exceeds the threshold."

**Slide 5: Scenario 4 - Temporal Decay (1.5 minutes)**
> "Scenario 4 shows temporal windowing. Two streetlight reports are 35 days apart—far exceeding our 48-hour window."

**Action:** Press `R`, then press `4`

> "Even though distance and category match, the time difference triggers a rejection."

**Slide 6: Conclusion (30 seconds)**
> "The Generalized DBSCAN successfully handles edge cases through adaptive epsilon, semantic awareness, and temporal constraints."

### 11.3 Troubleshooting

| Issue | Solution |
|-------|----------|
| Map not loading | Check console for tile errors, verify internet connection |
| No markers visible | Open console, check for JSON fetch errors |
| Buttons not responding | Check `simulationEngine.isRunning` flag, wait for current scenario to finish |
| Inspector not updating | Verify `updateInspector` callback is passed to SimulationEngine |
| Stats not updating | Verify `updateStats` callback is passed to SimulationEngine |

**Console Debug Commands:**
```javascript
// Access engine instance
window.debugCitizenLink.getEngine()

// Test Haversine calculation
window.debugCitizenLink.testHaversine(6.749, 125.357, 6.750, 125.358)

// View all configuration
window.debugCitizenLink.showConfig()
```

---

## 12. Development Notes

### 12.1 Design Decisions

**Why Vanilla JavaScript instead of React?**
- ✅ Faster loading (no framework overhead)
- ✅ Easier to demonstrate algorithm logic (no abstractions)
- ✅ Self-contained (no build process)
- ✅ Better for thesis defense (inspect code directly)

**Why Full System Scan approach?**
- ✅ Shows dataset scale immediately
- ✅ Professional "big data" aesthetic
- ✅ Spotlight effect emphasizes target cluster
- ✅ Aligns with real-world system behavior (scan all, filter, focus)

**Why 5 specific scenarios?**
- ✅ Scenario 1: Core functionality (merge related)
- ✅ Scenario 2: Edge case (duplicates)
- ✅ Scenario 3: Spatial rejection (distance)
- ✅ Scenario 4: Temporal rejection (time)
- ✅ Scenario 5: Semantic rejection (unrelated)
- ✅ Covers all decision branches in DBSCAN logic

### 12.2 Known Limitations

1. **No Backend:**
   - All data is static JSON
   - No database persistence
   - No real-time updates

2. **Simplified DBSCAN:**
   - Only pairwise comparisons (not full cluster detection)
   - No MinPts parameter (assumes 2)
   - No noise point classification

3. **Hardcoded Configuration:**
   - ADAPTIVE_EPSILON not dynamically tunable
   - RELATIONSHIP_MATRIX requires code edit to modify
   - Scenario definitions hardcoded

4. **Performance:**
   - Not optimized for > 1000 points
   - Animation delays slow down at scale
   - No spatial indexing (linear search)

### 12.3 Future Enhancements

**Phase 2 Features:**
- [ ] Admin panel to adjust epsilon values
- [ ] Custom scenario builder
- [ ] Export cluster results as JSON/CSV
- [ ] Heat map overlay for density visualization
- [ ] Multi-cluster detection (beyond pairwise)
- [ ] Real-time data integration (WebSocket)
- [ ] User authentication
- [ ] Historical data playback

**Research Extensions:**
- [ ] Machine learning for correlation score tuning
- [ ] Predictive clustering (forecast complaint hotspots)
- [ ] Sentiment analysis integration
- [ ] Multi-city comparison dashboard

### 12.4 Version History

**v1.0** (Initial)
- Basic DBSCAN implementation
- 5 scenario buttons
- Single point marker approach

**v2.0** (Semantic Enhancement)
- Added RELATIONSHIP_MATRIX
- Correlation scoring
- Temporal windowing
- Inspector panel

**v3.0** (Full System Scan) ← Current
- Background marker layer
- Spotlight/dimming effects
- Dataset Overview stats
- Batch processing visualization
- Performance optimizations

### 12.5 Code Quality

**Metrics:**
- Total Lines: ~2,176 (HTML + CSS + JS)
- Function Count: 38
- Class Count: 1 (SimulationEngine)
- Test Scenarios: 5
- Mock Data Records: 65

**Standards:**
- ✅ ES6+ syntax
- ✅ JSDoc comments on key functions
- ✅ Semantic HTML5
- ✅ BEM-inspired CSS naming
- ✅ Async/await for asynchronous operations
- ✅ Error handling with try/catch

### 12.6 Credits & References

**Algorithms:**
- DBSCAN: Ester, M., et al. (1996). "A Density-Based Algorithm for Discovering Clusters"
- Haversine: R.W. Sinnott (1984). "Virtues of the Haversine"

**Technologies:**
- Leaflet.js: [leafletjs.com](https://leafletjs.com)
- CartoDB: [carto.com](https://carto.com)
- Font Awesome: [fontawesome.com](https://fontawesome.com)

**Location Data:**
- Digos City, Philippines: OpenStreetMap contributors

---

## Appendix A: Complete Configuration Reference

```javascript
// ==================== ADAPTIVE EPSILON ====================
const ADAPTIVE_EPSILON = {
    "Pipe Leak": 15.0,
    "Flooding": 25.0,
    "Pothole": 10.0,
    "No Water": 5.0,
    "Trash": 8.0,
    "Stray Dog": 20.0,
    "Broken Streetlight": 12.0,
    "Illegal Dumping": 15.0,
    "Noise Complaint": 10.0,
    "Road Damage": 12.0
};

// ==================== RELATIONSHIP MATRIX ====================
const RELATIONSHIP_MATRIX = {
    "Pipe Leak": ["Flooding", "No Water", "Road Damage"],
    "Flooding": ["Pipe Leak", "Road Damage", "Trash"],
    "Pothole": ["Road Damage"],
    "Road Damage": ["Pothole", "Flooding"],
    "No Water": ["Pipe Leak"],
    "Trash": ["Illegal Dumping", "Stray Dog"],
    "Illegal Dumping": ["Trash", "Stray Dog"],
    "Stray Dog": [],
    "Broken Streetlight": [],
    "Noise Complaint": []
};

// ==================== CORRELATION SCORES ====================
const CORRELATION_SCORES = {
    "Pipe Leak->Flooding": 0.92,
    "Pipe Leak->No Water": 0.85,
    "Pipe Leak->Road Damage": 0.45,
    "Flooding->Pipe Leak": 0.88,
    "Flooding->Road Damage": 0.60,
    "Flooding->Trash": 0.30,
    "Pothole->Road Damage": 0.75,
    "Road Damage->Pothole": 0.75,
    "Road Damage->Flooding": 0.40,
    "No Water->Pipe Leak": 0.80,
    "Trash->Illegal Dumping": 0.70,
    "Trash->Stray Dog": 0.25,
    "Illegal Dumping->Trash": 0.70,
    "Illegal Dumping->Stray Dog": 0.35
};

// ==================== THRESHOLDS ====================
const CORRELATION_THRESHOLD = 0.50;
const MAX_TIME_DIFF_HOURS = 48;

// ==================== ANIMATION CONFIG ====================
const ANIMATION_CONFIG = {
    STEP_DELAY: 800,
    MARKER_DROP: 400,
    SCAN_DURATION: 1200,
    LINE_DRAW: 400,
    LOG_DELAY: 200,
    BATCH_SCAN_DELAY: 50
};

// ==================== CATEGORY ICONS ====================
const CATEGORY_ICONS = {
    "Pipe Leak": "droplet",
    "Flooding": "water",
    "Pothole": "road",
    "No Water": "faucet-drip",
    "Trash": "trash",
    "Stray Dog": "dog",
    "Broken Streetlight": "lightbulb",
    "Illegal Dumping": "dumpster",
    "Noise Complaint": "volume-up",
    "Road Damage": "road-barrier"
};

// ==================== SCENARIO CONFIG ====================
const SCENARIO_CONFIG = {
    1: {
        name: "Semantic Chain (Pipe → Flood)",
        prefix: "scenario_1",
        description: "Tests causal correlation: Pipe Leak causes Flooding",
        expectedResult: "MERGE",
        color: "#10b981"
    },
    2: {
        name: "Duplicate Detection",
        prefix: "scenario_2",
        description: "Tests spam/redundancy: Same user, same location",
        expectedResult: "MERGE",
        color: "#3b82f6"
    },
    3: {
        name: "Discrete Neighbors",
        prefix: "scenario_3",
        description: "Tests epsilon threshold: Distance > category limit",
        expectedResult: "SEPARATE",
        color: "#ef4444"
    },
    4: {
        name: "Temporal Decay",
        prefix: "scenario_4",
        description: "Tests time window: Report too old (35 days)",
        expectedResult: "SEPARATE",
        color: "#f59e0b"
    },
    5: {
        name: "False Positive Block",
        prefix: "scenario_5",
        description: "Tests semantic rejection: Unrelated categories",
        expectedResult: "SEPARATE",
        color: "#8b5cf6"
    }
};
```

---

## Appendix B: Mock Data Generation

The `generate_mock_data.py` script creates realistic test data:

**Process:**
1. Define Digos City center coordinates
2. Generate 5 scenario clusters (14 total points)
3. Generate 51 background noise points
4. Add realistic metadata (timestamps, barangays, user IDs)
5. Export to `mock_complaints.json`

**Key Functions:**
- `random_offset(radius_meters)`: Generate random lat/lng within radius
- `random_timestamp(hours_ago_min, hours_ago_max)`: Generate timestamps within range
- `generate_scenario_X()`: Create scenario-specific point clusters

**Usage:**
```bash
python generate_mock_data.py
# Output: mock_complaints.json (65 records)
```

---

## Appendix C: CSS Animation Keyframes

```css
/* Marker Drop Animation */
@keyframes markerDrop {
    0% {
        transform: translateY(-20px) scale(0.8);
        opacity: 0;
    }
    100% {
        transform: translateY(0) scale(1);
        opacity: 1;
    }
}

/* Pulse Glow Animation */
@keyframes pulse {
    0%, 100% {
        box-shadow: 0 0 10px currentColor;
    }
    50% {
        box-shadow: 0 0 25px currentColor;
    }
}

/* Fade In Animation */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Spotlight Grow Animation */
@keyframes spotlightGrow {
    0% {
        transform: scale(0.5);
        opacity: 0;
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}
```

---

## Appendix D: Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully Supported |
| Firefox | 88+ | ✅ Fully Supported |
| Safari | 14+ | ✅ Fully Supported |
| Edge | 90+ | ✅ Fully Supported |
| Opera | 76+ | ✅ Fully Supported |
| IE 11 | - | ❌ Not Supported (ES6+) |

**Required Features:**
- ES6 modules (import/export)
- Async/await
- Fetch API
- CSS Grid & Flexbox
- CSS Variables
- CSS Animations

---

## Appendix E: Contact & Support

**Project:** CitizenLink - System Simulation & Validation Dashboard  
**Version:** 3.0  
**Date:** January 8, 2026  
**Location:** Digos City, Philippines

**For questions or support:**
- Review this documentation
- Check console for error messages
- Use `window.debugCitizenLink` utilities
- Inspect source code (well-commented)

---

**End of Documentation**

*This dashboard is designed for thesis defense demonstration purposes. All data is synthetic. The algorithms and visualizations accurately represent the Generalized DBSCAN clustering approach.*
