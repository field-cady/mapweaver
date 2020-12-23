
// Global Variables

var DEFAULT_DATA = {"violations": [
{"Facility Name": "foo1", "Permit Number": "ST0006224", "Permit Status": "Active", "Permit Type": "Municipal to ground SWDP IP", "City": "Belfair", "County": "Mason", "Violation Date": "9/10/2020", "Is Addressed": "No", "Category": "Reporting Violations","Type": "Numeric effluent violation", "Parameter": " ", "Units": " ", "Statistical Base": " ", "Measurement Value": "2.998", "Benchmark/Limit": " ", "Violation Notes": " ", "Violation Override": " ", "Feature Name": " ", "ViolationId": "1638800", "FacilityId": "17635", "let": 47.464685, "lon": -122.809039, "lat": 47.464685},
{"Facility Name": "foo2", "Permit Number": "ST0006224", "Permit Status": "Active", "Permit Type": "Municipal to ground SWDP IP", "City": "Belfair", "County": "Mason", "Violation Date": "9/9/2020", "Is Addressed": "No", "Category": "Effluent Violations", "Type": "Numeric effluent violation", "Parameter": " ", "Units": " ", "Statistical Base": " ", "Measurement Value": "2.998", "Benchmark/Limit": " ", "Violation Notes": " ", "Violation Override": " ", "Feature Name": " ", "ViolationId": "1639118", "FacilityId": "17635", "let": 47.464685, "lon": -122.809039, "lat": 47.564685},
{"Facility Name": "foo3", "Permit Number": "ST0006224", "Permit Status": "Active", "Permit Type": "Municipal to ground SWDP IP", "City": "Belfair", "County": "Mason", "Violation Date": "9/8/2020", "Is Addressed": "No", "Category": "Effluent Violations", "Type": "Numeric effluent violation", "Parameter": " ", "Units": " ", "Statistical Base": " ", "Measurement Value": "2.997", "Benchmark/Limit": " ", "Violation Notes": " ", "Violation Override": " ", "Feature Name": " ", "ViolationId": "1638802", "FacilityId": "17635", "let": 47.464685, "lon": -122.809039, "lat": 47.464685},
{"Facility Name": "foo4", "Permit Number": "ST0006206", "Permit Status": "Active", "Permit Type": "Municipal to ground SWDP IP", "City": "LACEY", "County": "Thurston", "Violation Date": "9/6/2020", "Is Addressed": "No", "Category": "Monitoring Violations", "Type": "Analysis not Conducted", "Parameter": " ", "Units": " ", "Statistical Base": " ", "Measurement Value": " ", "Benchmark/Limit": " ", "Violation Notes": " ", "Violation Override": " ", "Feature Name": " ", "ViolationId": "1638438", "FacilityId": "5905309", "let": 47.0493011474609, "lon": -122.801742553711, "lat": 47.0493011474609}
]}

//var data = null;
var mymap = null;
var markers = [];

// Functions for populating the map

