<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
interface Visualization { type: 'line' | 'bar'; title: string; labels: string[]; datasets: Array<{ label: string; data: Array<number | null> }> }
const props = defineProps<{ visualization: Visualization }>()
const chartElement = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | undefined
function render() { if (!chartElement.value) return; chart ??= echarts.init(chartElement.value); chart.setOption({ title: { text: props.visualization.title, left: 0, textStyle: { fontSize: 15, color: '#001f4d' } }, tooltip: { trigger: 'axis' }, legend: { top: 26 }, grid: { left: 55, right: 24, bottom: 45, top: 70 }, xAxis: { type: 'category', data: props.visualization.labels }, yAxis: { type: 'value' }, series: props.visualization.datasets.map(dataset => ({ name: dataset.label, type: props.visualization.type, data: dataset.data, smooth: props.visualization.type === 'line', itemStyle: { color: dataset.label.toLowerCase().includes('margen') ? '#ef1235' : '#003b82' } })) }) }
function resize() { chart?.resize() }
onMounted(() => { render(); window.addEventListener('resize', resize) })
watch(() => props.visualization, render, { deep: true })
onBeforeUnmount(() => { window.removeEventListener('resize', resize); chart?.dispose() })
</script>
<template><div ref="chartElement" class="chart-container" /></template>
<style scoped>
.chart-container { width: min(100%, 760px); height: 330px; margin-top: 18px; background: white; border: 1px solid #dbe5f1; border-radius: 12px; padding: 10px; }
</style>
