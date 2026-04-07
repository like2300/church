// Congo Admin Map - Offline Leaflet Map for Location Admin
// Works completely offline with local GeoJSON data

var map;
var marker;
var departmentsLayer;

function initMap() {
    // Check if map already initialized
    if (map) {
        return;
    }
    
    // Check if element exists
    var mapElement = document.getElementById('map');
    if (!mapElement) {
        console.error('Map element not found');
        return;
    }
    
    // Coordonnées centrales du Congo
    var congoCenter = [-1.5, 15.0];
    
    // Initialisation de la carte
    map = L.map('map').setView(congoCenter, 6);

    // Style pour les départements
    function style(feature) {
        return {
            color: '#2563eb',
            weight: 2,
            fillOpacity: 0.2,
            fillColor: '#3b82f6'
        };
    }

    // Style pour le survol
    function highlightFeature(e) {
        var layer = e.target;
        layer.setStyle({
            weight: 3,
            fillOpacity: 0.4
        });
        layer.bringToFront();
    }

    function resetHighlight(e) {
        if (departmentsLayer) {
            departmentsLayer.resetStyle(e.target);
        }
    }

    function zoomToFeature(e) {
        map.fitBounds(e.target.getBounds());
    }

    function onEachFeature(feature, layer) {
        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
            click: zoomToFeature
        });
        
        // Ajouter un popup avec le nom du département
        if (feature.properties && feature.properties.name) {
            layer.bindPopup('<b>' + feature.properties.name + '</b><br>Chef-lieu: ' + feature.properties.chef_lieu);
        }
    }

    // Chargement du GeoJSON local des départements du Congo
    fetch('/static/data/congo_departments.geojson')
        .then(function(response) {
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .then(function(data) {
            departmentsLayer = L.geoJSON(data, {
                style: style,
                onEachFeature: onEachFeature
            }).addTo(map);
            
            // Ajuster le zoom pour afficher tout le Congo
            map.fitBounds(departmentsLayer.getBounds());
            
            // Invalidate map size after a short delay
            setTimeout(function() {
                map.invalidateSize();
            }, 100);
        })
        .catch(function(error) {
            console.error('Erreur chargement GeoJSON:', error);
            var errorDiv = document.getElementById('map-error');
            if (errorDiv) {
                errorDiv.style.display = 'block';
                errorDiv.innerHTML = '⚠️ Erreur: ' + error.message;
            }
        });

    // Gestion du clic pour récupérer Lat/Long
    map.on('click', function(e) {
        if (marker) {
            map.removeLayer(marker);
        }
        marker = L.marker(e.latlng).addTo(map);
        
        // Remplit automatiquement les champs Django
        var latField = document.getElementById('id_latitude');
        var lngField = document.getElementById('id_longitude');
        
        if (latField && lngField) {
            latField.value = e.latlng.lat.toFixed(4);
            lngField.value = e.latlng.lng.toFixed(4);
            
            // Animation visuelle pour confirmer
            latField.parentElement.classList.add('ring-2', 'ring-blue-500');
            setTimeout(function() {
                latField.parentElement.classList.remove('ring-2', 'ring-blue-500');
            }, 1000);
        }
    });
    
    // Fix map display issues
    setTimeout(function() {
        map.invalidateSize();
    }, 200);
}

// Export initMap to global scope
window.initMap = initMap;
