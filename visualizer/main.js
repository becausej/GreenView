var esri_url ='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
var esri_attribution = '© Esri © OpenStreetMap Contributors';
var lyr_satellite = L.tileLayer(esri_url, {id: 'MapID', maxZoom: 20, tileSize: 512, zoomOffset: -1, attribution: esri_attribution});
var map = L.map('map', {
  layers: [lyr_satellite],
}).setView([0, 0], 2);
var baseMaps = {
    "Satellite": lyr_satellite
};
var overlayMaps = {
};
L.control.layers(baseMaps, overlayMaps).addTo(map);

fetch("/geojson.json")
  .then(response => response.json())
  .then(data => {
    map.fitBounds(L.geoJSON(data).getBounds());
    L.geoJSON(
      data,
      {
        style: function(feature) {
          return {
            fillColor: feature.properties.fill,
            color: feature.properties.stroke,
            weight: feature.properties["stroke-width"],
            opacity: feature.properties["stroke-opacity"],
            fillOpacity: feature.properties["fill-opacity"],
          };
        }
      },
    ).addTo(map);
  });
