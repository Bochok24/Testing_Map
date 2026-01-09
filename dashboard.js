/**
 * CitizenLink Dashboard Controller v3.0
 * ======================================
 * Full System Scan Dashboard with Big Data Visualization
 * 
 * @requires simulation-engine.js
 * @requires Leaflet.js
 */

// ==================== GLOBAL VARIABLES ====================
let map;
let simulationEngine;

// ==================== INITIALIZE MAP ====================
function initMap() {
    // Initialize Leaflet map centered on Digos City
    map = L.map('map', {
        zoomControl: true,
        attributionControl: false,
        maxZoom: 22  // Allow deeper zoom for precise viewing
    }).setView([6.7490, 125.3572], 14);

    // Dark tile layer (CartoDB Dark Matter) with extended zoom
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 22,
        maxNativeZoom: 19,  // Tiles only available up to 19, but we can zoom further
        subdomains: 'abcd'
    }).addTo(map);

    // Add custom attribution
    L.control.attribution({
        position: 'bottomright',
        prefix: '<a href="https://leafletjs.com">Leaflet</a> | CitizenLink Thesis Demo'
    }).addTo(map);
    
    // Add scale control
    L.control.scale({
        position: 'bottomleft',
        metric: true,
        imperial: false
    }).addTo(map);
}

// ==================== LOGGING SYSTEM ====================
function addLog(message, type = 'info') {
    const logContent = document.getElementById('logContent');
    const logLine = document.createElement('div');
    logLine.className = `log-line ${type}`;
    logLine.textContent = message;
    logContent.appendChild(logLine);
    
    // Auto-scroll to bottom
    logContent.scrollTop = logContent.scrollHeight;
}

function clearLog() {
    const logContent = document.getElementById('logContent');
    logContent.innerHTML = `
        <div class="log-line system">[SYSTEM] CitizenLink Validation Console Ready</div>
        <div class="log-line system">[SYSTEM] Full System Scan Mode Active</div>
        <div class="log-line info">[INFO] All data points rendered. Select a scenario to analyze.</div>
    `;
}

// ==================== STATS UPDATE ====================
function updateStats(stats) {
    if (stats.datasetName) {
        document.getElementById('datasetName').textContent = stats.datasetName;
    }
    if (stats.totalRecords !== undefined) {
        document.getElementById('totalRecords').textContent = stats.totalRecords;
    }
    if (stats.pendingValidation !== undefined) {
        document.getElementById('pendingValidation').textContent = stats.pendingValidation;
    }
    if (stats.densityScore) {
        const densityEl = document.getElementById('densityScore');
        densityEl.textContent = stats.densityScore;
        densityEl.className = 'overview-value';
        if (stats.densityScore === 'High') {
            densityEl.classList.add('density-high');
        } else if (stats.densityScore === 'Medium') {
            densityEl.classList.add('density-medium');
        } else {
            densityEl.classList.add('density-low');
        }
    }
    if (stats.processingMode) {
        const modeEl = document.getElementById('processingMode');
        if (stats.processingMode === 'focused') {
            modeEl.innerHTML = '<i class="fas fa-crosshairs"></i> Focused Analysis';
            modeEl.className = 'mode-value focused';
        } else {
            modeEl.innerHTML = '<i class="fas fa-globe"></i> Global Scan';
            modeEl.className = 'mode-value';
        }
    }
}

// ==================== INSPECTOR PANEL ====================
function updateInspector(data) {
    document.getElementById('currentCategory').textContent = data.category || '-';
    document.getElementById('adaptiveEpsilon').textContent = data.epsilon || '-';
    document.getElementById('timeDiff').textContent = data.timeDiff || '-';
    document.getElementById('semanticMatch').textContent = data.semantic || '-';
    
    const verdictElement = document.getElementById('logicVerdict');
    verdictElement.textContent = data.verdict || '-';
    verdictElement.className = 'value verdict-text';
    
    if (data.verdict === 'MERGED') {
        verdictElement.classList.add('merged');
    } else if (data.verdict === 'REJECTED') {
        verdictElement.classList.add('rejected');
    }
    
    // Show inspector panel with animation
    document.getElementById('inspectorPanel').classList.add('visible');
}

function hideInspector() {
    document.getElementById('inspectorPanel').classList.remove('visible');
}

// ==================== STATUS OVERLAY ====================
function showStatus(message, duration = 3000) {
    const statusMessage = document.getElementById('statusMessage');
    statusMessage.textContent = message;
    statusMessage.style.display = 'block';
    
    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, duration);
}

// ==================== RESET FUNCTION ====================
function resetSimulation() {
    if (simulationEngine) {
        // Full reset: clears everything then re-renders all background points
        simulationEngine.fullReset();
    }
    
    clearLog();
    hideInspector();
    
    // Remove active state from buttons
    document.querySelectorAll('.scenario-btn').forEach(b => b.classList.remove('active'));
    
    // Reset map view - use metadata center if available
    if (simulationEngine && simulationEngine.metadata) {
        const center = simulationEngine.metadata.base_location;
        map.setView([center.latitude, center.longitude], 13);
    } else {
        map.setView([6.7490, 125.3572], 13);
    }
    
    addLog('[SYSTEM] Full System Scan Restored', 'system');
    addLog('[INFO] All data points visible. Select a scenario to analyze.', 'info');
    showStatus('🔄 Full System Scan Active');
}

