<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';

  export let data: any;
  export let title: string = '';
  export let type: 'line' | 'bar' | 'doughnut' | 'pie' | 'radar' = 'line';

  let canvas: HTMLCanvasElement;
  let chart: Chart | null = null;

  Chart.register(...registerables);

  onMount(() => {
    if (canvas && data) {
      createChart();
    }
  });

  onDestroy(() => {
    if (chart) {
      chart.destroy();
      chart = null;
    }
  });

  function createChart() {
    if (chart) {
      chart.destroy();
      chart = null;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx || !data) return;

    try {
      chart = new Chart(ctx, {
        type: type,
        data: data,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: !!title,
              text: title,
              font: {
                size: 16,
                weight: 'bold'
              },
              color: '#374151'
            },
            legend: {
              position: 'top',
              labels: {
                usePointStyle: true,
                padding: 15,
                font: {
                  size: 12
                }
              }
            }
          },
          scales: type === 'doughnut' || type === 'pie' ? {} : {
            y: {
              beginAtZero: true,
              grid: {
                color: '#f3f4f6'
              },
              ticks: {
                font: {
                  size: 11
                },
                color: '#6b7280'
              }
            },
            x: {
              grid: {
                color: '#f3f4f6'
              },
              ticks: {
                font: {
                  size: 11
                },
                color: '#6b7280'
              }
            }
          }
        }
      });
    } catch (error) {
      console.error('Error creating chart:', error);
    }
  }

  // Reactive statement to update chart when data changes
  $: if (chart && data) {
    chart.data = data;
    chart.update();
  }

  // Reactive statement to recreate chart when type changes
  $: if (canvas && data && type) {
    createChart();
  }
</script>

<div class="w-full h-full bg-white overflow-hidden">
  <canvas bind:this={canvas} class="w-full h-full"></canvas>
</div>
