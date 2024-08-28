const endpoints = {
    'Instituciones': '/api/institutions/',
    'Desembolsos': '/api/disbursements/',
    'Rendiciones': '/api/reports/',
    'Comprobantes': '/api/receipts/',
}

const columnNames = {
    'Instituciones': [
        "ID",
        "Código MEC",
        "Nombre",
        "Tipo",
        "Dirección",
        "Teléfono",
        "Sitio Web",
        "Email",
        "Latitud",
        "Longitud",
        "Localidad",
        "Distrito",
        "Departamento"
    ],
    'Desembolsos': [
        'ID',
        'Resolución',
        'ID Institución',
        'Nombre Institución',
        'Fecha desembolso',
        'Monto desembolso',
        'Origen del fondo',
        'Marco',
        'Fecha a rendir',
        'Nombre Director',
        'CI Director',
        'Tipo de pago',
    ],
    'Rendiciones': [
        'ID',
        'ID desembolso',
        'ID institución',
        'Nombre institución',
        'Estado',
        'Recepción',
    ],
    'Comprobantes': [
        'ID',
        'ID rendición',
        'Tipo comprobante',
        'Nro comprobante',
        'Fecha comprobante',
        'Objeto de gasto',
        'Conceptos',
        'Total'
    ]
}


function resourcesData() {
    return {
        results: [],
        next: null,
        previous: null,
        loading: true,
        collection: 'Instituciones',
        total: 0,

        fetchData(url = null) {
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('collection')) {
                this.collection = urlParams.get('collection')
            }

            if (!url) {
                url = endpoints[this.collection];
            }

            this.loading = true;
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    this.results = data.results;
                    this.next = data.next;
                    this.previous = data.previous;
                    this.total = data.count;
                    this.loading = false;
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                });
        },
        setCollection(collection) {
            let url = new URL(window.location.href);
            url.searchParams.set('collection', collection);
            window.history.pushState({}, '', url);
            this.fetchData();
        },
        getHeaders() {
            return columnNames[this.collection];
        },
        mapCollection() {
            return this.results?.map(result => {
                switch (this.collection) {
                    case "Instituciones":
                        return [
                            result.id,
                            result.code,
                            result.name,
                            result.institutionType,
                            result.establishment.address,
                            result.phoneNumber,
                            result.website,
                            result.email,
                            result.establishment.latitude,
                            result.establishment.longitude,
                            result.establishment.locality.name,
                            result.establishment.locality.district.name,
                            result.establishment.locality.district.department.name,
                        ];
                    case "Desembolsos":
                        return [
                            result.id,
                            `${result.resolution.documentNumber}/${result.resolution.documentYear}`,
                            result.institutionId,
                            result.institutionName,
                            result.disbursementDate,
                            result.amountDisbursed,
                            result.fundsOrigin,
                            result.originDetails,
                            result.dueDate,
                            result.principalName,
                            result.principalIssuedId,
                            result.paymentType,
                        ]
                    case 'Rendiciones':
                        return [
                            result.id,
                            result.disbursement.id,
                            result.disbursement.institutionId,
                            result.disbursement.institutionName,
                            result.status.value,
                            result.deliveredVia,
                        ]
                    case 'Comprobantes':
                        return [
                            result.id,
                            result.reportId,
                            result.receiptType.name,
                            result.receiptNumber,
                            result.receiptDate,
                            result.objectOfExpenditure,
                            result.description,
                            result.total,
                        ];
                    default:
                        return []
                }
            })
        },
        getExportUrl(format) {
            let base = `/export/?format=${format}&collection=`;
            switch (this.collection) {
                case "Instituciones":
                    return base + 'institutions';
                case "Desembolsos":
                    return base + 'disbursements';
                case "Rendiciones":
                    return base + 'reports';
                case "Comprobantes":
                    return base + 'receipts';
            }
        }
    };
}