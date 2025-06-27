<script lang="ts">
  import { onMount } from "svelte";
  import "../app.css"; // Ensure styles are applied
  import Chart from "./Chart.svelte";

  // Import chart data
  import salesData from "../data/sales-data.json";
  import quarterlyRevenue from "../data/quarterly-revenue.json";
  import productCategories from "../data/product-categories.json";

  interface Message {
    id: number;
    type: "user" | "assistant";
    content: string;
    chartData?: any;
  }

  interface SlashCommand {
    command: string;
    description: string;
    chartData: any;
  }

  let messages: Message[] = [];
  let inputText: string = "";
  let isLoading: boolean = false;
  let chatContainer: HTMLDivElement;
  let showSlashCommands: boolean = false;
  let textareaElement: HTMLTextAreaElement;

  // Sample initial message
  onMount(() => {
    messages = [
      {
        id: 1,
        type: "assistant" as const,
        content:
          "Hello! I'm your Data Lens AI Assistant. Ask me anything about data analysis, file conversion, or insights from your data.\n\n📊 Quick Charts: Type /sales, /revenue, or /categories to view data visualizations instantly!",
      },
    ];

    // Add global keydown listener for auto-focus
    const handleGlobalKeydown = (event: KeyboardEvent) => {
      // Don't interfere with special keys or when already focused on input
      if (event.ctrlKey || event.metaKey || event.altKey || 
          document.activeElement?.tagName === 'INPUT' ||
          document.activeElement?.tagName === 'TEXTAREA') {
        return;
      }

      // Focus on textarea when typing regular characters
      if (event.key.length === 1 && !isLoading) {
        const textarea = document.querySelector('.chat-textarea') as HTMLTextAreaElement;
        if (textarea) {
          textarea.focus();
        }
      }
    };

    document.addEventListener('keydown', handleGlobalKeydown);

    // Auto-focus the textarea when component mounts
    setTimeout(() => {
      if (textareaElement) {
        textareaElement.focus();
      }
    }, 100);

    // Cleanup function
    return () => {
      document.removeEventListener('keydown', handleGlobalKeydown);
    };
  });

  async function sendMessage() {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now(),
      type: "user",
      content: inputText.trim(),
    };

    messages = [...messages, userMessage];
    const currentInput = inputText;
    inputText = "";
    showSlashCommands = false;
    isLoading = true;

    // Scroll to bottom
    scrollToBottom();

    // Check if it's a slash command
    const slashCommand = slashCommands.find(cmd => 
      currentInput.toLowerCase() === cmd.command.toLowerCase()
    );

    if (slashCommand) {
      // Handle slash command - show chart
      setTimeout(() => {
        const assistantMessage: Message = {
          id: Date.now() + 1,
          type: "assistant",
          content: `Here's your ${slashCommand.description.toLowerCase()}:`,
          
          chartData: slashCommand.chartData
        };
        
        messages = [...messages, assistantMessage];
        isLoading = false;
        scrollToBottom();
      }, 500);
    } else {
      // Regular message - simulate API call
      setTimeout(() => {
        const assistantMessage: Message = {
          id: Date.now() + 1,
          type: "assistant",
          content: `I understand you're asking about: "${currentInput}". This is a simulated response. In a real implementation, this would connect to your data analysis backend to provide insights, help with file conversions, or analyze your data.`,

        };

        messages = [...messages, assistantMessage];
        isLoading = false;
        scrollToBottom();
      }, 1500);
    }
  }

  function selectSlashCommand(command: SlashCommand) {
    inputText = command.command;
    showSlashCommands = false;
    sendMessage();
  }

  function scrollToBottom() {
    setTimeout(() => {
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    }, 100);
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  function formatTime(timestamp: Date): string {
    return timestamp.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  // Available slash commands
  const slashCommands: SlashCommand[] = [
    {
      command: "/sales",
      description: "Show monthly sales performance chart",
      chartData: salesData,
    },
    {
      command: "/revenue",
      description: "Show quarterly revenue comparison",
      chartData: quarterlyRevenue,
    },
    {
      command: "/categories",
      description: "Show product categories distribution",
      chartData: productCategories,
    },
  ];

  // Filter slash commands based on input
  $: filteredSlashCommands = inputText.startsWith("/")
    ? slashCommands.filter((cmd) =>
        cmd.command
          .toLowerCase()
          .includes(inputText.toLowerCase().substring(1))
      )
    : [];

  // Show slash commands dropdown
  $: showSlashCommands =
    inputText.startsWith("/") && filteredSlashCommands.length > 0;
</script>

<!-- Chat Interface -->
<div
  class="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl border-2 border-gray-200 flex flex-col h-full"
>
  <!-- Chat Header -->
  <div
    class="flex items-center gap-3 p-6 border-b border-gray-200 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-t-3xl flex-shrink-0"
  >
    <div
      class="w-10 h-10 bg-white rounded-full flex items-center justify-center text-2xl"
    >
      🤖
    </div>
    <div class="flex-1">
      <h3 class="font-bold text-white text-lg">Data Lens AI</h3>
      <p class="text-indigo-100 text-sm">Your data analysis assistant</p>
    </div>
  </div>

  <!-- Chat Messages -->
  <div
    bind:this={chatContainer}
    data-chat-scroll
    class="flex-1 overflow-y-auto p-1 space-y-4 bg-gray-50/50 min-h-0"
  >
    {#each messages as message (message.id)}
      <div
        class="flex {message.type === 'user' ? 'justify-end' : 'justify-start'}"
      >
        <div class="max-w-[85%]">
          {#if message.type === "assistant"}
            <div class="flex items-start gap-3">
              <div
                class="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-bold shrink-0"
              >
                AI
              </div>
              <div
                class="bg-white rounded-2xl rounded-tl-sm p-4 shadow-sm border border-gray-100 max-w-full"
              >
                <p class="text-gray-800 leading-relaxed">{message.content}</p>
                {#if message.chartData}
                  <div class="mt-4 h-64 w-full">
                    <Chart 
                      data={message.chartData.data} 
                      title={message.chartData.title}
                      type={message.chartData.type}
                    />
                  </div>
                {/if}

              </div>
            </div>
          {:else}
            <div
              class="bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-2xl rounded-tr-sm p-4 shadow-sm"
            >
              <p class="leading-relaxed">{message.content}</p>
            </div>
          {/if}
        </div>
      </div>
    {/each}

    {#if isLoading}
      <div class="flex justify-start">
        <div class="flex items-start gap-3">
          <div
            class="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-bold shrink-0"
          >
            AI
          </div>
          <div
            class="bg-white rounded-2xl rounded-tl-sm p-4 shadow-sm border border-gray-100"
          >
            <div class="flex items-center gap-2">
              <div
                class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"
              ></div>
              <div
                class="w-2 h-2 bg-purple-400 rounded-full animate-bounce animate-delay-100"
              ></div>
              <div
                class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce animate-delay-200"
              ></div>
              <span class="text-gray-500 text-sm ml-2">Thinking...</span>
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- Chat Input -->
  <div
    class="p-4 border-t border-gray-200 bg-white/80 backdrop-blur-sm flex-shrink-0 rounded-b-3xl relative"
  >
    <!-- Slash Commands Dropdown -->
    {#if showSlashCommands}
      <div class="absolute bottom-full left-4 right-4 mb-2 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
        <div class="p-2">
          <div class="text-xs text-gray-500 mb-2 px-2">Available Commands:</div>
          {#each filteredSlashCommands as command}
            <button
              class="w-full text-left px-3 py-2 rounded-md hover:bg-gray-100 transition-colors duration-150 flex items-center gap-3"
              on:click={() => selectSlashCommand(command)}
            >
              <span class="font-mono text-indigo-600 text-sm">{command.command}</span>
              <span class="text-gray-600 text-sm">{command.description}</span>
            </button>
          {/each}
        </div>
      </div>
    {/if}
    
    <div class="flex gap-3">
      <textarea
        bind:this={textareaElement}
        bind:value={inputText}
        on:keypress={handleKeyPress}
        placeholder="Ask about data analysis, file conversion, or insights..."
        class="chat-textarea flex-1 p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none transition-all duration-200 bg-gray-50/50"
        rows="1"
        disabled={isLoading}
      ></textarea>
      <button
        on:click={sendMessage}
        disabled={!inputText.trim() || isLoading}
        class="bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 shadow-lg hover:shadow-xl"
      >
        {#if isLoading}
          <div
            class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
          ></div>
        {:else}
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            ></path>
          </svg>
        {/if}
      </button>
    </div>

    <!-- Help Text -->
    <div class="flex justify-between items-center mt-3 text-xs text-gray-500">
      <span class="flex items-center gap-4">
        <span>💡</span>
        <span>Press Enter to send, Shift+Enter for new line • Type / for charts</span>
      </span>
      <span class="text-gray-400">{inputText.length}/500</span>
    </div>
  </div>
</div>

<style lang="postcss">
  @reference "tailwindcss";
</style>
