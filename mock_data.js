// ==================== Real-World Mock Complaint Data (Digos City) ====================
// Context: Validating Hybrid DBSCAN for CitizenLink
// Simulation Logic:
// 1. Infrastructure -> Linear Clusters (Following road networks)
// 2. Environment -> Dense Clusters (Markets/Creeks)
// 3. Public Safety -> Intersection Clusters (Corner logic)

const mockComplaintData = [
    // =================================================================
    // CLUSTER A: INFRASTRUCTURE (The "Linear" Road Damage)
    // Location: Along Rizal Avenue (Main Thoroughfare)
    // Logic: Points vary slightly in Latitude but are consistent in Longitude (North-South Road)
    // =================================================================
    { id: 1, lat: 6.7552, lng: 125.3571, category: 'Infrastructure', type: 'Deep Pothole' },
    { id: 2, lat: 6.7555, lng: 125.3572, category: 'Infrastructure', type: 'Cracked Pavement' },
    { id: 3, lat: 6.7558, lng: 125.3570, category: 'Infrastructure', type: 'Exposed Rebar' },
    { id: 4, lat: 6.7562, lng: 125.3571, category: 'Infrastructure', type: 'Road Subsidence' },
    { id: 5, lat: 6.7565, lng: 125.3573, category: 'Infrastructure', type: 'Missing Manhole' },
    { id: 6, lat: 6.7569, lng: 125.3571, category: 'Infrastructure', type: 'Uneven Surface' },
    { id: 7, lat: 6.7548, lng: 125.3572, category: 'Infrastructure', type: 'Pothole' }, // Start of line
    { id: 8, lat: 6.7572, lng: 125.3570, category: 'Infrastructure', type: 'Damaged Gutter' }, // End of line

    // =================================================================
    // CLUSTER B: ENVIRONMENT (The "Dense" Market Hotspot)
    // Location: Digos Public Market Area
    // Logic: High density, random distribution within a small radius (0.0005)
    // =================================================================
    { id: 16, lat: 6.7532, lng: 125.3555, category: 'Environment', type: 'Overflowing Garbage' },
    { id: 17, lat: 6.7534, lng: 125.3557, category: 'Environment', type: 'Rotting Waste' },
    { id: 18, lat: 6.7531, lng: 125.3553, category: 'Environment', type: 'Clogged Drainage' },
    { id: 19, lat: 6.7533, lng: 125.3558, category: 'Environment', type: 'Illegal Dumping' },
    { id: 20, lat: 6.7535, lng: 125.3554, category: 'Environment', type: 'Market Waste' },
    { id: 21, lat: 6.7530, lng: 125.3556, category: 'Environment', type: 'Stagnant Water' },
    { id: 22, lat: 6.7536, lng: 125.3555, category: 'Environment', type: 'Blocked Canal' },

    // =================================================================
    // CLUSTER C: PUBLIC SAFETY (The "Intersection" Hazard)
    // Location: Quezon Avenue / Estrada Intersection
    // Logic: Points clustered around a specific 4-way corner
    // =================================================================
    { id: 31, lat: 6.7495, lng: 125.3620, category: 'Public Safety', type: 'Broken Traffic Light' },
    { id: 32, lat: 6.7496, lng: 125.3621, category: 'Public Safety', type: 'No Streetlight' },
    { id: 33, lat: 6.7494, lng: 125.3619, category: 'Public Safety', type: 'Confusing Signage' },
    { id: 34, lat: 6.7495, lng: 125.3622, category: 'Public Safety', type: 'Accident Prone Area' },
    { id: 35, lat: 6.7497, lng: 125.3618, category: 'Public Safety', type: 'Faded Crossing' },

    // =================================================================
    // SECONDARY CLUSTER: INFRASTRUCTURE (Bridge Damage)
    // Location: Bridge crossing near the river (Northern Sector)
    // =================================================================
    { id: 9, lat: 6.7610, lng: 125.3490, category: 'Infrastructure', type: 'Rusted Railing' },
    { id: 10, lat: 6.7611, lng: 125.3491, category: 'Infrastructure', type: 'Bridge Crack' },
    { id: 11, lat: 6.7609, lng: 125.3489, category: 'Infrastructure', type: 'Eroded Support' },
    { id: 12, lat: 6.7612, lng: 125.3492, category: 'Infrastructure', type: 'Loose Expansion Joint' },

    // =================================================================
    // CRITICAL OUTLIERS (The "Needles in the Haystack")
    // These are isolated but strictly URGENT. Ground Truth must mark these.
    // =================================================================
    { id: 40, lat: 6.7800, lng: 125.3500, category: 'Public Safety', type: 'Downed Power Line' }, // Far North
    { id: 41, lat: 6.7350, lng: 125.3450, category: 'Infrastructure', type: 'Collapsed Bridge Section' }, // Far South
    { id: 42, lat: 6.7450, lng: 125.3700, category: 'Environment', type: 'Chemical Spill' }, // Far East

    // =================================================================
    // NOISE DATA (Scattered / Low Priority)
    // Randomly distributed points to test if the user/system correctly ignores them.
    // =================================================================
    { id: 51, lat: 6.7500, lng: 125.3500, category: 'Environment', type: 'Littering' },
    { id: 52, lat: 6.7600, lng: 125.3600, category: 'Infrastructure', type: 'Faded Paint' },
    { id: 53, lat: 6.7400, lng: 125.3550, category: 'Public Safety', type: 'Dog Barking' },
    { id: 54, lat: 6.7700, lng: 125.3450, category: 'Environment', type: 'Minor Trash' },
    { id: 55, lat: 6.7550, lng: 125.3650, category: 'Infrastructure', type: 'Cracked Curb' },
    { id: 56, lat: 6.7480, lng: 125.3520, category: 'Public Safety', type: 'Dim Light' },
    { id: 57, lat: 6.7620, lng: 125.3580, category: 'Environment', type: 'Leaves on Road' },
    { id: 58, lat: 6.7580, lng: 125.3480, category: 'Infrastructure', type: 'Uneven Sidewalk' },
    { id: 59, lat: 6.7420, lng: 125.3580, category: 'Public Safety', type: 'Missing Reflector' },
    { id: 60, lat: 6.7650, lng: 125.3520, category: 'Environment', type: 'Plastic Bottle' },
    { id: 61, lat: 6.7390, lng: 125.3460, category: 'Infrastructure', type: 'Small Pothole' },
    { id: 62, lat: 6.7750, lng: 125.3550, category: 'Public Safety', type: 'Slippery Road' },
    { id: 63, lat: 6.7460, lng: 125.3640, category: 'Environment', type: 'Full Trash Bin' },
    { id: 64, lat: 6.7590, lng: 125.3620, category: 'Infrastructure', type: 'Chipped Paint' },
    { id: 65, lat: 6.7510, lng: 125.3530, category: 'Public Safety', type: 'Leaning Sign' }
];

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = mockComplaintData;
}