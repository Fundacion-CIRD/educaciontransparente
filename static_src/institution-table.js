const sortMap = {
  'Año': 'year',
  'Director': 'principal_name',
  'Doc. Director': 'principal_issued_id',
  'Monto Resol.': 'amount_disbursed',
  'Resolución': 'resolution',
  'Fecha Desembolso': 'disbursement_date',
  'Monto Desembolsado': 'amount_disbursed',
  'Fecha a rendir': 'due_date',
  'Monto rendido': 'total_reported',
}

function institutionDetails() {
  return {
    year: null,
    headers: [
      'Año',
      'Director',
      'Doc. Director',
      'Resolución',
      'Monto Resol.',
      'Fecha Desembolso',
      'Monto Desembolsado',
      'Fecha a rendir',
      'Monto rendido',
      'Detalle de rendición',
    ],
    results: [],
    sortCol: 'Año',
    sortDesc: false,
    summary: {
      totalReported: 0,
      totalDisbursed: 0,
    },
    async fetchResults() {
      const institutionId = window.location.pathname.split('/')[2]
      const params = new URLSearchParams();
      params.append('institution', institutionId)
      params.append('ordering', `${!this.sortDesc ? '-' : ''}${sortMap[this.sortCol]}`)
      if (this.year) params.append('year', this.year.toString());
      const response = await fetch(`/api/reports/?${params}`);
      const data = await response.json();
      this.results = data.results;
      this.summary = data.summary;
    },
    setYear(event) {
      this.year = event.target.value || null;
      void this.fetchResults();
    },
    formatDate(dateStr) {
      const [year, month, day] = dateStr.split('-');
      return `${day}/${month}/${year}`;
    },
    formatNumber(number) {
      try {
        return Intl.NumberFormat('es-ES').format(number)
      } catch (e) {
        return number;
      }
    },
    tagColor(inputDate) {
      const today = new Date();
      const targetDate = new Date(inputDate);

      // Calculate the difference in time (in milliseconds)
      const timeDiff = targetDate - today;

      // Calculate the difference in days
      const dayDiff = timeDiff / (1000 * 60 * 60 * 24);

      if (dayDiff < 0) {
        return 'is-danger'; // Date is lower than today
      } else if (dayDiff <= 10) {
        return 'is-warning'; // Date is at most 10 days into the future
      } else {
        return ''; // Otherwise, return an empty string
      }
    }
  }
}