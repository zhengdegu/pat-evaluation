let barChartTemplate = {
    xAxis: {
        type: 'category',
        data: [],
        axisLine: { lineStyle: { color: '#e4e8ee' } },
        axisLabel: { color: '#5a6577', fontSize: 12, fontFamily: 'Inter, Noto Sans SC, sans-serif' },
        axisTick: { show: false }
    },
    yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisLabel: { color: '#8c95a4', fontSize: 12, fontFamily: 'Inter, Noto Sans SC, sans-serif' },
        splitLine: { lineStyle: { color: '#edf0f5', type: 'dashed' } }
    },
    grid: { left: 60, right: 40, top: 40, bottom: 40 },
    tooltip: {
        trigger: 'axis',
        backgroundColor: '#1a2332',
        borderColor: '#1a2332',
        textStyle: { color: '#ffffff', fontSize: 13, fontFamily: 'Inter, Noto Sans SC, sans-serif' }
    },
    series: [{
        data: [],
        type: 'bar',
        barWidth: '50%',
        itemStyle: {
            color: {
                type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                    { offset: 0, color: '#2c5f8a' },
                    { offset: 1, color: '#1a3a5c' }
                ]
            },
            borderRadius: [3, 3, 0, 0]
        }
    }]
};

export default barChartTemplate;
