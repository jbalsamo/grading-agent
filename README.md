# Azure OpenAI Master Agent System

> A modular, multi-agent system with conversation history persistence and specialized AI agents with LangGraph

A sophisticated multi-agent Python application that uses LangGraph and LangChain to manage specialized AI agents and data storage with Azure OpenAI services.

## Features

- 🎯 **Master Agent Controller**: Intelligent task routing and agent coordination using LangGraph
- 🤖 **Specialized Agents**: Chat, Analysis, and Grading agents with unique capabilities
- 💬 **Conversation History**: Shared 20-message rolling window across all agents with persistence
- 💾 **Data Management**: Persistent storage of interactions in JSONL format
- 🔄 **LangGraph Workflows**: Structured multi-step agent processing with conditional routing
- ⚙️ **Modular Architecture**: Clean separation of concerns and extensible design
- 📊 **System Monitoring**: Performance tracking, health checks, and usage statistics
- 💻 **Interactive CLI**: Enhanced chat with system commands, verbose mode, and status monitoring
- 🛡️ **Comprehensive Error Handling**: Robust error management and logging
- 🔁 **Session Persistence**: Conversation history automatically saves and restores between sessions

## Project Structure

```
grading-agent/
├── main.py                 # Application entry point
├── README.md              # Project overview
├── requirements.txt       # Python dependencies
├── pytest.ini             # Pytest configuration
├── .env                   # Configuration (not in git)
├── .env.template          # Environment template
├── .gitignore            # Git ignore rules
│
├── modules/              # Core application modules
│   ├── __init__.py       # Module initialization
│   ├── master_agent.py   # Master agent orchestrator
│   ├── conversation_history.py  # Chat history with persistence
│   ├── data_manager.py   # Data storage and retrieval
│   ├── config.py         # Configuration management
│   ├── validate_config.py # Configuration validation
│   ├── utils.py          # Utilities and monitoring
│   └── agents/           # Specialized agents
│       ├── __init__.py        # Agents module init
│       ├── chat_agent.py      # General conversation
│       ├── analysis_agent.py  # Data analysis
│       └── grading_agent.py   # Educational grading
│
├── tests/                # Test suite
│   ├── README.md              # Testing documentation
│   ├── conftest.py           # Pytest fixtures
│   ├── test_chat_history.py
│   ├── test_config.py
│   ├── test_conversation_history.py
│   ├── test_integration.py
│   ├── test_main_app.py
│   ├── test_persistence.py
│   ├── test_utils.py
│   └── test_verbose_mode.py
│
├── docs/                 # Documentation
│   ├── USAGE.md
│   ├── PERSISTENCE_GUIDE.md
│   ├── PROJECT_STRUCTURE.md
│   ├── SYSTEM_OVERVIEW.md
│   ├── TESTING_SUMMARY.md
│   ├── DEPLOYMENT_SUMMARY.md
│   ├── REORGANIZATION_SUMMARY.md
│   └── CHANGELOG.md
│
├── examples/             # Example scripts
│   ├── README.md
│   ├── agent_comparison.py
│   └── batch_processing.py
│
└── data/                 # Runtime data
    └── interactions.jsonl
```

