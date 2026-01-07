// ==================== Global Variables ====================
let map;
let drawnItems;
let complaintMarkers = [];
let clusterCount = 0;
let outlierCount = 0;

// ==================== Map Initialization ====================
function initializeMap() {
    // Initialize map
    map = L.map('map', {
        zoomControl: true,
        attributionControl: true
    });

    // Add CartoDB Positron base layer (clean, light gray)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    // Try to load boundary data
    loadBoundaryData();

    // Initialize drawn items layer
    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);
}

// ==================== Load Boundary Data ====================
function loadBoundaryData() {
    // Load barangay boundaries from local directory
    fetch('./brgy_boundaries_location.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Barangay boundaries file not found');
            }
            return response.json();
        })
        .then(barangays => {
            // Create feature group to hold all barangay polygons
            const boundaryGroup = L.featureGroup();

            // Add each barangay as a separate polygon
            barangays.forEach((barangay, index) => {
                if (!barangay.geojson) return;

                // Generate distinct colors for each barangay
                const hue = (index * 47) % 360;
                const style = {
                    color: `hsl(${hue}, 70%, 40%)`,
                    weight: 2,
                    opacity: 0.8,
                    fillColor: `hsl(${hue}, 70%, 60%)`,
                    fillOpacity: 0.25
                };

                try {
                    // Add barangay polygon to map
                    const layer = L.geoJSON(barangay.geojson, {
                        style: style,
                        coordsToLatLng: function(coords) {
                            // GeoJSON uses [lng, lat], Leaflet uses [lat, lng]
                            return L.latLng(coords[1], coords[0]);
                        }
                    });

                    // Add popup with barangay name
                    layer.bindPopup(`<strong>${barangay.name}</strong>`, {
                        className: 'barangay-popup'
                    });

                    boundaryGroup.addLayer(layer);
                } catch (error) {
                    console.warn(`Failed to render barangay: ${barangay.name}`, error);
                }
            });

            // Add all boundaries to map
            boundaryGroup.addTo(map);

            // Fit map to show all barangays
            if (boundaryGroup.getBounds().isValid()) {
                map.fitBounds(boundaryGroup.getBounds(), { 
                    padding: [50, 50],
                    maxZoom: 14
                });
            }

            // Add city label at center
            const center = boundaryGroup.getBounds().getCenter();
            L.marker(center, {
                icon: L.divIcon({
                    className: 'boundary-label',
                    html: '<div style="background: rgba(0,123,255,0.95); color: white; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 700; white-space: nowrap; box-shadow: 0 3px 10px rgba(0,0,0,0.3); font-family: Inter, sans-serif; letter-spacing: 0.5px;">DIGOS CITY</div>',
                    iconSize: [120, 35],
                    iconAnchor: [60, 17]
                }),
                zIndexOffset: 1000
            }).addTo(map);

            console.log(`✅ Loaded ${barangays.length} barangay boundaries successfully`);
        })
        .catch(error => {
            console.warn('⚠️ Failed to load barangay boundaries, using default view:', error);
            // Fallback: Default to Digos City coordinates
            map.setView([6.75, 125.36], 13);
        });
}

// ==================== Plot Complaint Data ====================
function plotComplaintData() {
    // Check if mock data is available
    if (typeof mockComplaintData === 'undefined') {
        console.error('Mock data not loaded');
        return;
    }

    // Loop through complaint data
    mockComplaintData.forEach(complaint => {
        // Determine color and styling based on category
        let color, fillColor, radius;
        
        switch(complaint.category.toLowerCase()) {
            case 'infrastructure':
                color = '#343a40';
                fillColor = '#343a40';
                radius = 6;
                break;
            case 'environment':
                color = '#28a745';
                fillColor = '#28a745';
                radius = 6;
                break;
            case 'public safety':
                color = '#dc3545';
                fillColor = '#dc3545';
                radius = 6;
                break;
            default:
                color = '#6c757d';
                fillColor = '#6c757d';
                radius = 6;
        }

        // Create circle marker
        const marker = L.circleMarker([complaint.lat, complaint.lng], {
            radius: radius,
            fillColor: fillColor,
            color: color,
            weight: 2,
            opacity: 0.8,
            fillOpacity: 0.6,
            draggable: false
        });

        // Bind popup with complaint information
        marker.bindPopup(`
            <div style="font-family: 'Inter', sans-serif;">
                <strong style="color: ${color}; font-size: 14px;">${complaint.type}</strong><br>
                <span style="font-size: 12px; color: #6c757d;">Category: ${complaint.category}</span><br>
                <span style="font-size: 11px; color: #adb5bd;">ID: ${complaint.id}</span>
            </div>
        `);

        // Add to map
        marker.addTo(map);
        complaintMarkers.push(marker);
    });
}

