let barChartTemplate = {
    xAxis: {
        type: 'category', data: [],
        axisLine: { lineStyle: { color: '#BFC9C5' } },
        axisLabel: { color: '#3F4946', fontSize: 12, fontFamily: 'Inter, Noto Sans SC, sans-serif' },
        axisTick: { show: false }
    },
    yAxis: {
        type: 'value', axisLine: { show: false },
        axisLabel: { color: '#6F7976', fontSize: 12, fontFamily: 'Inter, Noto Sans SC, sans-serif' },
        splitLine: { lineStyle: { color: '#E3EAE7', type: 'dashed' } }
    },
    grid: { left: 60, right: 40, top: 40, bottom: 40 },
    tooltip: {
        trigger: 'axis',
        backgroundColor: '#171D1B', borderColor: '#171D1B',
        textStyle: { color: '#fff', fontSize: 13, fontFamily: 'Inter, Noto Sans SC, sans-serif' }
    },
    series: [{
        data: [], type: 'bar', barWidth: '50%',
        itemStyle: {
            color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [{ offset: 0, color: '#00897B' }, { offset: 1, color: '#006B5E' }]
            },
            borderRadius: [4, 4, 0, 0]
        }
    }]
};
export default barChartTemplate;
