# Streaming Quick Start Guide

Get started with the new streaming capabilities in 5 minutes!

---

## Installation

No new dependencies needed! All streaming features use existing packages:
- `langchain` (already installed)
- `langgraph` (already installed)
- `streamlit` (already installed)

---

## Quick Examples

### 1. Basic Streaming (Async)

```python
import asyncio
from modules.master_agent import MasterAgent

async def main():
    agent = MasterAgent()
    
    # Stream a response
    async for event in agent.chat_streaming("Tell me about Python"):
        if event['type'] == 'chunk':
            print(event['content'], end='', flush=True)
        elif event['type'] == 'status':
            print(f"\n[{event['agent']}] {event['content']}")
    
    print("\n✅ Complete!")

# Run it
asyncio.run(main())
```

**Output:**
```
[master] Classifying request...
[chat] Processing with chat agent...
Python is a high-level programming language...
✅ Complete!
```

---

### 2. Grading Workflow (Auto Multi-Agent)

```python
import asyncio
from modules.master_agent import MasterAgent

async def grade_assignment():
    agent = MasterAgent()
    
    grading_request = """
    Grade this clinical note:
    Patient: John Doe, 45yo male
    Chief Complaint: Chest pain
    Assessment: Possible angina
    """
    
    full_response = ""
    async for event in agent.chat_streaming(grading_request):
        if event['type'] == 'chunk':
            full_response += event['content']
            print(event['content'], end='', flush=True)
        elif event['type'] == 'complete':
            print(f"\n✅ {event['agent']} done!")
    
    print("\n" + "="*50)
    print("FINAL GRADED OUTPUT:")
    print(full_response)

asyncio.run(grade_assignment())
```

**Workflow:**
```
✅ grading done!      (raw evaluation)
✅ formatting done!   (spreadsheet format)
```

---

### 3. Streamlit Integration

```python
import streamlit as st
import asyncio
from modules.master_agent import MasterAgent
from modules.ui import StreamingContainer

st.title("Grading Agent with Streaming")

user_input = st.text_area("Enter your request:")

if st.button("Submit"):
    agent = MasterAgent()
    placeholder = st.empty()
    container = StreamingContainer()
    
    async def stream():
        async for event in agent.chat_streaming(user_input):
            if event['type'] == 'chunk':
                container.update(event['content'])
                container.render(placeholder)
            elif event['type'] == 'status':
                st.info(f"[{event['agent']}] {event['content']}")
    
    # Run async in Streamlit
    asyncio.run(stream())
    st.success("Complete!")
```

---

### 4. Progress Tracking

```python
import asyncio
from modules.master_agent import MasterAgent
from modules.streaming import StreamingProgressTracker

async def grade_with_progress():
    agent = MasterAgent()
    tracker = StreamingProgressTracker(
        expected_agents=['grading', 'formatting']
    )
    
    async for event in agent.chat_streaming("Grade this assignment"):
        agent_name = event.get('agent')
        
        if event['type'] == 'status' and 'starting' in event['content'].lower():
            tracker.start_agent(agent_name)
            print(f"🔄 {agent_name} starting...")
        
        elif event['type'] == 'chunk':
            tracker.add_chunk(agent_name, event['content'])
            print(event['content'], end='', flush=True)
        
        elif event['type'] == 'complete':
            tracker.complete_agent(agent_name)
            print(f"\n✅ {agent_name} complete!")
            print(f"Progress: {tracker.get_overall_progress():.1f}%")
    
    # Get final metrics
    metrics = tracker.get_metrics()
    print(f"\n📊 Total time: {metrics['duration']:.2f}s")
    print(f"📊 Total chunks: {metrics['total_chunks']}")

asyncio.run(grade_with_progress())
```

---

### 5. Individual Agent Streaming

```python
import asyncio
from modules.agents.grading_agent import GradingAgent
from modules.conversation_history import ConversationHistory

async def stream_grading_agent():
    agent = GradingAgent()
    history = ConversationHistory()
    
    # Add context
    history.add_user_message("What's the rubric?")
    history.add_assistant_message("The rubric includes...", "grading")
    
    # Stream with history
    print("Grading Agent Output:")
    async for chunk in agent.stream_process(
        "Grade student assignment", 
        history
    ):
        print(chunk, end='', flush=True)
    
    print("\n✅ Done!")

asyncio.run(stream_grading_agent())
```

---

### 6. FormattingAgent Usage

```python
from modules.agents.formatting_agent import FormattingAgent
import asyncio

# Non-streaming
formatter = FormattingAgent()
grading_results = {
    "student": "Jane Doe",
    "sections": {
        "PS": {"ai": 8, "human": 9, "max": 10},
        "DX": {"ai": 7, "human": 7, "max": 10}
    }
}

formatted = formatter.format_grading_results(grading_results)
print(formatted)

# Streaming
async def stream_format():
    async for chunk in formatter.stream_process(grading_results):
        print(chunk, end='', flush=True)

asyncio.run(stream_format())
```

