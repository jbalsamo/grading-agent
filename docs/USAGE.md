# Azure OpenAI Master Agent System - Usage Guide

## Quick Start

### Running the Application

```bash
# Navigate to the project directory
cd /Users/josephbalsamo/Development/Work/gradingAgent/grading-agent

# Activate the virtual environment
source .venv/bin/activate

# Run in quiet mode (default - only shows warnings and errors)
python main.py

# Run in verbose mode (shows INFO logs including HTTP requests and agent routing)
python main.py -v
# or
python main.py --verbose
```

### Command-Line Options

#### Verbose Mode (`-v` or `--verbose`)

Enable detailed logging to see what's happening under the hood:

```bash
python main.py --verbose
```

**What you'll see in verbose mode:**
- Master Agent initialization details
- Task classification decisions
- Agent routing information
- HTTP request/response logs to Azure OpenAI
- Data manager operations
- Conversation history updates
- Performance monitoring data

**Quiet mode (default):**
- Only shows warnings and errors
- Cleaner output for normal usage
- Better for production or demos

### Getting Help

```bash
# Show command-line help
python main.py --help

# Show in-chat commands
python main.py
# Then type: help
```

## Interactive Commands

Once the application is running, you can use these commands:

| Command | Description |
|---------|-------------|
| `status` | Show system status and agent availability |
| `stats` | Show performance statistics (uptime, requests, response times) |
| `health` | Run comprehensive health check on all components |
| `history` | Show conversation history statistics and recent messages |
| `clear-history` | Clear the conversation history (resets context and deletes saved file) |
| `save` | Manually save conversation history to disk |
| `help` | Show available commands |
| `quit` / `exit` / `bye` | Exit the application (auto-saves conversation) |

## Conversation History Features

The application maintains a **rolling window of the last 20 messages** (10 exchanges) across all agents with **automatic persistence** between sessions.

### Key Features:

1. **Persistent Across Sessions** ✨ *NEW*
   - Conversation history automatically saves when you exit
   - Automatically loads when you start the app
   - Continue conversations where you left off
   - Stored in `data/conversation_history.json`

2. **Shared Context Across Agents**
   - Chat agent → Analysis agent → Grading agent all share the same conversation history
   - Agents can reference previous messages and maintain continuity

3. **Automatic Management**
   - History is automatically tracked with each interaction
   - Rolling window prevents memory bloat
   - Configurable limit (default: 20 messages)
   - Auto-save on exit (normal or Ctrl+C)

4. **Agent Attribution**
   - Each response is tagged with the agent that generated it
   - Helps understand which specialized agent handled each request

### Example Conversation Flow:

```
Session 1 (Monday):
You: Hi, my name is Alice
Chat Agent: Nice to meet you, Alice!

You: I need help with data analysis
Analysis Agent: [accesses previous messages] Hi Alice, I can help with that!

You: quit
💾 Saving conversation history...
✅ Saved 4 messages for next session

Session 2 (Tuesday):
💾 Restored previous conversation with 4 messages

You: Do you remember my name?
Chat Agent: [remembers from previous session] Yes, your name is Alice!

You: Grade my analysis approach from yesterday
Grading Agent: [references earlier session] Based on what you discussed...
```

### Persistence Behavior:

**Automatic Save Triggers:**
- Typing `quit`, `exit`, or `bye`
- Pressing Ctrl+C to interrupt
- Normal application termination

**Automatic Load:**
- Happens on every startup
- Silent if no previous history exists
- Shows "Restored X messages" if history found

**Manual Control:**
- `save` - Save current conversation anytime
- `clear-history` - Clear memory AND delete saved file
- Saved file: `data/conversation_history.json`

## Agent Types

The system automatically routes your requests to specialized agents:

### Chat Agent
- General conversation
- Question answering
- Explanations and clarifications
- Creative writing assistance

### Analysis Agent
- Data analysis and interpretation
- Statistical analysis
- Code generation for data processing
- Mathematical computations
- Research methodology

### Grading Agent
- Assignment and essay grading
- Detailed feedback generation
- Rubric creation and application
- Learning outcome analysis
- Educational assessment design

## Examples

### Basic Chat Session

```bash
$ python main.py

👤 You: Hello! Can you help me with Python?
🤖 Master Assistant: Of course! I'd be happy to help you with Python...

👤 You: What's the difference between a list and a tuple?
🤖 Master Assistant: Great question! Here are the key differences...

👤 You: history
💬 Conversation History:
   Total Messages: 4
   User Messages: 2
   Assistant Messages: 2
   Agent Usage:
     - chat: 2 responses
```

### With Verbose Logging

```bash
$ python main.py -v

📝 Verbose logging enabled (INFO level)
🚀 Starting Azure OpenAI Master Agent System...
============================================================
📡 Initializing Master Agent System...
2025-09-30 16:10:23,498 - master_agent - INFO - Master Agent initialized...
2025-09-30 16:10:23,499 - conversation_history - INFO - ConversationHistory initialized...
...

👤 You: Hello
2025-09-30 16:10:24,732 - httpx - INFO - HTTP Request: POST https://...
2025-09-30 16:10:24,733 - master_agent - INFO - Task classified as: chat
...
```

### Switching Between Agents

```bash
👤 You: I'm working on a math problem
🤖 Chat Agent: I'd be happy to help! What's the problem?

👤 You: Can you analyze 15 + 27 step by step?
🤖 Analysis Agent: [references previous conversation] Let me break down...

👤 You: Grade my understanding of this problem
🤖 Grading Agent: [maintains context] Based on our discussion, I'd rate...
```

## Troubleshooting

### "ModuleNotFoundError: No module named..."

Make sure you've activated the virtual environment:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### "AZURE_OPENAI_ENDPOINT is required in .env file"

Create or update your `.env` file with the required configuration:
```bash
cp .env.template .env
# Edit .env with your Azure OpenAI credentials
```

### Too many INFO logs

Run without the `-v` flag for cleaner output:
```bash
python main.py  # Instead of: python main.py -v
```

### Want to see what's happening

Run with the `-v` flag to enable verbose logging:
```bash
python main.py -v
```

## Testing

Run the test suites to verify functionality:

```bash
# Test conversation history functionality
python test_chat_history.py

# Test main application functionality
python test_main_app.py

# Test verbose mode
python test_verbose_mode.py
```

## Configuration

Edit `.env` file to configure:
- Azure OpenAI endpoint
- API key
- API version
- Model deployment names

See `.env.template` for all available options.

## Tips

1. **Use verbose mode for debugging**: `python main.py -v`
2. **Check history regularly**: Type `history` to see conversation stats
3. **Clear history when changing topics**: Type `clear-history`
4. **Use status for health checks**: Type `status` to verify all agents are active
5. **Review stats for performance**: Type `stats` to see response times and usage
