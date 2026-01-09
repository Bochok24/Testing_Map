# CitizenLink - Thesis Defense Dashboard

**Full System Scan Visualization for Generalized DBSCAN Clustering Algorithm**

A sophisticated web-based dashboard for visualizing and demonstrating the Generalized DBSCAN clustering algorithm with semantic correlation, adaptive epsilon, and temporal filtering. Built for thesis defense presentation with realistic complaint data distributed across Digos City's 26 barangays.

---

## 🎯 Overview

This project implements a complete visualization system for demonstrating how a Generalized DBSCAN algorithm processes citizen complaints with:
- **Semantic Correlation**: Understands relationships between complaint categories (e.g., Pipe Leak → Flooding)
- **Adaptive Epsilon**: Different distance thresholds per category (5m for "No Water", 25m for "Flooding")
- **Temporal Filtering**: Filters old data (ignores complaints older than 30 days)
- **Geographic Boundaries**: Complaints generated within actual Digos City barangay polygons
- **Stacking Visualization**: Facebook-style notification badges for overlapping complaints

---

## ✨ Key Features

### 1. **Two-Layer Visualization System**
- **Background Layer**: All 500+ complaints shown as gray dots (persistent, never destroyed)
- **Spotlight Layer**: Scenario-specific colorful markers with animations (temporary, cleared after each scenario)
- **Smart Dimming**: Background fades to 15% opacity during scenario analysis

### 2. **Interactive Scenario Testing**
Five built-in test scenarios demonstrating different clustering behaviors:
- **Scenario 1**: Semantic Chain (Pipe Leak → Flooding) - Tests causal correlation
- **Scenario 2**: Duplicate Spammer - Tests redundancy detection
- **Scenario 3**: Discrete Neighbors - Tests category-specific epsilon thresholds
- **Scenario 4**: Old News - Tests temporal filtering (35-day old data ignored)
- **Scenario 5**: False Positive - Tests semantic rejection (unrelated categories)

### 3. **Geographic Accuracy**
- **26 Barangay Boundaries**: Visual polygon outlines with color-coding
- **Real Boundaries**: Complaints generated inside actual barangay polygons using point-in-polygon algorithm
- **Barangay Attribution**: Each complaint tagged with its barangay name
- **Hover Labels**: Tooltips show barangay names on boundary hover

### 4. **Advanced Map Features**
- **Deep Zoom**: Supports zoom levels up to 22 (20m+ precision)
- **Zoom-Responsive Markers**: Markers shrink at higher zoom levels (4px → 2px)
- **Instant Rendering**: No animation lag when zooming
- **Stacked Complaints**: Red notification badges show count when multiple complaints share exact coordinates

### 5. **Professional Dashboard UI**
- **Dark Theme**: High-contrast dark interface for presentations
- **Live Console**: Real-time logging of DBSCAN operations
- **Stats Panel**: Dataset overview, density scores, processing mode indicators
- **Inspector Panel**: Detailed view of clustering logic (epsilon, semantic match, verdict)
- **Batch Indicator**: Shows scanned/ignored/focused complaint counts during scenarios

### 6. **Mock Data Generator**
Python script that creates realistic test data:
- **500-600 complaints** per generation
- **10 categories** with Taglish descriptions (Filipino/English)
- **Hotspot distribution**: 30% of complaints placed at same coordinates for stacking
- **26 barangay coverage**: Complaints distributed across all Digos City barangays
- **Realistic timestamps**: Random timestamps within past week
- **Test scenarios**: 5 specific scenarios embedded in dataset

---

## 📁 Project Structure

```
ground_truth_tool/
├── dashboard.html                     # Main dashboard interface
├── dashboard.css                      # Dark theme styling (770+ lines)
├── dashboard.js                       # Dashboard controller
├── simulation-engine.js               # Core DBSCAN visualization engine (1400+ lines)
├── useSimulationEngine.js            # React-style hook (if using React)
├── generate_mock_data.py             # Python script to generate mock data
├── mock_complaints.json              # Generated complaint dataset (500+ records)
├── brgy_boundaries_location.json     # 26 barangay GeoJSON polygons
├── digos-city-boundary.json          # City boundary polygon
├── DOCUMENTATION.md                  # Comprehensive technical documentation (850+ lines)
└── README.md                         # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7+ (for data generation)
- Modern web browser (Chrome, Firefox, Edge)
- HTTP server (for serving files locally)

### Installation & Running

1. **Generate Mock Data**
   ```bash
   cd ground_truth_tool
   python generate_mock_data.py
   ```
   This creates `mock_complaints.json` with 500+ complaints distributed across barangays.

2. **Start Local Server**
   ```bash
   npx http-server -p 8080 -o
   ```
   Or use Python's built-in server:
   ```bash
   python -m http.server 8080
   ```

3. **Open Dashboard**
   Navigate to `http://localhost:8080/dashboard.html`

