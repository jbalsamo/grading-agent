# Project Structure

## Overview

The Azure OpenAI Master Agent System is now organized into a clean, modular structure for better maintainability and scalability.

## Directory Structure

```
grading-agent/
├── main.py                 # Application entry point
├── README.md              # Project overview
├── requirements.txt       # Python dependencies
├── .env                   # Configuration (not in git)
├── .env.template         # Configuration template
│
├── modules/              # Core application modules
│   ├── __init__.py       # Package initialization
│   ├── master_agent.py   # Master agent orchestrator
│   ├── conversation_history.py  # Chat history management
│   ├── data_manager.py   # Data storage and retrieval
│   ├── config.py         # Configuration management
│   ├── utils.py          # Utility functions
│   ├── validate_config.py # Configuration validation
│   └── agents/           # Specialized agents
│       ├── __init__.py
│       ├── chat_agent.py      # General conversation agent
│       ├── analysis_agent.py  # Data analysis agent
│       └── grading_agent.py   # Educational grading agent
│
├── tests/                # Test suite
│   ├── README.md                     # Testing documentation
│   ├── conftest.py                   # Pytest fixtures
│   ├── test_chat_history.py          # Conversation history tests
│   ├── test_config.py                # Configuration tests
│   ├── test_conversation_history.py  # History class tests
│   ├── test_integration.py           # Integration tests
│   ├── test_main_app.py              # Main application tests
│   ├── test_persistence.py           # Persistence tests
│   ├── test_utils.py                 # Utility tests
│   └── test_verbose_mode.py          # Logging tests
│
├── docs/                 # Documentation
│   ├── PROJECT_STRUCTURE.md       # This file
│   ├── USAGE.md                   # Usage guide
│   ├── PERSISTENCE_GUIDE.md       # Persistence documentation
│   ├── CHANGELOG.md               # Change log
│   ├── DEPLOYMENT_SUMMARY.md      # Deployment guide
│   ├── REORGANIZATION_SUMMARY.md  # Project reorganization notes
│   ├── TESTING_SUMMARY.md         # Testing documentation
│   └── SYSTEM_OVERVIEW.md         # System architecture
│
├── examples/             # Example scripts
│   ├── README.md
│   ├── agent_comparison.py    # Compare agent responses
│   └── batch_processing.py    # Batch processing example
│
└── data/                 # Runtime data (not in git)
    ├── interactions.jsonl          # Interaction logs
    └── conversation_history.json   # Saved conversations
```

## Module Organization

### Core Modules (`modules/`)

All core application logic is contained in the `modules/` package:

**Main Components:**
- `master_agent.py` - Orchestrates specialized agents and manages workflow
- `conversation_history.py` - Manages chat history with persistence
- `data_manager.py` - Handles data storage and context retrieval
- `config.py` - Configuration management from environment variables
- `utils.py` - System monitoring and health checking utilities
- `validate_config.py` - Configuration validation

**Specialized Agents (`modules/agents/`):**
- `chat_agent.py` - General conversation and Q&A
- `analysis_agent.py` - Data analysis and computational tasks
- `grading_agent.py` - Educational assessment and grading

### Tests (`tests/`)

Comprehensive test suite covering:
- Conversation history functionality and persistence
- Configuration validation and loading
- Main application integration and workflows
- System utilities and monitoring
- Verbose mode logging
- Agent processing with and without history
- Data manager operations

### Documentation (`docs/`)

All project documentation in one place:
- User guides and tutorials
- System architecture documentation
- API references and examples
- Deployment and configuration guides

### Examples (`examples/`)

Practical examples demonstrating:
- Agent comparison and capabilities
- Batch processing workflows
- Integration patterns

## Import Paths

### From Application Root

```python
# Main application
from modules.master_agent import MasterAgent
from modules.config import config
from modules.conversation_history import ConversationHistory

# Specialized agents
from modules.agents.chat_agent import ChatAgent
from modules.agents.analysis_agent import AnalysisAgent
from modules.agents.grading_agent import GradingAgent
```

### Within Modules Package

```python
# Relative imports within modules/
from .config import config
from .utils import SystemMonitor
from .conversation_history import ConversationHistory

# From agents subpackage
from .agents.chat_agent import ChatAgent
```

## Running the Application

### Main Application
```bash
cd /Users/josephbalsamo/Development/Work/gradingAgent/grading-agent
source .venv/bin/activate
python main.py                # Quiet mode
python main.py -v             # Verbose mode
python main.py --help         # Show help
```

