<script lang="ts">
  import ChatInterface from "./components/ChatInterface.svelte";
  import CssTest from "./components/CssTest.svelte";
</script>

<main
  class="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-purple-700 p-5"
>
  <div
    class="max-w-4xl mx-auto bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl h-[90vh] flex flex-col"
  >
    <!-- Chat Interface -->
    <ChatInterface />

  </div>
</main>