var initializeMap = function() {
  mapboxgl.accessToken = "pk.eyJ1IjoiZmllbGRjYWR5IiwiYSI6ImNqd3Rmb2d3bjBkMDA0OW5yamYxNnRwdGwifQ.kBilx8iMkTn8RUyrO7ZHGA";
  mymap = new mapboxgl.Map({
    container: 'mapid',
    style: 'mapbox://styles/mapbox/streets-v9',
    center: [-120.661, 47.596],
    zoom: 5,
    maxZoom: 13,
    maxBounds: [[-130, 45], [-110, 50]]
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
  addViolationsToMap(dat["violations"]);
  updateMarkers();
}

var addViolationsToMap = function(violations) {
  console.log('adding', violations.length, 'violations');
  for (i=0; i<violations.length; i++) {
    vio = violations[i];
    color = 'blue'
    m = new mapboxgl.Marker({color: color})
      .setLngLat([vio['lon'], vio['lat']]);
    var popup = new mapboxgl.Popup().setHTML(violation2marker_html(vio));
    m.setPopup(popup);
    m.addTo(mymap);
    //
    m.violation = vio;
    vio.marker = m;
    markers.push(m);
  };
}


// Helper utility functions
/*
{"Facility Name": "foo4", "Permit Number": "ST0006206", "Permit Status": "Active", "Permit Type": 
"Municipal to ground SWDP IP", "City": "LACEY", "County": "Thurston", "Violation Date": "9/6/2020", "Is Addressed": "No", 
"Category": "Monitoring Violations", "Type": "Analysis not Conducted", "Parameter": " ", "Units": " ", "Statistical Base": " ", 
"Measurement Value": " ", "Benchmark/Limit": " ", "Violation Notes": " ", "Violation Override": " ", "Feature Name": " ", 
"ViolationId": "1638438", "FacilityId": "5905309", "let": 47.0493011474609, "lon": -122.801742553711, "lat": 47.0493011474609}
*/

var violation2marker_html = function(vio) {
  violation_url = 'https://apps.ecology.wa.gov/paris/ComplianceAndViolations/PopupViolationTrigger.aspx?ViolationId='+vio['ViolationId']
  clickable_name = '<h3>Facility:</h3><a target="_blank" href="'+violation_url+'">'+vio['Facility Name']+'</a>'
  category = '<h3>Category:</h3>'+vio['Category']
  permit_type = '<h3>Permit Type:</h3>'+vio['Permit Type']
  date = '<h3>Violation Date:</h3>'+vio['Violation Date']
  is_addressed = '<h3>Is Addressed:</h3>'+vio['Is Addressed']
  //return clickable_name + '<br>' + category + '<br>' + permit_type + '<br>' + date + '<br>' + is_addressed
  return clickable_name +  category +  permit_type +  date +  is_addressed
}

var MAIN_CATEGORIES = ['Monitoring Violations', 'Effluent Violations', 'Reporting Violations']
var MAIN_TYPES = [
    'Municipal NPDES IP',
    'Industrial NPDES IP',
    'Industrial (IU) to POTW/PRIVATE SWDP IP',
    'Municipal to ground SWDP IP',
    'Industrial to ground SWDP IP',
    'Sand and Gravel GP',
    'Reclaimed Water IP'
];
var getFilterFunction = function() {
  console.log('in getFilterFunction')
  // Reads current filter settings and returns a function that says whether
  // a lake passes those filters

  // Type
  //var show_category = document.getElementById('categorySelect').checked;

  var category_select = document.getElementById('categorySelect');
  var categories_selected = [...category_select.options]
                    .filter(option => option.selected)
                    .map(option => option.value);

  var type_select = document.getElementById('typeSelect');
  var types_selected = [...type_select.options]
                    .filter(option => option.selected)
                    .map(option => option.value);
  console.log('categories', categories_selected);
  console.log('types_selected',types_selected);
  
  
  var type_filter = function(tp) {
    if (MAIN_TYPES.includes(tp)) {
      return types_selected.includes(tp)
    } else {
      return types_selected.includes('Other')
    }
  }
  var category_filter = function(ct) {
    if (MAIN_CATEGORIES.includes(ct)) {
      return categories_selected.includes(ct)
    } else {
      return categories_selected.includes('Other')
    }
  }

  return function(vio){
    return category_filter(vio.Category) & type_filter(vio['Permit Type'])
  }


}

// Top-level functions below this line

function toggleLoading() {
console.log('foo');
  var popup = document.getElementById("myPopup");
  popup.classList.toggle("show");
}
var updateMarkers = function() {
  console.log('in updateMarkers');
  //document.getElementById("loader").style.display = "block";
  //sleep(5000);
  filter_func = getFilterFunction()
  for (i=0; i<markers.length; i++) {
    m = markers[i];
    vio = m.violation;
    if (filter_func(vio)) {
      m.addTo(mymap);
    } else {
      m.remove(mymap);
    }
  };
  //myFunction();
  //document.getElementById("loader").style.display = "none";
}
var updateMarkersWithLoader = function() {
  //setTimeout(loaderOn,10);
  loaderOn();
  setTimeout(function(){
    updateMarkers();
    setTimeout(loaderOff,500);
  },500);
}

function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}

initializeMap()

if (location.origin === "file://") {
    //data = DEFAULT_DATA
    renderData(DEFAULT_DATA);
  } else {
    console.log('In the Cloud');
    downloadDataAndRender("data/paris_violations.json");
}
