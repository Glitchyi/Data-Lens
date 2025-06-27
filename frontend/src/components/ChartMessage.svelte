<script lang="ts">
  import Chart from './Chart.svelte';

  export let chartData: any;
  export let title: string = '';
  export let type: 'line' | 'bar' | 'doughnut' | 'pie' | 'radar' = 'line';
</script>

<div class="w-full bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
  <!-- Chart Header -->
  <div class="px-4 py-3 bg-gray-50 border-b border-gray-200">
    <h3 class="text-sm font-semibold text-gray-800 flex items-center gap-2">
      <span class="text-lg">📊</span>
      {title || 'Chart Visualization'}
    </h3>
  </div>
  
  <!-- Chart Container -->
  <div class="p-4">
    <div class="h-80 w-full relative">
      {#if chartData}
        <Chart data={chartData} title={''} {type} />
      {:else}
        <div class="flex items-center justify-center h-full text-gray-500">
          <p>No chart data available</p>
        </div>
      {/if}
    </div>
  </div>
</div>
