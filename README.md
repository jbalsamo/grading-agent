# Grading Helper

> A grading-focused StreamLit application built on a modular Azure OpenAI multi-agent system with document processing and specialized AI agents via LangGraph

Grading Helper is a sophisticated multi-agent Python application centered on clinical and educational grading workflows. It uses LangGraph and LangChain to manage specialized AI agents and data storage with Azure OpenAI services, and exposes them through a modern StreamLit web interface with Google APK-style debugging tools and document upload capabilities.

## Features

- 🌐 **StreamLit Web Interface**: Modern dark-themed web UI with Google APK-style debugging tools
- ⚡ **Real-Time Streaming**: Streaming chat responses with instant visual feedback
- 📄 **Document Upload & Processing**: Upload PDFs, DOCX, Excel, and more - automatically converted to markdown
- 🔍 **Advanced Debugging Tools**: Variable viewer, request history, and agent state inspection
- 📊 **Real-time Token Tracking**: Monitor token usage across documents and conversations
- 🎯 **Master Agent Controller**: Intelligent task routing and agent coordination using LangGraph
- 🤖 **Specialized Agents**: Chat, Analysis, Grading, and Code Review agents with unique capabilities
- 📋 **Clinical Grading**: Specialized semantic grading for clinical student patient notes with safeguards
- 💬 **Conversation History**: Shared 20-message rolling window across all agents with persistence
- 💾 **Data Management**: Persistent storage of interactions in JSONL format
- 🔄 **LangGraph Workflows**: Structured multi-step agent processing with conditional routing
- ⚙️ **Modular Architecture**: Clean separation of concerns and extensible design
- 📈 **System Monitoring**: Performance tracking, health checks, and usage statistics
- 💻 **Interactive CLI**: Enhanced command-line interface with system commands and verbose mode
- 🛡️ **Security Features**: Input validation, rate limiting, and sanitization
- 🔁 **Session Persistence**: Conversation history and session data automatically saved

## Project Structure

```
grading-agent/
├── app.py                 # StreamLit web application
├── main.py                # CLI application entry point
├── README.md              # Project overview (you are here)
├── requirements.txt       # Python dependencies
├── pytest.ini             # Pytest configuration
├── .env                   # Configuration (not in git)
├── .env.template          # Environment template
├── .gitignore            # Git ignore rules
├── run_app.sh             # StreamLit app launcher script
│
├── docs/                 # 📚 Documentation (see docs/INDEX.md)
│   ├── INDEX.md          # Documentation index
│   ├── GRADING_GUIDE.md  # Clinical grading instructions
│   ├── GRADING_REPORT_FORMAT.md  # Grading report structure
│   ├── STREAMING_IMPLEMENTATION.md  # Streaming features
│   ├── TEMPERATURE_FIX.md  # Troubleshooting guide
│   └── ... (see INDEX.md for full list)
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
│       ├── grading_agent.py   # Educational grading
│       └── grading_prompts.py # Clinical grading prompt templates
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
   # Azure services
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
   AZURE_COGNITIVE_SERVICES_KEY=your-cognitive-services-key
   AZURE_COGNITIVE_SERVICES_REGION=your-region
   
   # Agent behavior
   AGENT_TEMPERATURE=1.0
   MAX_CONVERSATION_MESSAGES=20
   
   # Performance & security
   RATE_LIMIT_ENABLED=true
   RATE_LIMIT_CALLS=10
   RATE_LIMIT_PERIOD=60
   ENABLE_RESPONSE_CACHE=true
   CACHE_TTL=300
   MAX_INPUT_LENGTH=500000
   
   # Monitoring
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your-langsmith-api-key
   LANGCHAIN_PROJECT=azure-agent-notebook
   ```

3. **Run the application:**
   
   **Option A: StreamLit Web Interface (Recommended)**
   ```bash
   # Start the StreamLit web app (normal mode)
   streamlit run app.py
   
   # Start with debug mode enabled
   streamlit run app.py -- -D
   # or
   streamlit run app.py -- --debug
   
   # Using the run script
   ./run_app.sh          # Normal mode
   ./run_app.sh -D       # Debug mode
   
   # App will open in your browser at http://localhost:8501
   ```
   
   **Option B: Command-Line Interface**
   ```bash
   # Run in quiet mode (WARNING level and above)
   python main.py
   
   # Run with verbose logging (INFO level)
   python main.py -v
   python main.py --verbose
   ```

## Usage

### StreamLit Web Interface (Grading Helper)

