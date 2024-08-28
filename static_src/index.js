let map;
let markers = [];
let cluster = null;
let currentInfoWindow = null;

async function initMap() {
    const {Map} = await google.maps.importLibrary("maps");

    map = new Map(document.getElementById("map"), {
        center: {lat: -23.641479, lng: -58.280955},
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
            const marker = new AdvancedMarkerElement({
                position: {lat: parseFloat(establishment.latitude), lng: parseFloat(establishment.longitude)},
                map,
                title: location.name // Optional: You can set the title to show on hover
            });
            const infoWindow = new google.maps.InfoWindow({
                content: `<div>
                            <h3 class="is-size-6 mb-2 has-text-weight-bold">${location.name}</h3>
                            <div class="is-flex">
<!--                            <div class="mr-2">-->
<!--                              <p class="my-1"><strong>Total<br/>desembolsado:</strong></p>-->
<!--                              <p>Gs. 17.000.000</p>-->
<!--                              </div>-->
<!--                              <div class="ml-1">-->
<!--                            <p class="my-1"><strong>Total<br/>rendido:</strong></p>-->
<!--                            <p>Gs. 15.000.000</p>-->
<!--                            </div>-->
                            </div>
                            
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