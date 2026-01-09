/**
 * useSimulationEngine - React Hook for CitizenLink Clustering Simulation
 * =======================================================================
 * 
 * A custom React hook that provides the complete simulation engine logic
 * for demonstrating Generalized DBSCAN clustering in a thesis defense.
 * 
 * @example
 * ```jsx
 * import useSimulationEngine from './useSimulationEngine';
 * 
 * function Dashboard() {
 *   const { 
 *     runScenario, 
 *     resetSimulation, 
 *     logs, 
 *     inspectorData,
 *     isRunning 
 *   } = useSimulationEngine(mapRef);
 * 
 *   return (
 *     <button onClick={() => runScenario(1)}>Run Scenario 1</button>
 *   );
 * }
 * ```
 */

import { useState, useCallback, useRef, useEffect } from 'react';

// ==================== CONFIGURATION CONSTANTS ====================

/**
 * Adaptive Epsilon values per category (in meters)
 */
export const ADAPTIVE_EPSILON = {
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

/**
 * Semantic Relationship Matrix
 */
export const RELATIONSHIP_MATRIX = {
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

/**
 * Correlation Scores between category pairs
 */
export const CORRELATION_SCORES = {
    "Pipe Leak->Flooding": 0.92,
    "Pipe Leak->No Water": 0.85,
    "Pipe Leak->Road Damage": 0.45,
    "Flooding->Pipe Leak": 0.88,
    "Flooding->Road Damage": 0.60,
    "Pothole->Road Damage": 0.75,
    "Road Damage->Pothole": 0.75,
    "No Water->Pipe Leak": 0.80,
    "Trash->Illegal Dumping": 0.70,
    "Illegal Dumping->Trash": 0.70
};

export const CORRELATION_THRESHOLD = 0.50;
export const MAX_TIME_DIFF_HOURS = 48;

/**
 * Scenario configurations
 */
export const SCENARIO_CONFIG = {
    1: {
        name: "Main Event (Flooding + Leak)",
        prefix: "scenario_1",
        description: "Tests semantic correlation: Pipe Leak → Flooding causal chain",
        expectedResult: "MERGE"
    },
    2: {
        name: "Duplicate Spammer",
        prefix: "scenario_2",
        description: "Tests redundancy detection: Same location, same user",
        expectedResult: "MERGE"
    },
    3: {
        name: "Discrete Neighbors",
        prefix: "scenario_3",
        description: "Tests epsilon threshold: Distance > category epsilon",
        expectedResult: "SEPARATE"
    },
    4: {
        name: "Old News (Time Decay)",
        prefix: "scenario_4",
        description: "Tests temporal window: Report too old",
        expectedResult: "SEPARATE"
    },
    5: {
        name: "False Positive",
        prefix: "scenario_5",
        description: "Tests semantic rejection: Unrelated categories",
        expectedResult: "SEPARATE"
    }
};


// ==================== CORE ALGORITHM FUNCTIONS ====================

/**
 * Calculate Haversine distance between two points
 * @param {number} lat1 - Latitude of point 1
 * @param {number} lon1 - Longitude of point 1
 * @param {number} lat2 - Latitude of point 2
 * @param {number} lon2 - Longitude of point 2
 * @returns {number} Distance in meters
 */
export function haversineDistance(lat1, lon1, lat2, lon2) {
    const R = 6371000; // Earth's radius in meters
    
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
}

/**
 * Get time difference between two timestamps in hours
 */
export function getTimeDifferenceHours(timestamp1, timestamp2) {
    const t1 = new Date(timestamp1);
    const t2 = new Date(timestamp2);
    return Math.abs(t2 - t1) / (1000 * 60 * 60);
}

/**
 * Get adaptive epsilon for a category
 */
export function getAdaptiveEpsilon(category) {
    return ADAPTIVE_EPSILON[category] || 10.0;
}

/**
 * Check semantic relationship between categories
 */
export function checkSemanticRelation(categoryA, categoryB) {
    if (categoryA === categoryB) {
        return { isRelated: true, score: 1.0, relationship: "IDENTICAL" };
    }
    
    const relatedCategories = RELATIONSHIP_MATRIX[categoryA] || [];
    const isRelated = relatedCategories.includes(categoryB);
    const key = `${categoryA}->${categoryB}`;
    const score = CORRELATION_SCORES[key] || 0.0;
    
    return {
        isRelated: isRelated && score >= CORRELATION_THRESHOLD,
        score,
        relationship: isRelated && score >= CORRELATION_THRESHOLD ? "CAUSAL" : "NONE"
    };
}

/**
 * Main logic check function
 * @param {Object} pointA - First complaint
 * @param {Object} pointB - Second complaint
 * @returns {Object} Decision result with all metrics
 */
export function checkLogic(pointA, pointB) {
    const result = {
        shouldMerge: false,
        distance: haversineDistance(
            pointA.latitude, pointA.longitude,
            pointB.latitude, pointB.longitude
        ),
        epsilon: Math.max(
            getAdaptiveEpsilon(pointA.category),
            getAdaptiveEpsilon(pointB.category)
        ),
        timeDiff: getTimeDifferenceHours(pointA.timestamp, pointB.timestamp),
        semantic: checkSemanticRelation(pointA.category, pointB.category),
        reasons: [],
        verdict: "REJECTED"
    };
    
    const distanceOk = result.distance <= result.epsilon;
    const semanticOk = result.semantic.isRelated;
    const temporalOk = result.timeDiff <= MAX_TIME_DIFF_HOURS;
    
    if (!distanceOk) result.reasons.push(`Distance ${result.distance.toFixed(1)}m > ε ${result.epsilon}m`);
    if (!semanticOk) result.reasons.push(`No semantic correlation (${result.semantic.score.toFixed(2)})`);
    if (!temporalOk) result.reasons.push(`Time diff ${result.timeDiff.toFixed(1)}h > ${MAX_TIME_DIFF_HOURS}h`);
    
    result.shouldMerge = distanceOk && semanticOk && temporalOk;
    result.verdict = result.shouldMerge ? "MERGED" : "REJECTED";
    
    return result;
}


// ==================== REACT HOOK ====================

/**
 * Custom React Hook for the Simulation Engine
 * 
 * @param {React.RefObject} mapRef - Reference to the Leaflet map instance
 * @returns {Object} Hook return values and methods
 */
export function useSimulationEngine(mapRef) {
    // State
    const [complaints, setComplaints] = useState([]);
    const [logs, setLogs] = useState([
        { message: '[SYSTEM] CitizenLink Validation Console Ready', type: 'system' },
        { message: '[SYSTEM] Generalized DBSCAN Engine v2.0 Loaded', type: 'system' }
    ]);
    const [inspectorData, setInspectorData] = useState({
        category: '-',
        epsilon: '-',
        timeDiff: '-',
        semantic: '-',
        verdict: '-'
    });
    const [isRunning, setIsRunning] = useState(false);
    const [currentScenario, setCurrentScenario] = useState(null);
    
    // Refs for map layers
    const markersRef = useRef([]);
    const circlesRef = useRef([]);
    const linesRef = useRef([]);
    
    /**
     * Add a log entry
     */
    const addLog = useCallback((message, type = 'info') => {
        const timestamp = new Date().toTimeString().split(' ')[0];
        setLogs(prev => [...prev, { 
            message: `[${timestamp}] ${message}`, 
            type,
            id: Date.now()
        }]);
    }, []);
    
    /**
     * Clear all logs
     */
    const clearLogs = useCallback(() => {
        setLogs([
            { message: '[SYSTEM] CitizenLink Validation Console Ready', type: 'system' },
            { message: '[INFO] Awaiting Scenario Selection...', type: 'info' }
        ]);
    }, []);
    
    /**
     * Load mock data from JSON
     */
    const loadData = useCallback(async () => {
        try {
            const response = await fetch('/mock_complaints.json');
            const data = await response.json();
            setComplaints(data.complaints);
            addLog(`Loaded ${data.complaints.length} complaint records`, 'success');
            return true;
        } catch (error) {
            addLog(`Failed to load data: ${error.message}`, 'error');
            return false;
        }
    }, [addLog]);
    
    /**
     * Clear all map layers
     */
    const clearMap = useCallback(() => {
        const map = mapRef?.current;
        if (!map) return;
        
        markersRef.current.forEach(m => map.removeLayer(m));
        circlesRef.current.forEach(c => map.removeLayer(c));
        linesRef.current.forEach(l => map.removeLayer(l));
        
        markersRef.current = [];
        circlesRef.current = [];
        linesRef.current = [];
    }, [mapRef]);
    
    /**
     * Delay helper
     */
    const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    
    /**
     * Filter complaints by scenario
     */
    const filterByScenario = useCallback((scenarioPrefix) => {
        return complaints.filter(c => 
            c._scenario && c._scenario.startsWith(scenarioPrefix)
        );
    }, [complaints]);
    
    /**
     * Run a specific scenario
     */
    const runScenario = useCallback(async (scenarioNumber) => {
        if (isRunning || !complaints.length) {
            if (!complaints.length) await loadData();
            return;
        }
        
        setIsRunning(true);
        setCurrentScenario(scenarioNumber);
        clearMap();
        
        const config = SCENARIO_CONFIG[scenarioNumber];
        const scenarioData = filterByScenario(config.prefix);
        
        addLog(`═══ SCENARIO ${scenarioNumber}: ${config.name} ═══`, 'system');
        addLog(config.description, 'info');
        addLog(`Processing ${scenarioData.length} points...`, 'info');
        
        // Sort by timestamp
        scenarioData.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        
        // Process scenario based on type
        // (Implement specific scenario logic here similar to the vanilla JS version)
        
        await delay(2000); // Placeholder for animation
        
        setIsRunning(false);
    }, [isRunning, complaints, loadData, clearMap, filterByScenario, addLog]);
    
    /**
     * Reset the simulation
     */
    const resetSimulation = useCallback(() => {
        if (isRunning) return;
        
        clearMap();
        clearLogs();
        setCurrentScenario(null);
        setInspectorData({
            category: '-',
            epsilon: '-',
            timeDiff: '-',
            semantic: '-',
            verdict: '-'
        });
        
        addLog('Simulation Reset Complete', 'system');
    }, [isRunning, clearMap, clearLogs, addLog]);
    
    /**
     * Initialize on mount
     */
    useEffect(() => {
        loadData();
    }, [loadData]);
    
    // Return hook interface
    return {
        // State
        complaints,
        logs,
        inspectorData,
        isRunning,
        currentScenario,
        
        // Actions
        runScenario,
        resetSimulation,
        clearLogs,
        addLog,
        
        // Utilities
        checkLogic,
        haversineDistance,
        getAdaptiveEpsilon,
        
        // Config
        SCENARIO_CONFIG,
        ADAPTIVE_EPSILON,
        RELATIONSHIP_MATRIX
    };
}

export default useSimulationEngine;
