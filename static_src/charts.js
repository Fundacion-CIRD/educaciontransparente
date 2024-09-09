const MILLION = 1000000;

function transformDataForECharts(yearlyReport) {
  const years = [];
  const totalDisbursed = [];
  const totalReported = [];

  for (const [year, data] of Object.entries(yearlyReport)) {
    years.push(year);
    totalDisbursed.push(data.total_disbursed ? parseFloat(data.total_disbursed) / MILLION : 0);
    totalReported.push(data.total_reported ? parseFloat(data.total_reported) / MILLION : 0);
  }

  return {
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
        }
      }
    ]
  };
}

function formatNumber(number) {
  return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
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

document.addEventListener('DOMContentLoaded', () => {
  // Bar Chart
  let barChart = echarts.init(document.getElementById('bar-chart'));
  let barOption = {
    title: {
      text: 'Recibido vs Rendido por Año'
    },
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
    ...transformDataForECharts(yearlyReport)
  };
  barChart.setOption(barOption);

  // Icicle Chart
  let treemapChart = echarts.init(document.getElementById('icicle-chart'));
  const institutionId = document.location.pathname.split('/')[2]
  fetch(`/api/account-objects/?institution=${institutionId}`).then(
    res => res.json())
    .then(data => {
      const treeData = data.results.map(mapToTreemapData);
      let treemapOption = {
        tooltip: {
          formatter: '{b}: Gs. {c}'
        },
        legend: {
          orient: 'horizontal',
          left: 'center',
          top: 'bottom',
          data: ['Servicios no personales', 'Bienes de consumo', 'Inversion fisica']
        },
        series: [{
          type: 'treemap',
          label: {
            show: true,
            formatter: '{b}\nGs. {c}',
            fontSize: 14,
            position: 'insideTopLeft',
          },
          levels: [
            {
              itemStyle: {
                borderColor: '#777',
                borderWidth: 2,
                gapWidth: 2
              }
            },
            {
              itemStyle: {
                borderColor: '#555',
                borderWidth: 1,
                gapWidth: 1
              }
            },
            {
              itemStyle: {
                borderColor: '#333',
                borderWidth: 1,
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

      treemapChart.setOption(treemapOption);
    });
});