### Tests
```bash
# Run all tests with pytest
pytest tests/

# Run individual test files
pytest tests/test_chat_history.py
pytest tests/test_conversation_history.py
pytest tests/test_config.py
pytest tests/test_integration.py
pytest tests/test_main_app.py
pytest tests/test_persistence.py
pytest tests/test_utils.py
pytest tests/test_verbose_mode.py

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=modules --cov-report=html
```

### Examples
```bash
python examples/agent_comparison.py
python examples/batch_processing.py
```

## File Responsibilities

### Entry Point
- **`main.py`** - CLI interface, argument parsing, application lifecycle

### Core Modules
- **`master_agent.py`** - Agent orchestration, task classification, workflow management
- **`conversation_history.py`** - Message storage, persistence, context retrieval
- **`data_manager.py`** - Interaction logging, context search, analytics
- **`config.py`** - Environment configuration, Azure OpenAI settings
- **`utils.py`** - System monitoring, health checks, statistics

### Agents
- **`chat_agent.py`** - General conversation, Q&A, explanations
- **`analysis_agent.py`** - Data analysis, code generation, research
- **`grading_agent.py`** - Educational assessment, feedback, rubrics

## Data Flow

1. **User Input** → `main.py`
2. **Main** → `MasterAgent.chat()`
3. **MasterAgent** → Task classification (LLM)
4. **MasterAgent** → Route to specialized agent
5. **Specialized Agent** → Process with conversation history
6. **Agent** → Generate response (LLM)
7. **MasterAgent** → Store interaction (DataManager)
8. **MasterAgent** → Save conversation history
9. **Response** → User

## Configuration

### Environment Variables (`.env`)
```bash
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
```

### Application Settings
- **Max conversation history**: 20 messages (configurable in `ConversationHistory`)
- **Storage location**: `data/conversation_history.json`
- **Log level**: WARNING (default) or INFO (verbose mode)

## Development Guidelines

### Adding a New Agent

1. Create agent in `modules/agents/new_agent.py`:
```python
from typing import Dict, Any, TYPE_CHECKING
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..config import config

if TYPE_CHECKING:
    from ..conversation_history import ConversationHistory

class NewAgent:
    def __init__(self):
        self.llm = AzureChatOpenAI(**config.get_azure_openai_kwargs())
        self.agent_type = "new_agent"
    
    def process_with_history(self, user_input: str, 
                             conversation_history: 'ConversationHistory') -> str:
        # Implementation
        pass
```

2. Register in `master_agent.py`:
```python
from .agents.new_agent import NewAgent

self.specialized_agents = {
    "chat": ChatAgent(),
    "analysis": AnalysisAgent(),
    "grading": GradingAgent(),
    "new_agent": NewAgent()  # Add here
}
```

3. Update task classification in `_classify_task()` method

### Adding a New Test

1. Create test file in `tests/test_new_feature.py`:
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.master_agent import MasterAgent

def test_new_feature():
    # Test implementation
    pass

if __name__ == "__main__":
    test_new_feature()
```

### Adding Documentation

1. Create markdown file in `docs/`
2. Follow existing documentation style
3. Update this file with references

## Migration Notes

### From Old Structure
The project was reorganized from a flat structure to the current modular organization:

**Old:**
```
grading-agent/
├── master_agent.py
├── config.py
├── agents/
├── test_*.py
└── *.md
```

**New:**
```
grading-agent/
├── modules/
│   ├── master_agent.py
│   ├── config.py
│   └── agents/
├── tests/
│   └── test_*.py
└── docs/
    └── *.md
```

### Import Changes
All imports were updated to use the new module structure:
- `from master_agent import` → `from modules.master_agent import`
- `from config import` → `from modules.config import`
- `from agents.x import` → `from modules.agents.x import`

## Best Practices

1. **Imports**: Use relative imports within modules package
2. **Tests**: Always add path to parent directory in test files
3. **Documentation**: Keep docs up to date with code changes
4. **Examples**: Provide working examples for new features
5. **Structure**: Keep related code in appropriate directories

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError`:
- Ensure you're running from the project root
- Check that `modules/__init__.py` exists
- Verify Python path is set correctly

### Test Failures
- Ensure virtual environment is activated
- Check that all dependencies are installed
- Verify `.env` file is configured correctly

### Path Issues
- Always use absolute imports from project root
- Tests should add parent directory to `sys.path`
- Examples should add parent directory to `sys.path`
