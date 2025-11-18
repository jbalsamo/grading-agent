# Pre-Refactor Architecture Documentation

> ⚠️ **HISTORICAL DOCUMENT** ⚠️  
> This documents the architecture **BEFORE** the streaming refactor.  
> For current architecture, see `REFACTOR_SUMMARY.md` and `ARCHITECTURE_COMPARISON.md`

**Date:** November 12, 2025  
**Purpose:** Baseline documentation of LangGraph architecture before streaming refactor  
**Status:** 🔒 **ARCHIVED** - Reference only, not current implementation

---

## Overview

The grading agent application uses LangGraph (v0.2.28) for workflow orchestration. The MasterAgent coordinates multiple specialized agents through a state machine.

---

## Current LangGraph Flow

```
Entry Point: classify_task
      │
      ├─→ (task classified)
      │
      ▼
┌─────────────────────┐
│  classify_task      │  Classifies user input into: chat, analysis, grading
└──────────┬──────────┘
           │
           ├─ error? ──→ handle_error → END
           │
           ▼ route
┌─────────────────────┐
│  route_to_agent     │  Routes to specialized agent based on classification
└──────────┬──────────┘
           │
           ├─ error? ──→ handle_error → END
           │
           ├─ data manager available?
           │   │
           │   ├─ Yes ──→ manage_data → synthesize_response → END
           │   │
           │   └─ No ───→ synthesize_response → END
           │
           └─────────────────────────────────────────────────┘
```

---

## Node Definitions

### 1. classify_task

**Location:** `modules/master_agent.py` lines 223-290  
**Function:** `_classify_task(state: MasterAgentState) -> MasterAgentState`

**Responsibilities:**
- Receives user input from state
- Uses LLM to classify request into: `chat`, `analysis`, `grading`, `code_review`
- Sets `task_classification` and `agent_type` in state
- Creates message list for LangChain format

**Input State Fields:**
- `user_input` (str)

**Output State Fields:**
- `task_classification` (str)
- `agent_type` (str)
- `messages` (list)
- `error` (str, if classification fails)

**LLM Prompt:**
```python
"""
Classify the following user request into one of these categories:
- chat: General conversation, questions, or assistance
- analysis: Data analysis, file processing, or computational tasks
- grading: Educational assessment, grading, or evaluation tasks
- code_review: Code review, refactoring, or code quality analysis

User request: "{user_input}"

Respond with only the category name (chat, analysis, or grading).
"""
```

**Error Handling:**
- Sets `state["error"]` if input is empty
- Falls back to "chat" if LLM returns invalid category
- Logs all classification results

---

### 2. route_to_agent

**Location:** `modules/master_agent.py` lines 292-347  
**Function:** `_route_to_agent(state: MasterAgentState) -> MasterAgentState`

**Responsibilities:**
- Routes to appropriate specialized agent based on `agent_type`
- Calls agent's `process_with_history()` if available, else `process()`
- Falls back to master agent direct processing if specialized agent unavailable
- Stores agent response in `agent_responses` dict

**Specialized Agents:**
- `chat` → ChatAgent
- `analysis` → AnalysisAgent  
- `grading` → GradingAgent
- Fallback → Master agent LLM directly

**Input State Fields:**
- `agent_type` (str)
- `user_input` (str)

**Output State Fields:**
- `agent_responses` (dict): `{agent_name: response}`
- `error` (str, if routing fails)

**Key Logic:**
```python
if agent_type in self.specialized_agents:
    specialized_agent = self.specialized_agents[agent_type]
    if hasattr(specialized_agent, 'process_with_history'):
        response = specialized_agent.process_with_history(user_input, self.conversation_history)
    else:
        response = specialized_agent.process(user_input)
    state["agent_responses"] = {agent_type: response}
else:
    # Fallback: master agent with history
    response = self.llm.invoke(all_messages)
    state["agent_responses"] = {"master": response.content}
```

---

### 3. manage_data

**Location:** `modules/master_agent.py` lines 349-391  
**Function:** `_manage_data(state: MasterAgentState) -> MasterAgentState`

