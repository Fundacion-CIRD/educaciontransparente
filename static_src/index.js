const departmentCenters = {
  "20": {lat: -25.2637, lng: -57.5759},
  "00": {lat: -25.2637, lng: -57.5759},
  "17": {lat: -20.0307, lng: -58.2825},
  "10": {lat: -25.4167, lng: -54.6167},
  "13": {lat: -22.3375, lng: -56.2300},
  "16": {lat: -22.5833, lng: -60.0833},
  "05": {lat: -25.4500, lng: -56.0167},
  "06": {lat: -26.2000, lng: -56.3667},
  "14": {lat: -24.1500, lng: -55.6667},
  "11": {lat: -25.3667, lng: -57.6333},
  "01": {lat: -23.4000, lng: -57.4333},
  "03": {lat: -25.3167, lng: -57.1500},
  "04": {lat: -25.7500, lng: -56.4167},
  "07": {lat: -27.1667, lng: -55.6667},
  "08": {lat: -26.5000, lng: -57.0000},
  "12": {lat: -27.0833, lng: -58.0000},
  "09": {lat: -25.6200, lng: -57.1500},
  "15": {lat: -23.1000, lng: -58.4500},
  "02": {lat: -24.1000, lng: -57.0833}
};

const paraguayCenter = {lat: -23.641479, lng: -58.280955}

let map;
let markers = [];
let cluster = null;
let currentInfoWindow = null;

async function initMap() {
  const {Map} = await google.maps.importLibrary("maps");

  map = new Map(document.getElementById("map"), {
    center: paraguayCenter,
    zoom: 6,
    mapId: "institutionsMap",
    gestureHandling: "greedy",
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: false,
  });
}

async function fetchPointsAndAddToMap(selectedFilters = {}) {
  const {AdvancedMarkerElement} = await google.maps.importLibrary("marker");

  const queryParams = new URLSearchParams();
  queryParams.append('limit', '1000');
  if (selectedFilters.departments)
    queryParams.append("department", selectedFilters.departments);
  if (selectedFilters.districts)
    queryParams.append("district", selectedFilters.districts.id);
  if (selectedFilters.institutions)
    queryParams.append('id', selectedFilters.institutions.id);

  clearMarkers();

  try {
    // Replace with your API endpoint
    const response = await fetch('/api/institutions/?' + queryParams.toString());

    const locations = await response.json();

    locations.results.forEach(location => {
      const establishment = location.establishment;
      if (!establishment.latitude || !establishment.longitude)
        return;
      const marker = new AdvancedMarkerElement({
        position: {lat: parseFloat(establishment.latitude), lng: parseFloat(establishment.longitude)},
        map,
        title: location.name // Optional: You can set the title to show on hover
      });
      const infoWindow = new google.maps.InfoWindow({
        content: `<div>
                            <h3 class="is-size-6 mb-2 has-text-weight-bold">${location.name}</h3>
                            <p class="mt-2 has-text-weight-semibold"><a href="/instituciones/${location.id}">Detalles</a></p>
                          </div>`
      });
      marker.addListener('click', () => {
        if (currentInfoWindow)
          currentInfoWindow.close();
        infoWindow.open(map, marker);
        currentInfoWindow = infoWindow;
      });
      markers.push(marker);
    });
    cluster = new markerClusterer.MarkerClusterer({markers, map});
    return locations.summary;
  } catch (error) {
    console.error('Error fetching locations:', error);
  }
}


function clearMarkers() {
  if (cluster) {
    cluster.clearMarkers();
    cluster.setMap(null);
    cluster = null;
  }
  markers.forEach(marker => {
    marker.setMap(null);
  });
  markers = [];
}


function mapFormComponent() {
  return {
    timeout: null,
    queries: {
      institutions: '',
      districts: '',
    },
    results: {
      institutions: [],
      districts: [],
    },
    open: {
      institutions: false,
      districts: false,
    },
    selected: {
      departments: null,
      districts: null,
      institutions: null,
    },
    selectedIndex: {
      institutions: -1,
      districts: -1,
    },
    summary: {
      totalDisbursed: 0,
      totalReported: 0,
    },

    async init() {
      await initMap();
      this.summary = await fetchPointsAndAddToMap();
    },

    async fetchResults(collection) {
      if (this.queries[collection].length < 2) {
        this.open[collection] = false;
        this.results[collection] = [];
        this.selected[collection] = null;
        this.summary = await fetchPointsAndAddToMap(this.selected);
        return;
      }

      const params = new URLSearchParams();
      if (this.selected.departments)
        params.append('department', this.selected.departments);
      if (collection === 'institutions' && this.selected.districts)
        params.append('district', this.selected.districts.id);
      params.append('search', this.queries[collection]);

      const response = await fetch(`/api/${collection}?${params.toString()}`)
      const data = await response.json();
      this.results[collection] = data.results;
      this.open[collection] = true;
    },

    debouncedFetchResults(collection) {
      clearTimeout(this.timeout);
      this.timeout = setTimeout(() => this.fetchResults(collection), 300);
    },

    async selectResult(collection, item) {
      this.queries[collection] = item.name;
      this.selected[collection] = item;
      this.open[collection] = false;
      this.summary = await fetchPointsAndAddToMap(this.selected);
    },

    async selectDepartment(event) {
      this.selected.departments = event.target.value;
      this.summary = await fetchPointsAndAddToMap(this.selected);
      const departmentCode = event.target.selectedOptions[0].dataset.department;
      const departmentCenter = departmentCenters[departmentCode];
      if (!this.selected.departments) {
        map.setCenter(paraguayCenter);
        map.setZoom(6);
        return;
      }
      if (departmentCenter) {
        map.setCenter(departmentCenter);
        map.setZoom(8);
      }
    },

  }
}

function autocompleteComponent(apiEndpoint, filterName) {
  return {
    query: '',
    results: [],
    open: false,
    selectedIndex: -1,
    timeout: null,

    fetchResults() {
      if (this.query.length < 2) {
        this.results = [];
        this.open = false;
        selectedFilters[filterName] = null;
        fetchPointsAndAddToMap()
        return;
      }

      fetch(`${apiEndpoint}?search=${this.query}`)
        .then(response => response.json())
        .then(data => {
          this.results = data.results;
          this.open = true;
        });
    },

    debouncedFetchResults() {
      clearTimeout(this.timeout);
      this.timeout = setTimeout(() => this.fetchResults(), 300);
    },

    selectResult(result) {
      this.query = result.name;
      this.open = false;
      selectedFilters[filterName] = result;
      fetchPointsAndAddToMap()
    },
  };
}

// Usage
function autocompleteDistrict() {
  return autocompleteComponent('/api/districts/', 'district');
}

function autocompleteInstitution() {
  return autocompleteComponent('/api/institutions/', 'institution');
}