4. **Test Scenarios**
   - Click scenario buttons (S-01 through S-05) to see DBSCAN in action
   - Watch the console log for detailed clustering steps
   - Observe how background markers dim and spotlight markers appear
   - Click "Reset Scan" to return to full system view

---

## 🎮 How to Use

### Viewing the Map
- **Pan**: Click and drag the map
- **Zoom**: Use mouse wheel or +/- buttons
- **Deep Zoom**: Zoom up to level 22 for precise viewing
- **Hover**: Hover over barangay boundaries to see names
- **Click Markers**: Click complaint markers to see details

### Running Scenarios
1. Click any scenario button (S-01 to S-05)
2. Watch the animation:
   - Background markers dim to 15% opacity
   - Map pans/zooms to scenario cluster
   - Spotlight markers appear with animations
   - Console logs show DBSCAN steps
3. Inspect the results:
   - Check epsilon circles (distance thresholds)
   - See connection lines between related complaints
   - View verdict in inspector panel (MERGED or REJECTED)
4. Click "Reset Scan" to clear and return to full view

### Understanding Visualizations
- **Gray Dots (4px)**: Background complaints (always visible)
- **Red Badge**: Stacked complaints counter (same coordinates)
- **Large Colored Icons**: Spotlight markers (scenario-specific)
- **Dashed Circles**: Epsilon threshold boundaries
- **Cyan Lines**: Connections between merged complaints
- **Colored Polygons**: Barangay boundaries (subtle, dashed)

---

## 📊 Data Structure

### Complaint Record Format
```json
{
  "id": "C-001",
  "user_id": "u_123",
  "timestamp": "2026-01-08T10:30:00",
  "category": "Pipe Leak",
  "description": "May tulo ng tubig dito sa kanto",
  "latitude": 6.749123,
  "longitude": 125.357456,
  "barangay": "Zone I",
  "status": "PENDING",
  "_scenario": "scenario_1_source"
}
```

### Metadata Structure
```json
{
  "generated_at": "2026-01-09T12:00:00",
  "generator": "CitizenLink Synthetic Data Generator v2.0",
  "total_records": 538,
  "base_location": {
    "city": "Digos City",
    "latitude": 6.7523,
    "longitude": 125.3572
  },
  "barangays": ["Kiagot", "Dulangan", ...],
  "barangay_count": 26,
  "category_epsilon": {
    "Pipe Leak": 15.0,
    "Flooding": 25.0,
    ...
  }
}
```

---

## 🔧 Technical Details

### Algorithm Configuration
- **DBSCAN Epsilon**: Adaptive per category (5m - 25m)
- **Temporal Window**: 30 days (ignores older complaints)
- **Semantic Matrix**: Pre-defined category relationships
- **Correlation Threshold**: 0.5 minimum for semantic matching
- **Stacking Threshold**: Exact coordinate matching (6 decimal places)

### Visualization Specs
- **Background Marker**: L.circleMarker, 4px radius, #888888 color
- **Spotlight Marker**: L.divIcon, 40px size, category-specific color
- **Epsilon Circle**: 10-25m radius, dashed cyan border
- **Connection Line**: 2px width, cyan color, animated
- **Stacked Badge**: Red circle, white text, 24px minimum, pulse animation

### Map Configuration
- **Center**: Dynamic (calculated from barangay centroids)
- **Default Zoom**: 13 (city-wide view)
- **Max Zoom**: 22 (street-level precision)
- **Tile Layer**: CartoDB Dark Matter
- **Max Native Zoom**: 19 (tiles), 22 (map zoom capability)

### Performance
- **Marker Count**: 500+ background markers (always rendered)
- **Clustering Algorithm**: O(n²) simplified DBSCAN
- **Point-in-Polygon**: Ray casting algorithm for barangay membership
- **Render Time**: < 1 second for 500+ markers
- **Zoom Response**: Instant (no transition animations)

---

## 📚 Categories & Epsilon Values

| Category | Epsilon | Description |
|----------|---------|-------------|
| No Water | 5m | Highly localized issue |
| Trash | 8m | Small area concern |
| Pothole | 10m | Road-specific issue |
| Noise Complaint | 10m | Localized disturbance |
| Broken Streetlight | 12m | Small neighborhood issue |
| Road Damage | 12m | Street-level problem |
| Pipe Leak | 15m | Can affect nearby areas |
| Illegal Dumping | 15m | Medium area impact |
| Stray Dog | 20m | Mobile, wider area |
| Flooding | 25m | Large area impact |