**Responsibilities:**
- Stores current interaction in DataManager (JSONL format)
- Retrieves relevant historical context based on user input
- Sets `data_context` with relevant previous interactions

**Input State Fields:**
- `user_input` (str)
- `agent_responses` (dict)
- `task_classification` (str)

**Output State Fields:**
- `data_context` (dict): Contains relevant past interactions
- `error` (str, if data management fails)

**DataManager Integration:**
```python
interaction_data = {
    "user_input": user_input,
    "task_type": state.get("task_classification", "unknown"),
    "agent_responses": agent_responses,
    "timestamp": self._get_timestamp()
}

self.data_manager.store_interaction(interaction_data)
context = self.data_manager.get_relevant_context(user_input)
state["data_context"] = context
```

**Note:** Optional node - only executes if DataManager is available

---

### 4. synthesize_response

**Location:** `modules/master_agent.py` lines 393-429  
**Function:** `_synthesize_response(state: MasterAgentState) -> MasterAgentState`

**Responsibilities:**
- Combines agent response with data context
- Creates final user-facing response
- Optionally enhances with historical context information

**Input State Fields:**
- `agent_responses` (dict)
- `data_context` (dict)

**Output State Fields:**
- `response` (str): Final response to return to user
- `error` (str, if synthesis fails)

**Logic:**
```python
# Get primary agent response
primary_response = list(agent_responses.values())[0]

# Add context info if relevant interactions found
if data_context and data_context.get("relevant_interactions"):
    context_info = f"\n\n[Context: Based on {len(data_context['relevant_interactions'])} previous interactions]"
    primary_response += context_info

state["response"] = primary_response
```

---

### 5. handle_error

**Location:** `modules/master_agent.py` lines 431-446  
**Function:** `_handle_error(state: MasterAgentState) -> MasterAgentState`

**Responsibilities:**
- Creates user-friendly error message
- Sets final response with error information
- Logs error for debugging

**Input State Fields:**
- `error` (str)

**Output State Fields:**
- `response` (str): Error message for user

**Error Response Format:**
```python
state["response"] = f"I apologize, but I encountered an error: {error_msg}"
```

---

## Conditional Edges

### _should_continue_classification

**Location:** `modules/master_agent.py` lines 448-462  
**Function:** `_should_continue_classification(state: MasterAgentState) -> str`

**Logic:**
```python
if state.get("error"):
    return "error"
return "route"
```

**Routes:**
- `"error"` → handle_error node
- `"route"` → route_to_agent node

---

### _should_manage_data

**Location:** `modules/master_agent.py` lines 464-481  
**Function:** `_should_manage_data(state: MasterAgentState) -> str`

**Logic:**
```python
if state.get("error"):
    return "error"
if self.data_manager:
    return "data"
return "synthesize"
```

**Routes:**
- `"error"` → handle_error node
- `"data"` → manage_data node (if DataManager available)
- `"synthesize"` → synthesize_response node (skip data management)

---

## State Schema

### MasterAgentState

**Location:** `modules/master_agent.py` lines 21-46  
**Type:** TypedDict

```python
class MasterAgentState(TypedDict):
    messages: list
    user_input: str
    response: str
    error: str
    agent_type: str
    task_classification: str
    agent_responses: dict
    data_context: dict
    conversation_history: list
```

**Field Descriptions:**
- `messages`: LangChain message format for LLM
- `user_input`: Original user query
- `response`: Final response to return
- `error`: Error message if any step fails
- `agent_type`: Classified agent type (chat/analysis/grading)
- `task_classification`: Same as agent_type (redundant)
- `agent_responses`: Dict of {agent_name: response_text}
- `data_context`: Retrieved historical interactions
- `conversation_history`: Messages for conversation context

---

## Graph Construction

**Location:** `modules/master_agent.py` lines 169-221  
**Function:** `_create_graph() -> StateGraph`

