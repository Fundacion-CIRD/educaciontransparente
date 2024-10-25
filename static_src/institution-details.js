const SORT_MAP = {
  'Año': 'year',
  'Director': 'principal_name',
  'Doc. Director': 'principal_issued_id',
  'Monto Resol.': 'amount_disbursed',
  'Resolución': 'resolution',
  'Fecha Desembolso': 'disbursement_date',
  'Monto Desembolsado': 'amount_disbursed',
  'Fecha a rendir': 'due_date',
}

const MILLION = 1000000;

var treemapChart = null;

function getYearlyReportChartData(yearlyReport) {
  const years = [];
  const totalDisbursed = [];
  const totalReported = [];
  for (const [year, data] of Object.entries(yearlyReport)) {
    years.push(year);
    totalDisbursed.push(data.total_disbursed ? (parseFloat(data.total_disbursed) / MILLION).toFixed(2) : 0);
    totalReported.push(data.total_reported ? (parseFloat(data.total_reported) / MILLION).toFixed(2) : 0);
  }

  return [years, {
    yAxis: {
      type: 'category',
      data: years,
    },
    series: [
      {
        name: 'Recibido',
        type: 'bar',
        data: totalDisbursed,
        itemStyle: {
          color: '#C8E4FF'
        }
      },
      {
        name: 'Rendido',
        type: 'bar',
        data: totalReported,
        itemStyle: {
          color: '#81C1FF'
        },
      }
    ],
    graphic: {
      type: 'text',
      left: 'center',
      bottom: 0,  // Adjust position relative to the bottom
      style: {
        text: 'En millones de Gs.',  // Footer text
        fontSize: 12,
        fill: '#333'  // Text color
      }
    }
  }];
}

function barchartFormatter(element, newline = true) {
  return `${element.name}${
    newline ? '\n' : ': '
  }Gs. ${element.value.toLocaleString()}`;
}

function parseChartElement(element) {
  if (!element.children) {
    return {
      name: `${element.key}: ${element.value}`,
      value: element.totalExpenditure,
    };
  }
  return {
    name: `${element.key}: ${element.value}`,
    children: element.children.map(parseChartElement),
  };
}

function parseChartData(response) {
  return response.results.map(parseChartElement);
}

function formatNumber(number) {
  try {
    return Intl.NumberFormat('es-ES').format(number)
  } catch (e) {
    return number;
  }
}

function parseTreemapOption(treeData) {
  const data = parseChartData(treeData);
  return {
    tooltip: {
      formatter: barchartFormatter,
    },
    series: [
      {
        type: 'treemap',
        label: {
          show: true,
          fontSize: 14,
          position: 'insideTopLeft',
          formatter: (params) => barchartFormatter(params, true),
        },
        leafDepth: 1,
        data,
      },
    ],
  };
}

function initBarChart() {
  const barChart = echarts.init(document.getElementById('bar-chart'));
  const [years, chartData] = getYearlyReportChartData(yearlyReport);
  const barOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['Recibido', 'Rendido']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01],
      axisLabel: {
        formatter: function (value) {
          return parseInt(value);  // Ensure the x-axis shows integers
        }
      }
    },
    ...chartData,
  }
  barChart.setOption(barOption);
  return [barChart, years];
}

async function initTreemapChart(institutionId, year) {
  if (!treemapChart)
    treemapChart = echarts.init(document.getElementById('treemap-chart'));
  const treemapOption = await generateTreemapOption(institutionId, year);
  treemapChart.setOption(treemapOption);
}

function setComments(results) {
  const commentsDiv = document.getElementById('accountObjectComments')
  commentsDiv.innerHTML = '';
  for (const result of results) {
    if (result.comments) {
      const p = document.createElement('p');
      p.className = 'help';
      p.textContent = `${result.key}: ${result.comments}`;
      commentsDiv.appendChild(p);
    }
  }
}

async function generateTreemapOption(institutionId, year) {
  const params = new URLSearchParams();
  params.append('institution', institutionId);
  if (year) params.append('year', year);
  const response = await fetch(`/api/account-objects/?${params.toString()}`);
  const data = await response.json();
  setComments(data.results);
  return parseTreemapOption(data);
}

async function fetchResults(institutionId, year) {
  const params = new URLSearchParams();
  params.append('institution', institutionId)
  if (year) params.append('year', year.toString());
  const response = await fetch(`/api/disbursements/?${params.toString()}`);
  return await response.json();
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
      'Detalle de rendición',
    ],
    results: [],
    sortCol: 'Año',
    sortDesc: false,
    summary: {
      totalReported: 0,
      totalDisbursed: 0,
    },
    institutionId: null,
    barChart: null,
    years: [],
    async init() {
      this.institutionId = document.location.pathname.split('/')[2];
      const [barChart, years] = initBarChart();
      this.barChart = barChart;
      this.years = years;
      await initTreemapChart(this.institutionId, this.year);
      const params = new URLSearchParams(window.location.search);
      const yearParam = params.get('year');
      if (yearParam) void this.setYear(null, yearParam);
      else {
        const data = await fetchResults(this.institutionId, this.year);
        this.results = data.results;
        this.summary = data.summary;
      }
    },
    highlightChart() {
      const dataIndex = this.years.indexOf(this.year);
      this.barChart.dispatchAction({type: 'hideTip', seriesIndex: 0});
      this.barChart.dispatchAction({type: 'hideTip', seriesIndex: 1});
      if (dataIndex >= 0) {
        this.barChart.dispatchAction({
          type: 'showTip',
          seriesIndex: 0,
          dataIndex: dataIndex
        });
        this.barChart.dispatchAction({
          type: 'showTip',
          seriesIndex: 1,
          dataIndex: dataIndex
        });
      }
    },
    async setYear(event, year = null) {
      if (event) this.year = event.target.value || null;
      else this.year = year;
      const data = await fetchResults(this.institutionId, this.year);
      this.results = data.results;
      this.summary = data.summary;
      const treemapOption = await generateTreemapOption(this.institutionId, this.year);
      treemapChart.setOption(treemapOption);
      this.highlightChart();
      const url = new URL(window.location);
      url.searchParams.set('year', this.year);
      window.history.pushState({}, '', url);
    },
    formatDate(dateStr) {
      if (!dateStr) {
        return '';
      }
      const [year, month, day] = dateStr.split('-');
      return `${day}/${month}/${year}`;
    },
    formatNumber,
    tagColor(disbursement) {
      const {dueDate} = disbursement;

      if (disbursement.isHistorical) {
        return '';
      }

      if (!disbursement.report) {
        const today = new Date();
        const targetDate = new Date(dueDate);

        // Calculate the difference in time (in milliseconds)
        const timeDiff = targetDate - today;

        // Calculate the difference in days
        const dayDiff = timeDiff / (1000 * 60 * 60 * 24);

        if (dayDiff < 0) {
          return 'is-danger'; // Date is lower than today
        } else if (dayDiff <= 10) {
          return 'is-warning'; // Date is at most 10 days into the future
        }
        return ''; // Otherwise, return an empty string
      }

      const {balance, reportDate} = disbursement.report;
      console.log(disbursement);
      if (balance < 0 && reportDate <= dueDate) {
        return '';
      }
      if (reportDate && reportDate > dueDate) {
        return 'is-danger';
      }
      if (balance && balance > 0) {
        return 'is-danger';
      }
    }
  }
}