---

## 🌐 Barangays Covered

Digos City's 26 barangays (all included):
- Kiagot, Dulangan, Tres de Mayo, Soong, Kapatagan
- Binaton, Igpit, Colorado, Lungag, Matti
- Goma, San Roque, San Agustin, San Jose, Tiguman
- San Miguel, Zone I, Zone II, Zone III, Dawis
- Aplaya, Cogon, Ruparan, Sinawilan, Balabag, Mahayahay

---

## 🎨 Color Scheme

### UI Colors
- Background: `#0a0e1a` (Very dark blue)
- Cards: `#151b2b` (Dark blue-gray)
- Text Primary: `#e4e6eb` (Light gray)
- Text Secondary: `#8b92a8` (Medium gray)
- Accent Blue: `#3b82f6`
- Accent Green: `#10b981`
- Accent Red: `#ef4444`

### Category Colors
- Pipe Leak: `#06b6d4` (Cyan)
- Flooding: `#3b82f6` (Blue)
- Pothole: `#f59e0b` (Amber)
- No Water: `#ef4444` (Red)
- Trash: `#84cc16` (Lime)
- Stray Dog: `#a855f7` (Purple)
- Others: Various vibrant colors

---

## 📖 Documentation

For comprehensive technical documentation, see [DOCUMENTATION.md](DOCUMENTATION.md), which includes:
- Complete algorithm specifications
- Step-by-step execution flow
- API reference for all functions
- Visual design specifications
- Implementation guidelines
- Testing scenarios

---

## 🛠️ Development

### Regenerate Mock Data
```bash
python generate_mock_data.py
```
Creates new `mock_complaints.json` with:
- 500-600 random complaints
- 5 embedded test scenarios
- Distribution across all 26 barangays
- ~30% stacked at hotspot locations

### Customize Categories
Edit `CATEGORY_EPSILON` in `generate_mock_data.py`:
```python
CATEGORY_EPSILON = {
    "New Category": 20.0,  # Distance threshold in meters
    ...
}
```

### Modify Semantic Relationships
Edit `RELATIONSHIP_MATRIX` in `simulation-engine.js`:
```javascript
const RELATIONSHIP_MATRIX = {
    "Category A": ["Category B", "Category C"],
    ...
};
```

### Add New Scenarios
1. Add scenario configuration in `simulation-engine.js`:
   ```javascript
   const SCENARIO_CONFIG = {
       6: { name: "New Scenario", ... }
   };
   ```
2. Implement scenario function:
   ```javascript
   async runScenario6(data, config) { ... }
   ```
3. Add button in `dashboard.html`

---

## 🐛 Troubleshooting

### Barangay boundaries not showing
- Check that `brgy_boundaries_location.json` is in the same directory
- Verify file is valid JSON (not corrupted)
- Check browser console for loading errors

### Mock data not loading
- Ensure `mock_complaints.json` exists (run `generate_mock_data.py`)
- Check file permissions
- Verify correct file path in fetch URL

### Markers not appearing
- Hard refresh: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
- Clear browser cache
- Check browser console for JavaScript errors

### Scenarios not working
- Ensure data is fully loaded before clicking scenario buttons
- Check console for error messages
- Verify scenario data exists in mock_complaints.json

---

## 📦 Dependencies

### JavaScript Libraries (CDN)
- **Leaflet.js v1.9.4**: Interactive map library
- **Font Awesome v6.0.0**: Icon library for UI elements

### Python (for data generation)
- **Python 3.7+**: Standard library only (no external dependencies)
- Uses: `json`, `random`, `math`, `datetime`, `typing`

---

## 📄 License

This project is provided as-is for academic and thesis defense purposes.

---

## 👥 Author

CitizenLink Development Team  
Digos City, Philippines  
January 2026

---

## 🎓 Academic Use

This project is designed for thesis defense presentations demonstrating:
- Advanced clustering algorithms (DBSCAN)
- Geographic information systems (GIS)
- Real-time data visualization
- Semantic relationship modeling
- User interface design for complex data

**Citation**: Please cite this work if used in academic research.

---

## 🔗 Quick Links

- [Technical Documentation](DOCUMENTATION.md) - Complete API reference
- [Mock Data Generator](generate_mock_data.py) - Data generation script
- [Dashboard](dashboard.html) - Main application interface
- [Simulation Engine](simulation-engine.js) - Core algorithm implementation

---

**Version**: 2.0  
**Last Updated**: January 9, 2026  
**Status**: Production Ready
