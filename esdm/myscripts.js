
// Global Variables

var DEFAULT_DATA = [
{"location": "Kenthurst, New South Wales, Australia", "lat": -33.662742, "lon": 151.002904, "html": "<h3><b>Kenthurst, New South Wales, Australia</b><h3>\n  <table>\n  <tr>\n      <th>Name</th>\n      <th>Degree</th>\n      <th>Email</th>\n    </tr>\n\n    <tr>\n      <th>Anne Chalfant</th>\n      <th>PsyD</th>\n      <th>info@anniescentre.com</th>\n      </tr>\n    "},
{"location": "Wollongong, NSW, Australia", "lat": -34.428377, "lon": 150.893892, "html": "<h3><b>Wollongong, NSW, Australia</b><h3>\n  <table>\n  <tr>\n      <th>Name</th>\n      <th>Degree</th>\n      <th>Email</th>\n    </tr>\n\n    <tr>\n      <th>Arina Atkova</th>\n      <th>BA, Reg. Teacher</th>\n      <th>Arina.aktova@hotmail.com</th>\n      </tr>\n    "},
{"location": "Cobbitty, New South Wales, Australia", "lat": -34.011739, "lon": 150.67192, "html": "<h3><b>Cobbitty, New South Wales, Australia</b><h3>\n  <table>\n  <tr>\n      <th>Name</th>\n      <th>Degree</th>\n      <th>Email</th>\n    </tr>\n\n    <tr>\n      <th>Belinda Fordham-Latta</th>\n      <th>M.Ed</th>\n      <th>ku.cobbitty@ku.com.au</th>\n      </tr>\n    "}
]

//var data = null;
var mymap = null;
var markers = [];

// Functions for populating the map

var initializeMap = function() {
  mapboxgl.accessToken = "pk.eyJ1IjoiZmllbGRjYWR5IiwiYSI6ImNqd3Rmb2d3bjBkMDA0OW5yamYxNnRwdGwifQ.kBilx8iMkTn8RUyrO7ZHGA";
  mymap = new mapboxgl.Map({
    container: 'mapid',
    style: 'mapbox://styles/mapbox/streets-v9',
    //center: [-120.661, 47.596],
    //zoom: 5,
    //maxZoom: 13,
    //maxBounds: [[-130, 45], [-110, 50]]
  });
}


var downloadDataAndRender = function(url) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'json';
    console.log('downloading', url);
    xhr.onload = function() {
      data=xhr.response;
      console.log('xhr', xhr);
      console.log('data:')
      console.log(data);
      renderData(data);
    };
    xhr.send();
};

var renderData = function(dat) {
  console.log('foo');
  //console.log(dat['marker_blobs'].length);
  addMarkersToMap(dat['marker_blobs']);
}

var addMarkersToMap = function(blobs) {
  console.log('adding', blobs.length, 'markers');
  for (var j=0; j<blobs.length; j++) {
    vio = blobs[j];
    color = 'blue'
    m = new mapboxgl.Marker({color: color})
      .setLngLat([vio['lon'], vio['lat']]);
    var popup = new mapboxgl.Popup().setHTML(vio['html']);
    m.setPopup(popup);
    m.addTo(mymap);
    //
    m.violation = vio;
    vio.marker = m;
    markers.push(m);
  };
  
}


initializeMap()

if (location.origin === "file://") {
    //data = DEFAULT_DATA
    renderData(DEFAULT_DATA);
  } else {
    console.log('In the Cloud');
    downloadDataAndRender("esdm_data.json");
}