```python
workflow = StateGraph(MasterAgentState)

# Add nodes
workflow.add_node("classify_task", self._classify_task)
workflow.add_node("route_to_agent", self._route_to_agent)
workflow.add_node("manage_data", self._manage_data)
workflow.add_node("synthesize_response", self._synthesize_response)
workflow.add_node("handle_error", self._handle_error)

# Set entry point
workflow.set_entry_point("classify_task")

# Add conditional edges
workflow.add_conditional_edges(
    "classify_task",
    self._should_continue_classification,
    {"route": "route_to_agent", "error": "handle_error"}
)

workflow.add_conditional_edges(
    "route_to_agent",
    self._should_manage_data,
    {"data": "manage_data", "synthesize": "synthesize_response", "error": "handle_error"}
)

# Add direct edges
workflow.add_edge("manage_data", "synthesize_response")
workflow.add_edge("synthesize_response", END)
workflow.add_edge("handle_error", END)

return workflow.compile()
```

---

## Agent Initialization

**Location:** `modules/master_agent.py` lines 133-167  
**Function:** `_initialize_agents()`

**Currently Loaded Agents:**
```python
self.specialized_agents = {
    "chat": ChatAgent(),
    "analysis": AnalysisAgent(),
    "grading": GradingAgent()
}
```

**Agent Capabilities:**
- **ChatAgent**: General conversation with history awareness
- **AnalysisAgent**: Data analysis, statistics, code generation
- **GradingAgent**: Clinical student note grading with semantic matching

---

## Conversation History Integration

**Implementation:**
- 20-message rolling window (configurable)
- Stored in `ConversationHistory` class
- Passed to agents via `process_with_history()` method
- Persisted to disk: `data/conversation_history.json`

**Usage in Agents:**
```python
history_messages = conversation_history.get_langchain_messages()
all_messages = [SystemMessage(...)] + history_messages + [HumanMessage(...)]
response = self.llm.invoke(all_messages)
```

---

## Current Limitations (To Be Addressed in Refactor)

1. **No Streaming**: All responses are blocking (full response at once)
2. **Single Agent Path**: Each request routes to only ONE agent
3. **No Multi-Agent Workflows**: Cannot chain agents (e.g., grading → formatting)
4. **No Progress Feedback**: User has no visibility into agent processing
5. **No Formatting Agent**: Grading results not formatted as spreadsheets
6. **Limited Error Recovery**: Errors terminate the workflow immediately

---

## Paths Through Graph

### Path 1: Successful with Data Management
```
classify_task → route_to_agent → manage_data → synthesize_response → END
```

### Path 2: Successful without Data Management
```
classify_task → route_to_agent → synthesize_response → END
```

### Path 3: Classification Error
```
classify_task → handle_error → END
```

### Path 4: Routing Error
```
classify_task → route_to_agent → handle_error → END
```

---

## Performance Characteristics

**Current Behavior:**
- **Blocking**: Complete response generated before returning
- **Latency**: User sees nothing until final response ready
- **Memory**: All messages kept in memory during processing
- **Cache**: Optional response caching (enabled by default)

**Timing Observations:**
- Classification: ~1-2 seconds
- Agent processing: Varies by task (2-10 seconds typical)
- Total: 3-12 seconds typical for complete response

---

## Components to Preserve

✅ **Keep Unchanged:**
- All agent system prompts (see PROMPT_REGISTRY.md)
- State field names (for compatibility)
- ConversationHistory integration
- DataManager JSONL storage format
- Error handling patterns

⚠️ **Modify Carefully:**
- Graph structure (adding nodes, not removing)
- State schema (adding fields, not removing)
- Agent initialization (adding FormattingAgent)

---

## Next Steps (Refactor)

1. **Add Streaming**: Implement `chat_streaming()` with `astream_events()`
2. **Add Grading Workflow**: Create Master → Grading → Formatting → Chat path
3. **Add FormattingAgent**: New agent for spreadsheet generation
4. **Enhance State**: Add streaming-specific fields
5. **Add UI Components**: Progress indicators and streaming display

---

**Last Updated:** November 12, 2025  
**Refactor Phase:** 1.2 - Architecture Mapping  
**Status:** ✅ Complete - Current architecture documented