**Output:**
```markdown
| Section | AI Score | Human Score | Max | Δ |
|---------|----------|-------------|-----|---|
| PS      | 8        | 9           | 10  | -1 ⚠️ |
| DX      | 7        | 7           | 10  | 0 ✅ |
```

---

## Event Types

When using `chat_streaming()`, you'll receive these event types:

### Status Events
```python
{
    'type': 'status',
    'content': 'Classifying request...',
    'agent': 'master'
}
```
Use for: Progress indicators, status messages

### Chunk Events
```python
{
    'type': 'chunk',
    'content': 'This is part of the response',
    'agent': 'grading'
}
```
Use for: Real-time display, accumulating response

### Complete Events
```python
{
    'type': 'complete',
    'content': '',
    'agent': 'grading'
}
```
Use for: Marking agent completion, updating progress

### Error Events
```python
{
    'type': 'error',
    'content': 'Error message here'
}
```
Use for: Error handling, user notifications

---

## UI Components

### StreamingContainer
```python
from modules.ui import StreamingContainer
import streamlit as st

container = StreamingContainer()
placeholder = st.empty()

for chunk in stream:
    container.update(chunk)
    container.render(placeholder)
```

### AgentProgressIndicator
```python
from modules.ui import AgentProgressIndicator
import streamlit as st

AgentProgressIndicator.render(
    agent_name='Grading Agent',
    status='streaming',  # pending, streaming, complete, error
    details='Processing rubric items...',
    duration=2.5
)
```

### WorkflowVisualizer
```python
from modules.ui import WorkflowVisualizer
import streamlit as st

WorkflowVisualizer.render(
    workflow_steps=['Classify', 'Grade', 'Format', 'Synthesize'],
    current_step='Format',
    completed_steps=['Classify', 'Grade']
)
```

---

## Backward Compatibility

**All old code still works!**

```python
from modules.master_agent import MasterAgent

agent = MasterAgent()

# Old way - still works!
response = agent.chat("Hello")
print(response)

# New way - streaming!
async for event in agent.chat_streaming("Hello"):
    if event['type'] == 'chunk':
        print(event['content'], end='')
```

---

## Common Patterns

### Pattern 1: Collect Full Response
```python
async def get_full_response(user_input):
    agent = MasterAgent()
    full_response = ""
    
    async for event in agent.chat_streaming(user_input):
        if event['type'] == 'chunk':
            full_response += event['content']
    
    return full_response
```

### Pattern 2: Show Progress Bar
```python
import streamlit as st

async def stream_with_progress(user_input):
    agent = MasterAgent()
    progress = st.progress(0)
    
    chunks = 0
    async for event in agent.chat_streaming(user_input):
        if event['type'] == 'chunk':
            chunks += 1
            progress.progress(min(chunks / 10, 1.0))
```

### Pattern 3: Multi-Container Display
```python
import streamlit as st

async def multi_container_stream(user_input):
    agent = MasterAgent()
    
    containers = {
        'grading': st.empty(),
        'formatting': st.empty(),
        'chat': st.empty()
    }
    
    async for event in agent.chat_streaming(user_input):
        if event['type'] == 'chunk':
            agent_name = event['agent']
            if agent_name in containers:
                containers[agent_name].markdown(event['content'])
```

---

## Testing Your Streaming Code

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_streaming():
    from modules.master_agent import MasterAgent
    
    agent = MasterAgent()
    chunks = []
    
    async for event in agent.chat_streaming("Hello"):
        if event['type'] == 'chunk':
            chunks.append(event['content'])
    
    assert len(chunks) > 0
    full_response = ''.join(chunks)
    assert len(full_response) > 0
```

---

## Tips & Best Practices

### ✅ DO:
- Use `async for` with `chat_streaming()`
- Handle all event types (status, chunk, complete, error)
- Show progress indicators for long operations
- Buffer chunks before display to reduce UI flicker
- Test both streaming and non-streaming paths

### ❌ DON'T:
- Block the event loop with synchronous operations
- Ignore error events
- Update UI on every single chunk (buffer for performance)
- Forget to finalize streaming messages in history
- Mix async and sync code incorrectly

---

## Troubleshooting

### Issue: "RuntimeError: This event loop is already running"
**Solution:** Use `asyncio.run()` or ensure you're in an async context

### Issue: Chunks not appearing in real-time
**Solution:** Use `flush=True` when printing, or update UI placeholder immediately

### Issue: Streaming seems slow
**Solution:** Check chunk buffer size, reduce UI update frequency

### Issue: "Event type 'X' not recognized"
**Solution:** Always check event['type'] before accessing event fields

---

## Next Steps

1. **Try the examples above** in `examples/streaming_demo.py`
2. **Read** `docs/REFACTOR_SUMMARY.md` for complete details
3. **Run tests** with `pytest tests/test_streaming.py -v`
4. **Update your app** to use streaming for better UX

---

**Happy Streaming! 🚀**
