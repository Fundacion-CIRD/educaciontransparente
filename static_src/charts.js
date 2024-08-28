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
            data: [
                {
                    name: 'Servicios no personales',
                    value: 8800000 + 8700000 + 1450000,
                    children: [
                        {name: 'Catering', value: 880000},
                        {name: 'Publicidad', value: 870000},
                        {name: 'Otros', value: 1450000}
                    ]
                },
                {
                    name: 'Bienes de consumo',
                    value: 15000000 + 4350000 + 2500000,
                    children: [
                        {name: 'Merienda escolar', value: 15000000},
                        {name: 'Utiles escolares', value: 4350000},
                        {name: 'Juguetes', value: 2500000}
                    ]
                },
                {
                    name: 'Inversion fisica',
                    value: 8900000 + 2300000 + 7000000,
                    children: [
                        {name: 'Material de construccion', value: 8900000},
                        {name: 'Pintura', value: 2300000},
                        {name: 'Elementos de carpinteria', value: 7000000}
                    ]
                }
            ]
        }]
    };

    treemapChart.setOption(treemapOption);
});