The Grading Helper StreamLit app provides a modern web interface with:

**Main Features:**
- **Document Upload**: Upload PDFs, DOCX, Excel, PowerPoint, and text files
  - Automatic conversion to markdown using `markitdown` library
  - Documents added to agent context for enhanced responses
  - Real-time token usage tracking
- **Chat Interface**: Interactive conversation with the master agent
  - Message history display with metadata
  - Real-time response generation
  - Context-aware responses using uploaded documents
- **Debugging Tools** (Google APK-style):
  - **Variable Viewer**: Inspect session state and runtime variables
  - **Request History**: View detailed request/response logs
  - **Agent State**: Monitor agent status and configuration
- **Metrics Sidebar**:
  - Total token usage across all documents and messages
  - Document count and details
  - Request statistics and performance metrics
  - Error rate monitoring

**Getting Started:**
1. Start the app: `streamlit run app.py` (or with `-D` for debug mode)
2. Upload documents (optional) using the sidebar
3. Start chatting with the agent
4. Enable debug mode to inspect variables and requests (if not already enabled via `-D`)
5. Export session data for analysis

**Debug Mode:**
Debug mode can be enabled in two ways:
- **CLI flag**: Use `-D` or `--debug` when starting the app
- **UI toggle**: Click the toggle switch in the sidebar (only visible if debug mode is accessible)

When debug mode is enabled, you get:
- Document processing details (character counts, token estimates)
- Context size information before each request
- Full markdown preview of uploaded documents
- Variable viewer showing session state
- Request history with detailed JSON logs
- Agent state inspector

### Command-Line Interface

The CLI provides a terminal-based interface that:
1. Initializes the master agent controller with Azure OpenAI
2. Loads specialized agents (Chat, Analysis, Grading, Code Review)
3. Sets up data management system and conversation history
4. Restores previous conversation history from disk (if available)
5. Sends a hello message to test the connection
6. Starts an interactive chat session with intelligent routing
7. Auto-saves conversation history on exit

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
  - **Clinical Grading Specialization**: Semantic grading for student patient notes
  - **Scoring Thresholds**: Semantic similarity ≥ 0.55, token overlap ≥ 0.35, combined ≥ 0.50
  - **Safeguards**: Checked-only and student-content (anti-template) safeguards
  - **See [GRADING_GUIDE.md](docs/GRADING_GUIDE.md) for detailed clinical grading instructions**

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
- StreamLit 1.31.1+ (for web interface)
- markitdown library (for document processing)

## Supported Document Formats

The StreamLit interface supports uploading and processing the following file types:
- **PDF** (.pdf) - Portable Document Format
- **Word** (.docx, .doc) - Microsoft Word documents  
- **Excel** (.xlsx, .xls, .csv) - Spreadsheets and data files
- **PowerPoint** (.pptx) - Presentations
- **Text** (.txt, .md) - Plain text and Markdown files

All uploaded documents are automatically converted to markdown and added to the agent's context, enabling intelligent responses based on document content.

## Advanced Features

### StreamLit Debugging Tools (Google APK-style)

The web interface includes professional debugging tools inspired by Google APK:

**Variable Viewer**
- Real-time inspection of session state variables
- Message count tracking
- Document load status
- Token usage monitoring
- Agent initialization status

**Request History**
- Detailed logs of all requests and responses
- JSON-formatted request/response data
- Timestamp tracking
- Token usage per request
- Response time metrics

**Agent State Inspector**
- Real-time agent status monitoring
- Specialized agent health checks
- Data manager status
- System configuration display

**Session Export**
- Export complete session data to JSON
- Includes conversation history, uploaded documents, and metrics
- Useful for debugging and analysis

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

## 📚 Documentation

Complete documentation is available in the [`docs/`](docs/) folder:

- **[Documentation Index](docs/INDEX.md)** - Complete list of all documentation
- **[Grading Guide](docs/GRADING_GUIDE.md)** - Clinical grading instructions
- **[Grading Report Format](docs/GRADING_REPORT_FORMAT.md)** - Report structure and examples
- **[Streaming Implementation](docs/STREAMING_IMPLEMENTATION.md)** - Real-time streaming features
- **[Temperature Fix](docs/TEMPERATURE_FIX.md)** - Troubleshooting temperature parameter errors
- **[Usage Guide](docs/USAGE.md)** - How to use the system
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Development guidelines

For a complete list of all documentation, see **[docs/INDEX.md](docs/INDEX.md)**.