// ==================== MAIN INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[CitizenLink] Initializing Dashboard...');
    
    // Initialize map
    initMap();
    console.log('[CitizenLink] Map initialized');
    
    // Initialize simulation engine with callbacks (including statsCallback)
    simulationEngine = new SimulationEngine(map, addLog, updateInspector, updateStats);
    console.log('[CitizenLink] Simulation Engine created');
    
    // Load mock data
    const success = await simulationEngine.initialize();
    
    if (success) {
        showStatus('✅ Full System Scan Active', 2500);
        console.log('[CitizenLink] Data loaded and rendered successfully');
    } else {
        showStatus('❌ Failed to Load Data - Check console', 4000);
        console.error('[CitizenLink] Failed to load mock data');
    }
    
    // ==================== SCENARIO BUTTON LISTENERS ====================
    const scenarioButtons = document.querySelectorAll('.scenario-btn');
    
    scenarioButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            // Prevent multiple concurrent runs
            if (simulationEngine.isRunning) {
                showStatus('⏳ Simulation in progress, please wait...', 1500);
                return;
            }
            
            // Update UI state
            scenarioButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Get scenario configuration
            const scenarioNum = parseInt(btn.getAttribute('data-scenario'));
            const config = SCENARIO_CONFIG[scenarioNum];
            
            // DON'T clear the map - just dim background points
            hideInspector();
            
            // Show status
            showStatus(`🔬 Analyzing: ${config.name}`, 2500);
            
            // Run the scenario simulation (this will dim background and spotlight relevant points)
            await simulationEngine.runScenario(scenarioNum);
            
            // Log completion
            console.log(`[CitizenLink] Scenario ${scenarioNum} completed`);
        });
    });
    
    // ==================== RESET BUTTON ====================
    document.querySelector('.reset-btn').addEventListener('click', () => {
        if (simulationEngine.isRunning) {
            showStatus('⏳ Cannot reset while simulation is running', 1500);
            return;
        }
        resetSimulation();
    });
    
    // ==================== INSPECTOR CLOSE BUTTON ====================
    document.getElementById('closeInspector').addEventListener('click', hideInspector);
    
    // ==================== KEYBOARD SHORTCUTS ====================
    document.addEventListener('keydown', (e) => {
        // Ignore if typing in an input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        
        // Number keys 1-5 to trigger scenarios
        if (e.key >= '1' && e.key <= '5' && !simulationEngine.isRunning) {
            const scenarioNum = parseInt(e.key);
            const btn = document.querySelector(`[data-scenario="${scenarioNum}"]`);
            if (btn) {
                btn.click();
                console.log(`[CitizenLink] Triggered scenario ${scenarioNum} via keyboard`);
            }
        }
        
        // R to reset
        if ((e.key === 'r' || e.key === 'R') && !simulationEngine.isRunning) {
            resetSimulation();
        }
        
        // Escape to close inspector
        if (e.key === 'Escape') {
            hideInspector();
        }
    });
    
    // ==================== WELCOME MESSAGE ====================
    setTimeout(() => {
        addLog('[SYSTEM] Full System Scan Dashboard Ready', 'system');
        addLog('[INFO] Displaying ALL data points in workspace', 'info');
        addLog('[INFO] Press keys 1-5 or click to spotlight a scenario', 'info');
        addLog('[INFO] Press R to reset full scan view', 'info');
    }, 1500);
    
    console.log('[CitizenLink] Dashboard initialization complete');
});


// ==================== UTILITY: EXPORT DATA FOR DEBUGGING ====================
window.debugCitizenLink = {
    getEngine: () => simulationEngine,
    getMap: () => map,
    getBackgroundMarkers: () => simulationEngine?.backgroundMarkers,
    getSpotlightMarkers: () => simulationEngine?.spotlightMarkers,
    testHaversine: (lat1, lon1, lat2, lon2) => {
        if (typeof haversineDistance === 'function') {
            const dist = haversineDistance(lat1, lon1, lat2, lon2);
            console.log(`Distance: ${dist.toFixed(2)} meters`);
            return dist;
        }
        console.error('haversineDistance not available');
    },
    testLogic: (pointA, pointB) => {
        if (typeof checkLogic === 'function') {
            const result = checkLogic(pointA, pointB);
            console.log('Logic Check Result:', result);
            return result;
        }
        console.error('checkLogic not available');
    },
    showConfig: () => {
        console.log('Adaptive Epsilon:', ADAPTIVE_EPSILON);
        console.log('Relationship Matrix:', RELATIONSHIP_MATRIX);
        console.log('Scenario Config:', SCENARIO_CONFIG);
    },
    dimTest: () => {
        simulationEngine?.dimBackgroundMarkers([]);
        console.log('All markers dimmed');
    },
    resetTest: () => {
        simulationEngine?.resetBackgroundMarkers();
        console.log('All markers restored');
    }
};
