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

function barChartFormatter(params, newline = false) {
  if (newline) {
    return `${params.name}\nGs. ${params.value.toLocaleString()}`;
  }
  return `${params.name}: Gs. ${params.value.toLocaleString()}`;
}

function formatNumber(number) {
  try {
    return Intl.NumberFormat('es-ES').format(number)
  } catch (e) {
    return number;
  }
}

function mapToTreemapData(node) {
  // Base case: If it's a leaf node, return its value and name
  if (!node.children) {
    return {
      name: node.value,
      value: node.totalExpenditure || 0
    };
  }

  // Recursive case: Map its children
  return {
    name: node.value,
    children: node.children.map(mapToTreemapData)
  };
}

function parseTreemapOption(treeData) {
  return {
    tooltip: {
      formatter: function (params) {
        return barChartFormatter(params);
      },
    },
    breadcrumb: {
      show: false  // Disable the breadcrumb
    },
    series: [{
      type: 'treemap',
      label: {
        show: true,
        formatter: function (params) {
          return barChartFormatter(params, true);
        },
        fontSize: 14,
        position: 'insideTopLeft',
      },
      levels: [
        {
          itemStyle: {
            borderColor: '#777',
            borderWidth: 0,
            gapWidth: 2
          }
        },
        {
          itemStyle: {
            borderColor: '#555',
            borderWidth: 0,
            gapWidth: 1
          }
        },
        {
          itemStyle: {
            borderColor: '#333',
            borderWidth: 0,
            gapWidth: 1
          }
        }
      ],
      upperLabel: {
        show: true,
        height: 30,
        color: '#fff',
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        fontSize: 16,
        formatter: '{b}',
      },
      itemStyle: {
        borderColor: '#fff'
      },
      data: treeData
    }]
  };
}

function initBarChart() {
  const barChart = echarts.init(document.getElementById('bar-chart'));
  const [years, chartData] = getYearlyReportChartData(yearlyReport);
  const barOption = {
    // title: {
    //   text: 'Recibido vs Rendido por Año'
    // },
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

async function generateTreemapOption(institutionId, year) {
  const params = new URLSearchParams();
  params.append('institution', institutionId);
  if (year) params.append('year', year);
  const response = await fetch(`/api/account-objects/?${params.toString()}`);
  const data = await response.json();
  const treeData = data.results.map(mapToTreemapData);
  return parseTreemapOption(treeData);
}

async function fetchResults(institutionId, year) {
  const params = new URLSearchParams();
  params.append('institution', institutionId)
  if (year) params.append('year', year.toString());
  const response = await fetch(`/api/reports/?${params.toString()}`);
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
    treemapChart: null,
    treemapChartData: null,
    async init() {
      this.institutionId = document.location.pathname.split('/')[2];
      const [barChart, years] = initBarChart();
      this.barChart = barChart;
      this.years = years;
      this.treemapChart = echarts.init(document.getElementById('icicle-chart'));
      const treemapOption = await generateTreemapOption(this.institutionId, this.year);
      this.treemapChart.setOption(treemapOption);
      const data = await fetchResults(this.institutionId, this.year);
      this.results = data.results;
      this.summary = data.summary;
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
    async setYear(event) {
      this.year = event.target.value || null;
      const data = await fetchResults(this.institutionId, this.year);
      this.results = data.results;
      this.summary = data.summary;
      const treemapOption = await generateTreemapOption(this.institutionId, this.year);
      this.treemapChart.setOption(treemapOption);
      this.highlightChart();
    },
    formatDate(dateStr) {
      const [year, month, day] = dateStr.split('-');
      return `${day}/${month}/${year}`;
    },
    formatNumber,
    tagColor(inputDate) {
      const today = new Date();
      const targetDate = new Date(inputDate);

      // Calculate the difference in time (in milliseconds)
      const timeDiff = targetDate - today;

      // Calculate the difference in days
      const dayDiff = timeDiff / (1000 * 60 * 60 * 24);

      if (dayDiff < 0) {
        return 'tag is-danger'; // Date is lower than today
      } else if (dayDiff <= 10) {
        return 'tag is-warning'; // Date is at most 10 days into the future
      } else {
        return ''; // Otherwise, return an empty string
      }
    }
  }
}