// ==================== Setup Drawing Controls ====================
function setupDrawingControls() {
    // Create custom icon for outlier markers
    const outlierIcon = L.icon({
        iconUrl: 'data:image/svg+xml;base64,' + btoa(`
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
                <circle cx="16" cy="16" r="14" fill="#ff6b6b" stroke="white" stroke-width="3"/>
                <path d="M16 8 L18 14 L24 14 L19 18 L21 24 L16 20 L11 24 L13 18 L8 14 L14 14 Z" fill="white"/>
            </svg>
        `),
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
    });

    // Configure draw control with freehand drawing
    const drawControl = new L.Control.Draw({
        position: 'topleft',
        draw: {
            polygon: {
                allowIntersection: false,
                showArea: true,
                shapeOptions: {
                    color: '#007bff',
                    fillColor: '#007bff',
                    fillOpacity: 0.2,
                    weight: 3
                },
                drawError: {
                    color: '#dc3545',
                    message: '<strong>Error:</strong> Shape edges cannot cross!'
                }
            },
            marker: {
                icon: outlierIcon
            },
            polyline: false,
            rectangle: false,
            circle: false,
            circlemarker: false
        },
        edit: {
            featureGroup: drawnItems,
            remove: true
        }
    });

    map.addControl(drawControl);

    // Add freehand drawing functionality
    let isFreehandMode = false;
    let freehandPath = null;
    let freehandPoints = [];

    // Create custom freehand button
    const FreehandControl = L.Control.extend({
        options: {
            position: 'topleft'
        },
        onAdd: function(map) {
            const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            container.style.cursor = 'pointer';
            container.innerHTML = `
                <a id="freehand-btn" title="Freehand drawing (click and drag)" style="width: 32px; height: 32px; line-height: 30px; text-align: center; display: block; background: white; color: #333;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 19l7-7 3 3-7 7-3-3z"></path>
                        <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"></path>
                        <path d="M2 2l7.586 7.586"></path>
                        <circle cx="11" cy="11" r="2"></circle>
                    </svg>
                </a>
            `;
            
            L.DomEvent.on(container, 'click', function(e) {
                L.DomEvent.stopPropagation(e);
                L.DomEvent.preventDefault(e);
                toggleFreehandMode();
            });
            
            return container;
        }
    });
    
    map.addControl(new FreehandControl());

    function toggleFreehandMode() {
        isFreehandMode = !isFreehandMode;
        const btn = document.getElementById('freehand-btn');
        
        if (isFreehandMode) {
            btn.style.background = '#007bff';
            btn.style.color = 'white';
            btn.title = 'Freehand drawing active (click and drag)';
            map.getContainer().style.cursor = 'crosshair';
            
            // Disable map dragging and other interactions
            map.dragging.disable();
            map.touchZoom.disable();
            map.doubleClickZoom.disable();
            map.scrollWheelZoom.disable();
            map.boxZoom.disable();
            map.keyboard.disable();
            
            // Disable other drawing tools
            if (map.pm) map.pm.disableDraw();
        } else {
            btn.style.background = 'white';
            btn.style.color = '#333';
            btn.title = 'Freehand drawing (click and drag)';
            map.getContainer().style.cursor = '';
            
            // Re-enable map interactions
            map.dragging.enable();
            map.touchZoom.enable();
            map.doubleClickZoom.enable();
            map.scrollWheelZoom.enable();
            map.boxZoom.enable();
            map.keyboard.enable();
        }
    }

    // Freehand drawing event handlers
    let isDrawing = false;

    map.on('mousedown', function(e) {
        if (!isFreehandMode) return;
        
        L.DomEvent.preventDefault(e.originalEvent);
        L.DomEvent.stopPropagation(e.originalEvent);
        
        isDrawing = true;
        freehandPoints = [];
        freehandPoints.push([e.latlng.lat, e.latlng.lng]);
        
        if (freehandPath) {
            map.removeLayer(freehandPath);
        }
        
        freehandPath = L.polyline(freehandPoints, {
            color: '#007bff',
            weight: 3,
            opacity: 0.8
        }).addTo(map);
    });

    map.on('mousemove', function(e) {
        if (!isFreehandMode || !isDrawing) return;
        
        L.DomEvent.preventDefault(e.originalEvent);
        
        freehandPoints.push([e.latlng.lat, e.latlng.lng]);
        freehandPath.setLatLngs(freehandPoints);
    });

    map.on('mouseup', function(e) {
        if (!isFreehandMode || !isDrawing) return;
        
        L.DomEvent.preventDefault(e.originalEvent);
        L.DomEvent.stopPropagation(e.originalEvent);
        
        isDrawing = false;
        
        // Only create polygon if there are enough points
        if (freehandPoints.length > 3) {
            // Simplify the path to reduce point count (Douglas-Peucker algorithm simulation)
            const simplifiedPoints = simplifyPath(freehandPoints, 0.0001);
            
            // Close the polygon by adding the first point at the end
            simplifiedPoints.push(simplifiedPoints[0]);
            
            // Remove temporary path
            if (freehandPath) {
                map.removeLayer(freehandPath);
                freehandPath = null;
            }
            
            // Create permanent polygon
            const polygon = L.polygon(simplifiedPoints, {
                color: '#007bff',
                fillColor: '#007bff',
                fillOpacity: 0.2,
                weight: 3
            });
            
            polygon.feature = {
                type: 'Feature',
                properties: {
                    type: 'cluster',
                    createdAt: new Date().toISOString(),
                    drawingMethod: 'freehand'
                },
                geometry: polygon.toGeoJSON().geometry
            };
            
            drawnItems.addLayer(polygon);
            clusterCount++;
            updateStats();
        } else {
            // Remove path if not enough points
            if (freehandPath) {
                map.removeLayer(freehandPath);
                freehandPath = null;
            }
        }
        
        freehandPoints = [];
    });
    
    // Handle case where mouse leaves map while drawing
    map.getContainer().addEventListener('mouseleave', function() {
        if (isDrawing && isFreehandMode) {
            // Finish the drawing
            isDrawing = false;
            
            if (freehandPoints.length > 3) {
                const simplifiedPoints = simplifyPath(freehandPoints, 0.0001);
                simplifiedPoints.push(simplifiedPoints[0]);
                
                if (freehandPath) {
                    map.removeLayer(freehandPath);
                    freehandPath = null;
                }
                
                const polygon = L.polygon(simplifiedPoints, {
                    color: '#007bff',
                    fillColor: '#007bff',
                    fillOpacity: 0.2,
                    weight: 3
                });
                
                polygon.feature = {
                    type: 'Feature',
                    properties: {
                        type: 'cluster',
                        createdAt: new Date().toISOString(),
                        drawingMethod: 'freehand'
                    },
                    geometry: polygon.toGeoJSON().geometry
                };
                
                drawnItems.addLayer(polygon);
                clusterCount++;
                updateStats();
            } else {
                if (freehandPath) {
                    map.removeLayer(freehandPath);
                    freehandPath = null;
                }
            }
            
            freehandPoints = [];
        }
    });

    // Simple path simplification (Douglas-Peucker-like)
    function simplifyPath(points, tolerance) {
        if (points.length <= 2) return points;
        
        const simplified = [points[0]];
        let lastPoint = points[0];
        
        for (let i = 1; i < points.length; i++) {
            const point = points[i];
            const distance = Math.sqrt(
                Math.pow(point[0] - lastPoint[0], 2) + 
                Math.pow(point[1] - lastPoint[1], 2)
            );
            
            if (distance > tolerance) {
                simplified.push(point);
                lastPoint = point;
            }
        }
        
        return simplified;
    }

    // Event listener for created shapes
    map.on(L.Draw.Event.CREATED, function(event) {
        const layer = event.layer;
        const type = event.layerType;

        // Add properties to identify the feature type
        if (type === 'polygon') {
            layer.feature = {
                type: 'Feature',
                properties: {
                    type: 'cluster',
                    createdAt: new Date().toISOString()
                },
                geometry: layer.toGeoJSON().geometry
            };
            clusterCount++;
            updateStats();
        } else if (type === 'marker') {
            layer.feature = {
                type: 'Feature',
                properties: {
                    type: 'critical_outlier',
                    createdAt: new Date().toISOString()
                },
                geometry: layer.toGeoJSON().geometry
            };
            outlierCount++;
            updateStats();
        }

        drawnItems.addLayer(layer);
    });

    // Event listener for deleted shapes
    map.on(L.Draw.Event.DELETED, function(event) {
        const layers = event.layers;
        layers.eachLayer(function(layer) {
            if (layer.feature && layer.feature.properties) {
                if (layer.feature.properties.type === 'cluster') {
                    clusterCount--;
                } else if (layer.feature.properties.type === 'critical_outlier') {
                    outlierCount--;
                }
            }
        });
        updateStats();
    });

    // Event listener for edited shapes
    map.on(L.Draw.Event.EDITED, function(event) {
        const layers = event.layers;
        layers.eachLayer(function(layer) {
            if (layer.feature && layer.feature.properties) {
                layer.feature.properties.editedAt = new Date().toISOString();
            }
        });
    });
}

