const endpoints = {
  'Instituciones': '/api/institutions/',
  'Desembolsos': '/api/disbursements/',
  'Rendiciones': '/api/reports/',
  'Comprobantes': '/api/receipts/',
  'Detalles de comprobante': '/api/receipt-items/',
}

const columnNames = {
  'Instituciones': [
    "ID",
    "Código MEC Establecimiento",
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
    'Monto Resolución',
    'Monto desembolsado',
    'Origen del fondo',
    'Marco',
    'Fecha a rendir',
    'Nombre Director',
    'CI Director',
    'Tipo de pago',
    'Observaciones',
  ],
  'Rendiciones': [
    'ID',
    'ID desembolso',
    'ID institución',
    'Nombre institución',
    'Fecha rendición',
    'Monto rendido',
    'Recepción',
    'Observaciones',
  ],
  'Comprobantes': [
    'ID',
    'ID institución',
    'Nombre institución',
    'ID desembolso',
    'ID rendición',
    'Tipo comprobante',
    'Nro comprobante',
    'RUC proveedor',
    'Nombre proveedor',
    'Fecha comprobante',
    'Total',
  ],
  'Detalles de comprobante': [
    'ID',
    'ID comprobante',
    'Objeto de gasto',
    'Cantidad',
    'Descripción',
    'Precio unitario',
  ]
}

