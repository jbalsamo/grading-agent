# Azure OpenAI Master Agent System with LangGraph

A sophisticated multi-agent Python application that uses LangGraph and LangChain to manage specialized AI agents and data storage with Azure OpenAI services.

## Features

- 🎯 **Master Agent Controller**: Intelligent task routing and agent coordination
- 🤖 **Specialized Agents**: Chat, Analysis, and Grading agents with unique capabilities
- 💾 **Data Management**: Persistent storage and context-aware interactions
- 🔄 **LangGraph Workflows**: Structured multi-step agent processing
- ⚙️ **Modular Architecture**: Clean separation of concerns and extensible design
- 💬 **Interactive Interface**: Enhanced chat with system commands and status monitoring
- 🛡️ **Comprehensive Error Handling**: Robust error management and logging

## Project Structure

```
grading-agent/
├── main.py              # Main application entry point
├── master_agent.py      # Master agent controller with LangGraph workflow
├── config.py            # Azure OpenAI configuration management
├── data_manager.py      # Data storage and context management
├── agents/              # Specialized agent modules
│   ├── __init__.py      # Package initialization
│   ├── chat_agent.py    # General conversation and assistance
│   ├── analysis_agent.py # Data analysis and computational tasks
│   └── grading_agent.py # Educational assessment and grading
├── data/                # Data storage directory (created automatically)
│   ├── interactions.jsonl # Interaction history
│   └── context.json     # Persistent context data
├── requirements.txt     # Python dependencies
├── .env                # Environment variables (not in git)
├── .env.template       # Environment template
└── README.md           # This file
```

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
   
   Edit `.env` with your Azure OpenAI configuration:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Usage

The Master Agent System will:
1. Initialize the master agent controller
2. Load specialized agents (Chat, Analysis, Grading)
3. Set up data management system
4. Send a hello message to test the connection
5. Start an interactive chat session with intelligent routing

### Interactive Commands
- **Regular messages**: Automatically routed to appropriate specialized agents
- **`status`**: Display system status and agent health
- **`help`**: Show available commands
- **`quit`/`exit`/`bye`**: Stop the application

### Agent Routing
The system automatically classifies your requests:
- **Chat Agent**: General conversation, questions, explanations
- **Analysis Agent**: Data analysis, computational tasks, research
- **Grading Agent**: Educational assessment, feedback, rubric creation

## Components

### `master_agent.py`
- **Master Agent Controller**: Orchestrates the entire system
- **Task Classification**: Automatically determines the appropriate agent
- **LangGraph Workflow**: Multi-step processing with error handling
- **Agent Coordination**: Routes tasks and synthesizes responses

### `agents/` Directory
- **`chat_agent.py`**: Specialized for general conversation and assistance
- **`analysis_agent.py`**: Optimized for data analysis and computational tasks
- **`grading_agent.py`**: Focused on educational assessment and grading

### `data_manager.py`
- **Persistent Storage**: Saves interaction history and context
- **Context Retrieval**: Provides relevant historical context
- **Data Analytics**: Tracks usage patterns and system performance

### `config.py`
- **Environment Management**: Loads and validates Azure OpenAI configuration
- **Centralized Settings**: Provides configuration access across the system

### `main.py`
- **Application Entry Point**: Initializes and runs the master agent system
- **Enhanced Interface**: Interactive chat with system commands and monitoring

## Requirements

- Python 3.8+
- Azure OpenAI resource with deployed model
- Valid API key and endpoint

## Advanced Features

### Data Persistence
- **Interaction History**: All conversations are stored in `data/interactions.jsonl`
- **Context Awareness**: System provides relevant context from previous interactions
- **Usage Analytics**: Track agent usage patterns and system performance

### Extensibility
- **Modular Design**: Easy to add new specialized agents
- **Plugin Architecture**: Agents can be independently developed and tested
- **Configuration Management**: Centralized settings for easy customization

## Error Handling

The system includes comprehensive error handling for:
- **Configuration Issues**: Missing or invalid Azure OpenAI settings
- **API Errors**: Azure OpenAI service connectivity and rate limiting
- **Agent Failures**: Graceful fallback when specialized agents encounter errors
- **Data Management**: Robust storage and retrieval error handling
- **Network Issues**: Automatic retry and error reporting