📖 **See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for detailed structure documentation**

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Copy `.env.template` to `.env` and fill in your Azure OpenAI details:
   ```bash
   cp .env.template .env
   ```
   
   Required configuration in `.env`:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
   ```
   
   Optional configuration:
   ```
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
   AZURE_COGNITIVE_SERVICES_KEY=your-cognitive-services-key
   AZURE_COGNITIVE_SERVICES_REGION=your-region
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your-langsmith-api-key
   LANGCHAIN_PROJECT=azure-agent-notebook
   ```

3. **Run the application:**
   ```bash
   # Run in quiet mode (WARNING level and above)
   python main.py
   
   # Run with verbose logging (INFO level)
   python main.py -v
   python main.py --verbose
   ```

## Usage

The Master Agent System will:
1. Initialize the master agent controller with Azure OpenAI
2. Load specialized agents (Chat, Analysis, Grading)
3. Set up data management system and conversation history
4. Restore previous conversation history from disk (if available)
5. Send a hello message to test the connection
6. Start an interactive chat session with intelligent routing
7. Auto-save conversation history on exit

### Interactive Commands
- **Regular messages**: Automatically routed to appropriate specialized agents
- **`status`**: Display system status and agent health
- **`stats`**: Show performance statistics (uptime, response time, agent usage)
- **`health`**: Run comprehensive health check
- **`history`**: View conversation history statistics and recent messages
- **`clear-history`**: Clear conversation history and delete saved file
- **`save`**: Manually save conversation history to disk
- **`help`**: Show available commands
- **`quit`/`exit`/`bye`**: Exit the application (auto-saves conversation history)

### Agent Routing
The system automatically classifies your requests:
- **Chat Agent**: General conversation, questions, explanations
- **Analysis Agent**: Data analysis, computational tasks, research
- **Grading Agent**: Educational assessment, feedback, rubric creation

## Components

### `master_agent.py`
- **Master Agent Controller**: Orchestrates the entire system using LangGraph
- **Task Classification**: Uses LLM to classify requests as chat, analysis, or grading
- **LangGraph Workflow**: Multi-step processing (classify → route → manage data → synthesize)
- **Agent Coordination**: Routes tasks to specialized agents with conversation history
- **Conversation History**: Maintains 20-message rolling window shared across agents
- **Session Persistence**: Automatically saves/restores conversation history
- **System Monitoring**: Tracks performance metrics and health status

### `agents/` Directory
All agents support both standard processing and conversation history:
- **`chat_agent.py`**: General conversation with context awareness
- **`analysis_agent.py`**: Data analysis and computational tasks with history
- **`grading_agent.py`**: Educational assessment with conversation context

Each agent implements:
- `process(user_input)`: Basic processing without history
- `process_with_history(user_input, conversation_history)`: Context-aware processing
- `get_status()`: Agent health status
- `get_capabilities()`: Agent capabilities description

### `conversation_history.py`
- **Rolling Window**: Maintains last 20 messages across all agents
- **Session Persistence**: Saves to `data/conversation_history.json`
- **Cross-Agent Sharing**: All agents access the same conversation context
- **Message Attribution**: Tracks which agent generated each response
- **LangChain Integration**: Formats messages for LLM consumption

### `data_manager.py`
- **Interaction Storage**: Saves all interactions to `data/interactions.jsonl`
- **Context Retrieval**: Keyword-based relevance matching
- **Usage Analytics**: Task type distribution and agent usage statistics
- **Data Cleanup**: Configurable retention period for old interactions

### `config.py`
- **Environment Management**: Loads configuration from `.env` file
- **Validation**: Ensures required Azure OpenAI settings are present
- **Centralized Access**: Provides global config instance

### `utils.py`
- **SystemMonitor**: Tracks requests, errors, response times, and agent usage
- **ConfigValidator**: Validates Azure config and data directory setup
- **SystemHealthChecker**: Comprehensive health checks with status reporting

### `main.py`
- **CLI Entry Point**: Initializes and runs the master agent system
- **Argument Parsing**: Supports verbose mode (`-v`, `--verbose`)
- **Interactive Commands**: Status, stats, health, history, and more
- **Graceful Shutdown**: Auto-saves conversation history on exit

## Requirements

- Python 3.8+
- Azure OpenAI resource with deployed model
- Valid API key and endpoint

## Advanced Features

### Conversation History Management
- **Rolling Window**: Keeps last 20 messages (configurable via `max_messages`)
- **Session Persistence**: Automatically saves to `data/conversation_history.json`
- **Cross-Session Continuity**: Restores history on startup for seamless continuation
- **Agent Attribution**: Each message tagged with originating agent
- **Manual Control**: Commands for viewing stats, clearing, and manual saves

### Data Persistence
- **Interaction Logging**: All conversations stored in `data/interactions.jsonl` (JSONL format)
- **Separate Concerns**: Conversation history (20-message window) vs. full interaction log
- **Context Retrieval**: Keyword-based search for relevant past interactions
- **Usage Analytics**: Task type distribution, agent usage, and recent activity tracking

### System Monitoring
- **Performance Metrics**: Response times, request counts, error rates
- **Agent Statistics**: Per-agent usage and average response times
- **Health Checks**: Configuration, data directory, connectivity, and system resources
- **Uptime Tracking**: System uptime and requests per minute

### Extensibility
- **Modular Design**: Easy to add new specialized agents
- **Conversation History Support**: New agents can implement `process_with_history()` for context
- **Backward Compatibility**: Agents without history support fall back to `process()`
- **LangGraph Workflow**: Conditional routing enables complex agent orchestration
- **Configuration Management**: Centralized settings for easy customization

## Error Handling

The system includes comprehensive error handling for:
- **Configuration Issues**: Missing or invalid Azure OpenAI settings
- **API Errors**: Azure OpenAI service connectivity and rate limiting
- **Agent Failures**: Graceful fallback when specialized agents encounter errors
- **Data Management**: Robust storage and retrieval error handling
- **Network Issues**: Automatic retry and error reporting