const dataDictionary = {
  'Instituciones': [
    {
      "name": "ID",
      "description": "Identificador único de la institución",
      "type": "integer",
      "example": "50213"
    },
    {
      "name": "Código MEC Establecimiento",
      "description": "Código único asignado al establecimiento por el Ministerio de Educación y Ciencias",
      "type": "string",
      "example": "1114036"
    },
    {
      "name": "Código MEC",
      "description": "Código del MEC para la institución",
      "type": "string",
      "example": "8508"
    },
    {
      "name": "Nombre",
      "description": "Nombre de la institución",
      "type": "string",
      "example": "CENTRO REGIONAL DE EDUCACIÓN SATURIO RÍOS"
    },
    {
      "name": "Tipo",
      "description": "Tipo de establecimiento (Oficial, Privado, etc.)",
      "type": "string",
      "example": "OFICIAL"
    },
    {
      "name": "Dirección",
      "description": "Dirección física del establecimiento",
      "type": "string",
      "example": "GARIVALDI CASI TTE. MASCHIO"
    },
    {
      "name": "Teléfono",
      "description": "Número de teléfono de la institución",
      "type": "string",
      "example": "582386"
    },
    {
      "name": "Sitio Web",
      "description": "Sitio web oficial de la institución",
      "type": "string",
      "example": ""
    },
    {
      "name": "Email",
      "description": "Correo electrónico de contacto de la institución",
      "type": "string",
      "example": ""
    },
    {
      "name": "Latitud",
      "description": "Coordenada de latitud de la ubicación del establecimiento",
      "type": "string",
      "example": "-25.34852583"
    },
    {
      "name": "Longitud",
      "description": "Coordenada de longitud de la ubicación del establecimiento",
      "type": "string",
      "example": "-57.51468806"
    },
    {
      "name": "Localidad",
      "description": "Localidad o ciudad donde se encuentra el establecimiento",
      "type": "string",
      "example": "SAN ANTONIO - CIUDAD"
    },
    {
      "name": "Distrito",
      "description": "Distrito al que pertenece el establecimiento",
      "type": "string",
      "example": "SAN LORENZO"
    },
    {
      "name": "Departamento",
      "description": "Departamento al que pertenece el establecimiento",
      "type": "string",
      "example": "CENTRAL"
    }
  ],
  'Desembolsos': [
    {
      "name": "ID",
      "description": "Identificador único del desembolso",
      "type": "integer",
      "example": "26647"
    },
    {
      "name": "Resolución",
      "description": "Número de la resolución que aprueba el desembolso",
      "type": "string",
      "example": "490/2020"
    },
    {
      "name": "ID Institución",
      "description": "Identificador único de la institución que recibe el desembolso",
      "type": "integer",
      "example": "48033"
    },
    {
      "name": "Nombre Institución",
      "description": "Nombre de la institución que recibe el desembolso",
      "type": "string",
      "example": "ESCUELA BÁSICA N° 215 PROFESOR EMILIO FERREIRA"
    },
    {
      "name": "Fecha desembolso",
      "description": "Fecha en la que se realizó el desembolso",
      "type": "string",
      "example": "2020-06-03"
    },
    {
      "name": "Monto Resolución",
      "description": "Monto total aprobado en la resolución para el desembolso",
      "type": "integer",
      "example": "1920150"
    },
    {
      "name": "Monto desembolsado",
      "description": "Monto realmente desembolsado a la institución",
      "type": "integer",
      "example": "1920150"
    },
    {
      "name": "Origen del fondo",
      "description": "Fuente u origen del fondo del desembolso",
      "type": "integer",
      "example": "834"
    },
    {
      "name": "Marco",
      "description": "Descripción del marco legal o programa en el cual se enmarca el desembolso",
      "type": "string",
      "example": "Gratuidad de la educación inicial primero, segundo y tercer ciclo"
    },
    {
      "name": "Fecha a rendir",
      "description": "Fecha límite para la rendición de cuentas del desembolso",
      "type": "string",
      "example": "2020-12-18"
    },
    {
      "name": "Nombre Director",
      "description": "Nombre del director de la institución receptora",
      "type": "string",
      "example": "Rocio Alice Amarilla de Rolón"
    },
    {
      "name": "CI Director",
      "description": "Número de cédula de identidad del director de la institución receptora",
      "type": "string",
      "example": "1238560"
    },
    {
      "name": "Tipo de pago",
      "description": "Método de pago utilizado para el desembolso",
      "type": "string",
      "example": "Transferencia bancaria"
    },
    {
      "name": "Observaciones",
      "description": "Cualquier comentario o información adicional relacionada con el desembolso",
      "type": "string",
      "example": ""
    }
  ],
  'Rendiciones': [
    {
      "name": "ID",
      "description": "Identificador único de la rendición",
      "type": "integer",
      "example": "25769"
    },
    {
      "name": "ID desembolso",
      "description": "Identificador del desembolso relacionado con la rendición",
      "type": "integer",
      "example": "26241"
    },
    {
      "name": "ID institución",
      "description": "Identificador de la institución que realiza la rendición",
      "type": "integer",
      "example": "48996"
    },
    {
      "name": "Nombre institución",
      "description": "Nombre de la institución que realiza la rendición",
      "type": "string",
      "example": "COLEGIO NACIONAL REPÚBLICA DOMINICANA"
    },
    {
      "name": "Fecha rendición",
      "description": "Fecha en que se realizó la rendición de cuentas",
      "type": "string",
      "example": null
    },
    {
      "name": "Monto rendido",
      "description": "Monto total rendido por la institución",
      "type": "integer",
      "example": "5025000"
    },
    {
      "name": "Recepción",
      "description": "Método o estado de recepción de la rendición",
      "type": "string",
      "example": "Rendido por el RUE"
    },
    {
      "name": "Observaciones",
      "description": "Comentarios adicionales sobre la rendición",
      "type": "string",
      "example": ""
    }
  ],
  'Comprobantes': [
    {
      "name": "ID",
      "description": "Identificador único del comprobante",
      "type": "integer",
      "example": "143232"
    },
    {
      "name": "ID institución",
      "description": "Identificador de la institución que recibe el comprobante",
      "type": "integer",
      "example": "48996"
    },
    {
      "name": "ID desembolso",
      "description": "Identificador del desembolso relacionado con el comprobante",
      "type": "integer",
      "example": "26241"
    },
    {
      "name": "ID rendición",
      "description": "Identificador de la rendición relacionada con el comprobante",
      "type": "integer",
      "example": "25769"
    },
    {
      "name": "Tipo comprobante",
      "description": "Tipo de comprobante emitido (factura, recibo, etc.)",
      "type": "string",
      "example": "Factura Contado"
    },
    {
      "name": "Nro comprobante",
      "description": "Número del comprobante emitido",
      "type": "string",
      "example": "001-001-0000263"
    },
    {
      "name": "RUC proveedor",
      "description": "RUC del proveedor que emitió el comprobante",
      "type": "string",
      "example": "4531980-4"
    },
    {
      "name": "Nombre proveedor",
      "description": "Nombre del proveedor que emitió el comprobante",
      "type": "string",
      "example": "Fernando Santa Cruz Cáceres"
    },
    {
      "name": "Fecha comprobante",
      "description": "Fecha de emisión del comprobante",
      "type": "string",
      "example": "2023-07-29"
    },
    {
      "name": "Total",
      "description": "Monto total del comprobante",
      "type": "integer",
      "example": "450000"
    }
  ],
  'Detalles de comprobante': [
    {
      "name": "ID",
      "description": "Identificador único del detalle del comprobante",
      "type": "integer",
      "example": "6898"
    },
    {
      "name": "ID comprobante",
      "description": "Identificador del comprobante relacionado con este detalle",
      "type": "integer",
      "example": "143218"
    },
    {
      "name": "Objeto de gasto",
      "description": "Código y descripción del objeto de gasto relacionado con el comprobante",
      "type": "string",
      "example": "248: Otros mantenimientos y reparaciones menores"
    },
    {
      "name": "Cantidad",
      "description": "Cantidad de productos o servicios adquiridos",
      "type": "integer",
      "example": "1"
    },
    {
      "name": "Descripción",
      "description": "Descripción del bien o servicio adquirido",
      "type": "string",
      "example": "Reparación y configuración de cámaras de seguridad"
    },
    {
      "name": "Precio unitario",
      "description": "Precio unitario de cada bien o servicio adquirido",
      "type": "integer",
      "example": "1300000"
    }
  ]
}


