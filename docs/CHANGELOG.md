# Changelog

## [Unreleased] - 2025-09-30

### Added - Conversation History Persistence

#### New Features
- **Automatic save on exit**: Conversation history saves when app closes
- **Automatic load on startup**: Previous conversations restore automatically
- **Persistent storage**: History saved to `data/conversation_history.json`
- **Manual save command**: Type `save` to save anytime
- **Shutdown handler**: Graceful shutdown with history preservation
- **Cross-session context**: Continue conversations across app restarts

#### What Changed
- `ConversationHistory` class: Added `save_to_disk()`, `load_from_disk()`, `delete_saved_history()` methods
- `MasterAgent`: Added `_load_conversation_history()`, `save_conversation_history()`, `shutdown()` methods
- `main.py`: Integrated shutdown handling on exit and Ctrl+C
- Storage format: JSON with timestamps and metadata

#### Behavior
- **On startup**: Automatically loads previous conversation if file exists
- **On exit**: Automatically saves current conversation (normal exit or Ctrl+C)
- **Manual save**: `save` command saves immediately
- **Clear history**: `clear-history` now also deletes the saved file

#### Usage Examples
```bash
# Session 1
$ python main.py
You: My name is Alice
Agent: Nice to meet you, Alice!
You: quit
💾 Saving conversation history...
✅ Saved 2 messages for next session

# Session 2 (later)
$ python main.py
💾 Restored previous conversation with 2 messages
You: Do you remember my name?
Agent: Yes, your name is Alice!
```

#### Testing
- Created `test_persistence.py` with comprehensive persistence tests
- Verified save/load across sessions
- Verified context preservation
- Verified clear-history removes saved file
- All tests passing

---

## [Unreleased] - 2025-09-30

### Added - Verbose Mode CLI Option

#### New Features
- **Command-line argument parsing** with `argparse`
- **Verbose mode flag**: `-v` or `--verbose`
  - Shows INFO level logs when enabled
  - Shows only WARNING/ERROR logs when disabled (default)
- **Enhanced help system**: `python main.py --help`
- **Logging configuration function**: `setup_logging(verbose=bool)`

#### What Changed
- `main.py`: Added CLI argument parsing and logging configuration
- Logging now configurable via command-line flag instead of hardcoded
- Default mode is now "quiet" (WARNING level) for cleaner output
- Verbose mode shows detailed operational logs including:
  - Master Agent initialization
  - Task classification decisions
  - Agent routing information  
  - HTTP requests to Azure OpenAI
  - Data manager operations
  - Conversation history updates

#### Usage Examples
```bash
# Run in quiet mode (default)
python main.py

# Run with verbose logging
python main.py -v
python main.py --verbose

# Show help
python main.py --help
```

#### Testing
- Created `test_verbose_mode.py` to verify logging functionality
- All tests pass in both quiet and verbose modes
- Verified INFO logs appear in verbose mode and are hidden in quiet mode

---

## [Unreleased] - 2025-09-30

### Added - Shared Conversation History

#### New Features
- **ConversationHistory class** (`conversation_history.py`)
  - Rolling window of last 20 messages (configurable)
  - Message tracking with timestamps and agent attribution
  - LangChain integration for seamless LLM communication
  - Context retrieval methods

- **Master Agent Updates**
  - Conversation history management integrated into chat workflow
  - Cross-agent context sharing
  - New methods: `get_conversation_history()`, `clear_conversation_history()`, `set_conversation_history_limit()`

- **Specialized Agent Updates**
  - All agents now have `process_with_history()` method
  - Agents can reference previous messages and maintain context
  - Backward compatibility with original `process()` methods

- **Interactive Commands**
  - `history`: View conversation statistics and recent messages
  - `clear-history`: Reset conversation history

#### What Changed
- Agents now share conversation context across specializations
- Chat → Analysis → Grading agents can all reference previous messages
- Rolling window prevents memory bloat while maintaining context
- Each response tagged with the agent that generated it

#### Usage
Conversation history is automatically managed:
- User messages and agent responses are tracked
- Last 20 messages maintained (10 exchanges)
- History persists across agent switches
- Can be cleared with `clear-history` command

#### Testing
- `test_chat_history.py`: Comprehensive conversation history tests
- `test_main_app.py`: Integration tests for main application
- All tests passing with context awareness verified

---

## Documentation

### New Files
- `USAGE.md`: Comprehensive usage guide with examples
- `CHANGELOG.md`: This file - tracking all changes
- `test_verbose_mode.py`: Test script for verbose mode
- `test_chat_history.py`: Test script for conversation history
- `test_main_app.py`: Integration test for main application

### Updated Files
- `main.py`: Added CLI argument parsing and verbose mode
- `master_agent.py`: Integrated conversation history management
- `agents/chat_agent.py`: Added history-aware processing
- `agents/analysis_agent.py`: Added history-aware processing
- `agents/grading_agent.py`: Added history-aware processing