// ==================== Update Statistics ====================
function updateStats() {
    document.getElementById('cluster-count').textContent = clusterCount;
    document.getElementById('outlier-count').textContent = outlierCount;
}

// ==================== Export Ground Truth Data ====================
function exportGroundTruth() {
    // Check if there are any drawn items
    if (drawnItems.getLayers().length === 0) {
        alert('⚠️ No data to export! Please draw some clusters or mark outliers first.');
        return;
    }

    // Extract GeoJSON from drawn items
    const geoJSON = drawnItems.toGeoJSON();

    // Add metadata
    const groundTruthData = {
        type: 'FeatureCollection',
        metadata: {
            tool: 'CitizenLink Ground Truth Validation Tool',
            version: '1.0.0',
            exportDate: new Date().toISOString(),
            totalClusters: clusterCount,
            totalOutliers: outlierCount,
            totalFeatures: geoJSON.features.length
        },
        features: geoJSON.features
    };

    // Create blob from JSON
    const jsonString = JSON.stringify(groundTruthData, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });

    // Generate filename with timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const filename = `ground_truth_session_${timestamp}.json`;

    // Create download link
    const downloadLink = document.createElement('a');
    downloadLink.href = URL.createObjectURL(blob);
    downloadLink.download = filename;

    // Trigger download
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    // Clean up blob URL
    URL.revokeObjectURL(downloadLink.href);

    // Show success message
    showSuccessMessage(filename);
}

// ==================== Show Success Message ====================
function showSuccessMessage(filename) {
    // Create temporary notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #28a745;
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
        z-index: 10000;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 600;
        animation: slideDown 0.3s ease-out;
    `;
    notification.innerHTML = `✅ Successfully exported: ${filename}`;

    // Add animation keyframes
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateX(-50%) translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(-50%) translateY(0);
            }
        }
    `;
    document.head.appendChild(style);

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideDown 0.3s ease-out reverse';
        setTimeout(() => {
            document.body.removeChild(notification);
            document.head.removeChild(style);
        }, 300);
    }, 3000);
}

// ==================== Initialize Application ====================
function initializeApp() {
    // Initialize map
    initializeMap();

    // Plot complaint data
    plotComplaintData();

    // Setup drawing controls
    setupDrawingControls();

    // Setup export button
    document.getElementById('export-btn').addEventListener('click', exportGroundTruth);

    // Initialize stats
    updateStats();
}

// ==================== Run on DOM Content Loaded ====================
document.addEventListener('DOMContentLoaded', initializeApp);