function resourcesData() {
  return {
    results: [],
    next: null,
    previous: null,
    loading: true,
    showModal: false,
    collection: 'Instituciones',
    total: 0,
    timeout: null,
    open: {
      districts: false,
      resolutions: false,
    },
    queries: {
      institution: '',
      district: '',
      department: '',
      institutionType: '',
      resolution: '',
      disbursementId: '',
      reportId: '',
      receiptId: '',
    },
    selectedFilters: {
      institution: null,
      district: null,
      department: null,
      institutionType: null,
      disbursementOrigin: null,
      disbursementBefore: null,
      disbursementAfter: null,
      reportDateBefore: null,
      reportDateAfter: null,
      receiptDateBefore: null,
      receiptDateAfter: null,
      resolution: null,
      receiptType: null,
      objectOfExpenditure: null,
    },
    selectedDistrict: null,
    selectedDepartment: null,
    selectedInstitutionType: null,
    filterResults: {
      districts: [],
      resolutions: [],
      institutions: [],
    },
    selectedIndex: {
      districts: null,
    },
    init() {
      switch (document.location.pathname.split('/')[2]) {
        case 'institutions':
          this.collection = 'Instituciones';
          break;
        case 'disbursements':
          this.collection = 'Desembolsos';
          break;
        case 'reports':
          this.collection = 'Rendiciones';
          break;
        case 'receipts':
          this.collection = 'Comprobantes';
          break;
        case 'receipt-items':
          this.collection = 'Detalles de comprobante';
          break;
        default:
          break;
      }
      this.fetchData();
    },

    getColumnNames() {
      return dataDictionary[this.collection]
    },

    toggleModal() {
      this.showModal = !this.showModal;
    },

    async fetchDistricts() {
      if (this.queries.district.length < 2) {
        this.open.districts = false;
        this.selectedFilters.district = null;
        this.fetchData();
        return;
      }
      const params = new URLSearchParams()
      if (this.selectedDepartment) params.append('department', this.selectedDepartment);
      params.append('search', this.queries.district);
      const response = await fetch(`/api/districts/?${params.toString()}`)
      const data = await response.json();
      this.filterResults.districts = data.results;
      this.open.districts = true;
    },

    selectDistrict(item) {
      this.selectedFilters.district = item;
      this.queries.district = item.name;
      this.open.districts = false;
      this.fetchData();
    },

    async fetchResolutions() {
      if (this.queries.resolution.length < 2) {
        this.open.resolutions = false;
        this.selectedFilters.resolution = null;
        this.fetchData();
        return;
      }
      const params = new URLSearchParams()
      params.append('search', this.queries.resolution);
      const response = await fetch(`/api/resolutions/?${params.toString()}`)
      const data = await response.json();
      this.filterResults.resolutions = data.results;
      this.open.resolutions = true;
    },

    selectResolution(item) {
      this.selectedFilters.resolution = item;
      this.queries.resolution = item.fullDocumentNumber;
      this.open.resolutions = false;
      this.fetchData();
    },

    async fetchInstitutions() {
      if (this.queries.institution.length < 2) {
        this.open.institutions = false;
        this.selectedFilters.institution = null;
        this.fetchData();
        return;
      }
      const params = new URLSearchParams()
      params.append('search', this.queries.institution);
      const response = await fetch(`/api/institutions/?${params.toString()}`)
      const data = await response.json();
      this.filterResults.institutions = data.results;
      this.open.institutions = true;
    },

    selectInstitution(item) {
      this.selectedFilters.institution = item;
      this.queries.institution = item.name;
      this.open.institutions = false;
      this.fetchData();
    },

    selectDepartment(event) {
      this.selectedFilters.department = event.target.value;
      this.fetchData();
    },

    selectReceiptType(event) {
      this.selectedFilters.receiptType = event.target.value;
      this.fetchData();
    },

    selectDisbursementOrigin(event) {
      this.selectedFilters.disbursementOrigin = event.target.value;
      this.fetchData();
    },

    selectInstitutionType(event) {
      this.selectedFilters.institutionType = event.target.value;
      this.fetchData();
    },

    selectDisbursementBefore(event) {
      this.selectedFilters.disbursementBefore = event.target.value;
      this.fetchData();
    },

    selectDisbursementAfter(event) {
      this.selectedFilters.disbursementAfter = event.target.value;
      this.fetchData();
    },

    selectReportDateBefore(event) {
      this.selectedFilters.reportDateBefore = event.target.value;
      this.fetchData();
    },

    selectReportDateAfter(event) {
      this.selectedFilters.reportDateAfter = event.target.value;
      this.fetchData();
    },

    selectReceiptDateBefore(event) {
      this.selectedFilters.receiptDateBefore = event.target.value;
      this.fetchData();
    },

    selectReceiptDateAfter(event) {
      this.selectedFilters.receiptDateAfter = event.target.value;
      this.fetchData();
    },

    selectAccountObject(event) {
      this.selectedFilters.objectOfExpenditure = event.target.value;
      this.fetchData();
    },


    fetchFilterList(_collection) {
      switch (_collection) {
        case 'districts':
          void this.fetchDistricts();
          return;
        case 'institutions':
          if (this.collection === 'Instituciones') {
            this.fetchData();
            return;
          }
          this.fetchInstitutions();
          break;
        case 'resolutions':
          this.fetchResolutions();
          break;
        case 'disbursement':
          this.fetchData();
          break;
        case 'report':
          this.fetchData();
          break;
        case 'receipt':
          this.fetchData();
          break;
      }
    },

    debouncedFetchFilterList(collection) {
      clearTimeout(this.timeout);
      this.timeout = setTimeout(() => this.fetchFilterList(collection), 300);
    },

    fetchData(url = null) {
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.has('collection')) {
        this.collection = urlParams.get('collection')
      }

      if (!url) {

        const params = new URLSearchParams();
        params.append('limit', '20');
        if (this.selectedFilters.district) params.append('district', this.selectedFilters.district.id);
        if (this.selectedFilters.department) params.append('department', this.selectedFilters.department);
        if (this.selectedFilters.institutionType) params.append('institution_type', this.selectedFilters.institutionType);
        if (this.collection === 'Instituciones' && this.queries.institution) params.append('name', this.queries.institution);
        if (this.selectedFilters.disbursementOrigin) params.append('funds_origin', this.selectedFilters.disbursementOrigin);
        if (this.selectedFilters.disbursementBefore) params.append('disbursement_date_before', this.selectedFilters.disbursementBefore);
        if (this.selectedFilters.disbursementAfter) params.append('disbursement_date_after', this.selectedFilters.disbursementAfter);
        if (this.selectedFilters.reportDateBefore) params.append('report_date_before', this.selectedFilters.reportDateBefore);
        if (this.selectedFilters.reportDateAfter) params.append('report_date_after', this.selectedFilters.reportDateAfter);
        if (this.selectedFilters.receiptDateBefore) params.append('receipt_date_before', this.selectedFilters.receiptDateBefore);
        if (this.selectedFilters.receiptDateAfter) params.append('receipt_date_after', this.selectedFilters.receiptDateAfter);
        if (this.selectedFilters.resolution) params.append('resolution', this.selectedFilters.resolution.id);
        if (this.selectedFilters.institution) params.append('institution', this.selectedFilters.institution.id);
        if (this.queries.disbursementId) params.append('disbursement', this.queries.disbursementId);
        if (this.queries.reportId) params.append('report', this.queries.reportId);
        if (this.selectedFilters.receiptType) params.append('receipt_type', this.selectedFilters.receiptType);
        if (this.queries.receiptId) params.append('receipt', this.queries.receiptId);
        if (this.selectedFilters.objectOfExpenditure) params.append('object_of_expenditure', this.selectedFilters.objectOfExpenditure);
        url = endpoints[this.collection] + `?${params.toString()}`;
      }

      this.loading = true;
      fetch(url)
        .then(response => response.json())
        .then(data => {
          this.next = data.next;
          this.previous = data.previous;
          this.total = data.count;
          this.results = data.results;
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
      if (!this.results) return [];
      return this.results.map(result => {
        switch (this.collection) {
          case "Instituciones":
            return [
              result.id,
              result.establishment?.code,
              result.code,
              result.name,
              result.institutionType,
              result.establishment?.address,
              result.phoneNumber,
              result.website,
              result.email,
              result.establishment?.latitude,
              result.establishment?.longitude,
              result.establishment?.locality.name,
              result.establishment?.locality.district.name,
              result.establishment?.locality.district.department.name,
            ];
          case "Desembolsos":
            return [
              result.id,
              `${result.resolution?.documentNumber}/${result.resolution?.documentYear}`,
              result.institutionId,
              result.institutionName,
              result.disbursementDate,
              result.resolutionAmount,
              result.amountDisbursed,
              result.fundsOrigin.code,
              result.originDetails.name,
              result.dueDate,
              result.principalName,
              result.principalIssuedId,
              result.paymentType?.name,
              result.comments,
            ]
          case 'Rendiciones':
            return [
              result.id,
              result.disbursement?.id,
              result.institutionId,
              result.disbursement?.institutionName,
              result.reportDate,
              result.reportedAmount,
              result.deliveredVia,
              result.comments,
            ]
          case 'Comprobantes':
            return [
              result.id,
              result.institution.id,
              result.institution.name,
              result.disbursementId,
              result.reportId,
              result.receiptType?.name,
              result.receiptNumber,
              result.provider?.ruc,
              result.provider?.name,
              result.receiptDate,
              result.receiptTotal,
            ]
          case 'Detalles de comprobante':
            return [
              result.id,
              result.receiptId,
              `${result.objectOfExpenditure?.key}: ${result.objectOfExpenditure?.value}`,
              result['quantity'],
              result.description,
              result.unitPrice,
            ]
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
        case 'Detalles de comprobante':
          return base + 'receipt-items'
      }
    }
  };
}