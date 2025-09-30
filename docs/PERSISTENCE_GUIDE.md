# Conversation History Persistence Guide

## Overview

The Azure OpenAI Master Agent System now features **automatic conversation history persistence**, allowing conversations to continue seamlessly across application sessions.

## How It Works

### Automatic Save
The conversation history is automatically saved in these scenarios:
- When you type `quit`, `exit`, or `bye`
- When you press `Ctrl+C` to interrupt the application
- On normal application termination

### Automatic Load
- Every time you start the application, it checks for a saved conversation
- If found, the conversation history is automatically restored
- You'll see: `💾 Restored previous conversation with X messages`
- If no saved history exists, starts fresh silently

### Storage Location
- **File**: `data/conversation_history.json`
- **Format**: JSON with message content, timestamps, and agent attribution
- **Max messages**: 20 (rolling window)

## Commands

| Command | Action | Result |
|---------|--------|--------|
| `save` | Manually save conversation | Saves current history to disk immediately |
| `clear-history` | Clear all history | Clears memory AND deletes saved file |
| `history` | View history stats | Shows message count and recent context |
| `quit`/`exit`/`bye` | Exit app | Auto-saves before closing |

## Usage Examples

### Example 1: Continue Conversation Next Day

```bash
# Monday afternoon
$ python main.py
👤 You: Hi, my name is Bob. I'm working on a Python project.
🤖 Chat Agent: Nice to meet you, Bob! I'd love to hear about your project...

👤 You: I need to analyze some CSV data
🤖 Analysis Agent: I can help with that...

👤 You: quit
💾 Saving conversation history...
✅ Saved 4 messages for next session
👋 Goodbye!

# Tuesday morning
$ python main.py
💾 Restored previous conversation with 4 messages

👤 You: Can you remind me what we discussed yesterday?
🤖 Chat Agent: Yesterday you mentioned you're Bob and working on a Python 
project involving CSV data analysis...
```

### Example 2: Manual Save During Important Conversation

```bash
👤 You: Let me explain my complex data analysis requirements...
🤖 Analysis Agent: [detailed response]

👤 You: save
💾 Saving conversation history...
✅ Saved 6 messages to disk

👤 You: Thanks, I'll continue this later
```

### Example 3: Start Fresh After Clearing History

```bash
👤 You: clear-history
🗑️  Conversation history cleared!

# Saved file is also deleted
# Next startup will have no history to restore
```

## What Gets Saved

Each saved conversation includes:
- **User messages**: Your input text
- **Assistant responses**: Agent replies
- **Timestamps**: When each message was sent
- **Agent attribution**: Which specialized agent handled each response
- **Metadata**: Additional context (if any)

## What Doesn't Get Saved

- Performance statistics (`stats` command)
- System status information
- Health check results
- Data manager interaction logs (separate storage in `data/interactions.jsonl`)

## File Structure

The saved JSON file looks like this:

```json
{
  "max_messages": 20,
  "saved_at": "2025-09-30T16:35:21.240437",
  "messages": [
    {
      "role": "user",
      "content": "My name is Bob",
      "timestamp": "2025-09-30T16:35:10.123456",
      "agent_type": null,
      "metadata": null
    },
    {
      "role": "assistant",
      "content": "Nice to meet you, Bob!",
      "timestamp": "2025-09-30T16:35:15.789012",
      "agent_type": "chat",
      "metadata": {}
    }
  ]
}
```

## Technical Details

### ConversationHistory Class Methods

**Persistence Methods:**
- `save_to_disk()` - Saves current history to JSON file
- `load_from_disk()` - Loads history from JSON file
- `delete_saved_history()` - Removes the saved file

**Usage in Code:**
```python
# Save
success = conversation_history.save_to_disk()

# Load
success = conversation_history.load_from_disk()

# Delete
success = conversation_history.delete_saved_history()
```

### MasterAgent Integration

**Startup:**
```python
def __init__(self):
    # ... initialization ...
    self.conversation_history = ConversationHistory(max_messages=20)
    self._load_conversation_history()  # Auto-load
```

**Shutdown:**
```python
def shutdown(self):
    if len(self.conversation_history) > 0:
        self.save_conversation_history()  # Auto-save
```

## Benefits

✅ **Continuity**: Resume conversations from days or weeks ago  
✅ **Context Preservation**: Agents remember previous interactions  
✅ **Agent Switching**: Context maintained across different specialized agents  
✅ **Automatic**: No manual intervention required  
✅ **Controllable**: Manual save and clear options available  
✅ **Graceful**: Handles interrupted sessions (Ctrl+C)  

## Limitations

- **Rolling Window**: Only last 20 messages are kept (configurable)
- **Single Session**: One saved conversation per installation (not multi-user)
- **No Versioning**: New saves overwrite previous saves
- **Local Only**: Saved to local disk, not cloud/database

## Advanced Usage

### Custom Storage Location

To use a different storage location, modify when creating ConversationHistory:

```python
history = ConversationHistory(
    max_messages=20,
    storage_file="path/to/custom/location.json"
)
```

### Change Message Limit

```python
agent.set_conversation_history_limit(40)  # Keep 40 messages instead of 20
```

### Programmatic Access

```python
# Get history stats
stats = agent.conversation_history.get_stats()

# Get recent context as string
context = agent.conversation_history.get_recent_context(num_messages=10)

# Get LangChain formatted messages
messages = agent.conversation_history.get_langchain_messages()
```

## Troubleshooting

**Q: History not loading on startup?**
- Check if `data/conversation_history.json` exists
- Verify file permissions (must be readable)
- Check logs for error messages (run with `-v` flag)

**Q: Save failing?**
- Ensure `data/` directory exists and is writable
- Check disk space
- Verify no file locks on `conversation_history.json`

**Q: Want to start completely fresh?**
```bash
# In the app
You: clear-history

# Or manually delete
rm data/conversation_history.json
```

**Q: How to backup conversations?**
```bash
# Copy the file before running
cp data/conversation_history.json backups/conversation_$(date +%Y%m%d).json
```

## Testing

Run the persistence test suite:

```bash
cd /Users/josephbalsamo/Development/Work/gradingAgent/grading-agent
source .venv/bin/activate
python test_persistence.py
```

This verifies:
- Save and load functionality
- Cross-session context preservation
- Clear history behavior
- File management

## Future Enhancements

Potential improvements (not yet implemented):
- Multiple named sessions
- Conversation branching
- Cloud storage integration
- Encryption for sensitive conversations
- Automatic backup rotation
- Export to different formats (Markdown, PDF)
