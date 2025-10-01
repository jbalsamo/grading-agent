# Azure OpenAI Multi-Agent System: Developer Guide

> A comprehensive guide for intermediate to advanced developers on understanding, extending, and building with the grading-agent multi-agent system.

## Table of Contents
1. [Introduction & Architecture Overview](#introduction--architecture-overview)
2. [Understanding the Agent System](#understanding-the-agent-system)
3. [How Agents Work](#how-agents-work)
4. [Adding New Agents](#adding-new-agents)
5. [Tools & Utilities You Can Add](#tools--utilities-you-can-add)
6. [Conversation History System](#conversation-history-system)
7. [Data Management & Persistence](#data-management--persistence)
8. [Security & Performance Features](#security--performance-features)
9. [Synopsis & Future Directions](#synopsis--future-directions)

---

## Introduction & Architecture Overview

### What is This System?

The **grading-agent** is a sophisticated multi-agent AI system built on Azure OpenAI, LangChain, and LangGraph. It demonstrates how to build production-ready AI applications with:

- **Multiple Specialized Agents**: Different AI personalities optimized for specific tasks
- **Intelligent Task Routing**: Automatic classification and delegation using LLM reasoning
- **Conversation Memory**: Shared context across agents with 20-message rolling window
- **Enterprise Features**: Rate limiting, caching, monitoring, and security validation

### Core Philosophy: Orchestration Over Monolithic Design

Traditional AI applications use a single model for everything. This system takes a different approach:

```
Single Model Approach:          Multi-Agent Orchestration:
┌─────────────────┐            ┌──────────────────────────┐
│   One LLM       │            │   Master Orchestrator    │
│  (Jack of All   │            └──────────┬───────────────┘
│   Trades)       │                      │
└─────────────────┘                      │ Routes to:
                                         │
                       ┌─────────────────┼─────────────────┐
                       │                 │                 │
                  ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
                  │  Chat   │      │Analysis │      │ Grading │
                  │  Agent  │      │  Agent  │      │  Agent  │
                  └─────────┘      └─────────┘      └─────────┘
```

**Why This Matters:**
- **Specialization**: Each agent has optimized system prompts for their domain
- **Scalability**: Add new capabilities without retraining models
- **Maintainability**: Update one agent without affecting others
- **Cost Control**: Use different models/temperatures per task type
- **Flexibility**: Mix synchronous and asynchronous processing as needed

### The LangGraph Workflow Engine

At the heart of this system is **LangGraph**, a library for building stateful, multi-step LLM applications as directed graphs.

**Traditional Approach (Sequential):**
```python
# Linear processing - inflexible and hard to debug
def process_request(user_input):
    response = llm.invoke(user_input)
    store_data(response)
    return response
```

**LangGraph Approach (Graph-Based):**
```python
# Conditional routing, error handling, observability
from langgraph.graph import StateGraph, END

workflow = StateGraph(MasterAgentState)
workflow.add_node("classify", classify_task)
workflow.add_node("route", route_to_agent)
workflow.add_node("synthesize", synthesize_response)

# Conditional edges based on state
workflow.add_conditional_edges(
    "classify", 
    should_continue,
    {"route": "route", "error": "handle_error"}
)

workflow.add_edge("route", "synthesize")
workflow.add_edge("synthesize", END)

compiled_graph = workflow.compile()
```

**Key Benefits:**
- **Conditional Logic**: Different paths based on classification results
- **Error Recovery**: Handle failures gracefully with dedicated error nodes
- **Observability**: Track state transitions through the entire graph
- **Testability**: Test individual nodes in isolation
- **Complexity Management**: Complex workflows remain readable and maintainable

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│                    (CLI Interface)                          │
│  Commands: status, stats, health, history, clear-history   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   MasterAgent                               │
│              (Orchestrator + LangGraph)                     │
│                                                             │
│  LangGraph Workflow:                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Classify    │→ │   Route to   │→ │  Manage Data │    │
│  │    Task      │  │    Agent     │  │  & Synthesize│    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  Security Layer: InputValidator, RateLimiter               │
│  Performance: ResponseCache, TokenOptimizer                │
└────────┬────────────────────┬──────────────────────────────┘
         │                    │
         │                    ▼
         │        ┌──────────────────────┐
         │        │  ConversationHistory │
         │        │   (20-msg Rolling    │
         │        │    Window + Persist) │
         │        └──────────────────────┘
         │
         ├──────────────┬──────────────┬──────────────┐
         ▼              ▼              ▼              ▼
    ┌────────┐    ┌─────────┐    ┌─────────┐   ┌──────────┐
    │  Chat  │    │Analysis │    │ Grading │   │   Data   │
    │  Agent │    │  Agent  │    │  Agent  │   │ Manager  │
    │        │    │         │    │         │   │          │
    │ Temp:  │    │ Temp:   │    │ Temp:   │   │ JSONL    │
    │  1.0   │    │  1.0    │    │  1.0    │   │ Storage  │
    └────────┘    └─────────┘    └─────────┘   └──────────┘
```

### Technology Stack

**Core Dependencies:**
- **Azure OpenAI**: GPT-4 models for LLM capabilities
- **LangChain**: Framework for LLM applications
- **LangGraph**: State machine and workflow orchestration
- **Python 3.8+**: Modern Python with type hints

**Key Libraries:**
```python
# requirements.txt
langchain-openai>=0.0.2
langgraph>=0.0.20
python-dotenv>=1.0.0
pydantic>=2.0.0
```

### Configuration Management

The system uses environment variables for configuration:

```python
# .env file
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Agent settings
AGENT_TEMPERATURE=1.0
MAX_CONVERSATION_MESSAGES=20

# Performance settings
ENABLE_RESPONSE_CACHE=true
CACHE_TTL=300
CACHE_MAX_SIZE=100

# Security settings
RATE_LIMIT_ENABLED=true
RATE_LIMIT_CALLS=10
RATE_LIMIT_PERIOD=60
MAX_INPUT_LENGTH=10000
```

**Configuration Class Pattern:**

```python
# modules/config.py
class AzureOpenAIConfig:
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.agent_temperature = float(os.getenv("AGENT_TEMPERATURE", "1.0"))
        
        # Validate on initialization
        self._validate_config()
    
    def get_azure_openai_kwargs(self) -> dict:
        """Get kwargs for LLM initialization."""
        return {
            "azure_endpoint": self.endpoint,
            "api_key": self.api_key,
            "api_version": self.api_version,
            "azure_deployment": self.chat_deployment,
        }

# Global config instance
config = AzureOpenAIConfig()
```

### Data Flow Example

Let's trace a complete request through the system:

```
1. User Input
   └─> "Can you analyze this sales data?"

2. Main.py receives input
   └─> Calls MasterAgent.chat(user_input)

3. Security Layer
   ├─> InputValidator.validate_input() ✓
   ├─> RateLimiter.check_rate_limit() ✓
   └─> ResponseCache.get() → Cache miss

4. Add to Conversation History
   └─> ConversationHistory.add_user_message()

5. LangGraph Workflow Begins
   │
   ├─> Node: classify_task
   │   ├─> LLM call: "Classify this request..."
   │   └─> Result: task_type = "analysis"
   │
   ├─> Conditional Edge: should_continue? → "route"
   │
   ├─> Node: route_to_agent
   │   ├─> Select: AnalysisAgent
   │   ├─> Call: process_with_history(input, history)
   │   │   ├─> Get last 20 messages from history
   │   │   ├─> Combine: [system] + [history] + [user_input]
   │   │   └─> LLM call with full context
   │   └─> Response: "To analyze sales data..."
   │
   ├─> Node: manage_data
   │   └─> DataManager.store_interaction()
   │
   └─> Node: synthesize_response
       └─> Return final response

6. Post-Processing
   ├─> ConversationHistory.add_assistant_message()
   ├─> ResponseCache.set()
   └─> Metrics recorded

7. Return to User
   └─> Display response in CLI
```

This architecture provides:
- **Separation of concerns**: Each component has a single responsibility
- **Extensibility**: Easy to add new agents or tools
- **Observability**: Track requests through the entire pipeline
- **Reliability**: Error handling at each layer

---

## Understanding the Agent System

### The MasterAgent: Orchestrator Pattern

The `MasterAgent` class is the central coordinator that:
1. Receives all user requests
2. Classifies tasks using LLM reasoning
3. Routes to appropriate specialized agents
4. Manages conversation history
5. Handles data persistence
6. Coordinates security and performance layers

**Core Implementation:**

```python
# modules/master_agent.py
class MasterAgent:
    def __init__(self):
        # Initialize LLM for classification
        self.llm = AzureChatOpenAI(**config.get_azure_openai_kwargs())
        
        # Create LangGraph workflow
        self.graph = self._create_graph()
        
        # Initialize specialized agents
        self.specialized_agents = {
            "chat": ChatAgent(),
            "analysis": AnalysisAgent(),
            "grading": GradingAgent()
        }
        
        # Initialize supporting systems
        self.conversation_history = ConversationHistory(max_messages=20)
        self.data_manager = DataManager()
        self.input_validator = InputValidator()
        self.rate_limiter = RateLimiter()
        self.response_cache = ResponseCache()
```

**The State Object:**

LangGraph workflows operate on a shared state object that flows through all nodes:

```python
class MasterAgentState(TypedDict):
    """State passed through the LangGraph workflow."""
    messages: list                  # Message history for LLM
    user_input: str                 # Current user request
    response: str                   # Final response to return
    error: str                      # Error message if any
    agent_type: str                 # Selected agent (chat/analysis/grading)
    task_classification: str        # Classification result
    agent_responses: dict           # Responses from specialized agents
    data_context: dict              # Retrieved context from data manager
    conversation_history: list      # Full conversation context
```

**Each node in the workflow can:**
- Read from the state
- Modify the state
- Trigger conditional routing based on state values

### Specialized Agents: The Worker Pattern

Each specialized agent follows a consistent pattern:

```python
# modules/agents/analysis_agent.py
class AnalysisAgent:
    """Specialized agent for data analysis tasks."""
    
    def __init__(self):
        # Each agent gets its own LLM instance
        self.llm = self._create_llm()
        self.agent_type = "analysis"
    
    def _create_llm(self) -> AzureChatOpenAI:
        """Create LLM with agent-specific config."""
        return AzureChatOpenAI(
            **config.get_azure_openai_kwargs(),
            temperature=config.agent_temperature,  # Can be customized per agent
        )
    
    def process(self, user_input: str) -> str:
        """Basic processing without conversation history."""
        system_message = """You are a specialized data analysis AI.
        You excel at statistical analysis, data interpretation,
        and computational tasks."""
        
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=user_input)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def process_with_history(self, user_input: str, 
                            conversation_history: ConversationHistory) -> str:
        """Process with full conversation context."""
        system_message = """You are a specialized data analysis AI.
        You have access to conversation history, so you can reference
        previous analyses and maintain context."""
        
        # Get history formatted for LangChain
        history_messages = conversation_history.get_langchain_messages()
        
        # Build complete message list
        all_messages = [
            SystemMessage(content=system_message),
            *history_messages,
            HumanMessage(content=user_input)
        ]
        
        response = self.llm.invoke(all_messages)
        return response.content
    
    def get_status(self) -> str:
        """Health check endpoint."""
        return "active"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Describe agent capabilities."""
        return {
            "agent_type": self.agent_type,
            "capabilities": [
                "Data analysis and interpretation",
                "Statistical analysis",
                "Pattern recognition"
            ],
            "supports_history": True,
            "temperature": config.agent_temperature
        }
```

**Key Design Decisions:**

1. **Separate LLM Instances**: Each agent has its own LLM to allow different configurations
2. **Dual Methods**: `process()` and `process_with_history()` for backward compatibility
3. **System Prompts**: Each agent has a specialized system prompt defining its expertise
4. **Type Checking**: Uses `TYPE_CHECKING` to avoid circular imports with ConversationHistory

### Agent Comparison

| Feature | ChatAgent | AnalysisAgent | GradingAgent |
|---------|-----------|---------------|--------------|
| **Purpose** | General conversation | Data analysis | Educational assessment |
| **Temperature** | 1.0 (creative) | 1.0 (balanced) | 1.0 (balanced) |
| **System Prompt Focus** | Helpful, friendly | Statistical, methodical | Fair, constructive |
| **Typical Use Cases** | Q&A, explanations | Data processing | Assignment grading |
| **Conversation History** | ✓ Supported | ✓ Supported | ✓ Supported |

### The LangGraph Workflow in Detail

The MasterAgent uses a LangGraph workflow with these nodes:

**Node 1: classify_task**
```python
def _classify_task(self, state: MasterAgentState) -> MasterAgentState:
    """Use LLM to classify the user's request."""
    user_input = state["user_input"]
    
    classification_prompt = """
    Classify the following user request:
    - chat: General conversation
    - analysis: Data analysis or computational tasks
    - grading: Educational assessment
    
    User request: "{user_input}"
    
    Respond with only the category name.
    """
    
    # Call LLM
    messages = [
        SystemMessage(content="You are a task classifier."),
        HumanMessage(content=classification_prompt)
    ]
    response = self.llm.invoke(messages)
    
    # Update state
    task_type = response.content.strip().lower()
    state["task_classification"] = task_type
    state["agent_type"] = task_type
    
    return state
```

**Why LLM Classification?**
- **Flexible**: No need for rule-based logic or regex patterns
- **Contextual**: Understands intent, not just keywords
- **Extensible**: Add new categories without rewriting logic
- **Natural**: Handles ambiguous or complex requests

**Node 2: route_to_agent**
```python
def _route_to_agent(self, state: MasterAgentState) -> MasterAgentState:
    """Route to the appropriate specialized agent."""
    agent_type = state["agent_type"]
    user_input = state["user_input"]
    
    if agent_type in self.specialized_agents:
        agent = self.specialized_agents[agent_type]
        
        # Check if agent supports conversation history
        if hasattr(agent, 'process_with_history'):
            response = agent.process_with_history(
                user_input,
                self.conversation_history
            )
        else:
            # Fallback for agents without history support
            response = agent.process(user_input)
        
        state["agent_responses"] = {agent_type: response}
    else:
        # Fallback to master agent if no specialized agent
        state["agent_responses"] = {"master": "Agent not found"}
    
    return state
```

**Node 3: manage_data**
```python
def _manage_data(self, state: MasterAgentState) -> MasterAgentState:
    """Store interaction and retrieve relevant context."""
    if self.data_manager:
        # Store this interaction
        interaction_data = {
            "user_input": state["user_input"],
            "task_type": state["task_classification"],
            "agent_responses": state["agent_responses"],
            "timestamp": datetime.now().isoformat()
        }
        self.data_manager.store_interaction(interaction_data)
        
        # Get relevant past context
        context = self.data_manager.get_relevant_context(state["user_input"])
        state["data_context"] = context
    
    return state
```

**Node 4: synthesize_response**
```python
def _synthesize_response(self, state: MasterAgentState) -> MasterAgentState:
    """Create final response from agent output and context."""
    agent_responses = state["agent_responses"]
    
    # Get primary agent response
    primary_response = list(agent_responses.values())[0]
    
    # Optionally enhance with context
    data_context = state.get("data_context", {})
    if data_context.get("relevant_interactions"):
        context_note = f"\n[Based on {len(data_context['relevant_interactions'])} previous interactions]"
        primary_response += context_note
    
    state["response"] = primary_response
    return state
```

**Conditional Edges:**

These determine the flow between nodes:

```python
def _should_continue_classification(self, state: MasterAgentState) -> str:
    """Decide next step after classification."""
    if state.get("error"):
        return "error"
    return "route"

def _should_manage_data(self, state: MasterAgentState) -> str:
    """Decide if we need data management."""
    if state.get("error"):
        return "error"
    if self.data_manager:
        return "data"
    return "synthesize"
```

**Complete Workflow Graph:**

```
START
  ↓
classify_task
  ↓
  ├──[error?]──→ handle_error → END
  │
  └──[success]──→ route_to_agent
                      ↓
                      ├──[error?]──→ handle_error → END
                      │
                      └──[success]──→ manage_data
                                          ↓
                                      synthesize_response
                                          ↓
                                        END
```

---

## How Agents Work

### Complete Request Lifecycle

Let's trace a complete user request through the system step-by-step:

**Example: "Can you analyze sales data from Q4?"**

#### Step 1: User Input & Security

```python
# User enters request in main.py CLI
user_input = "Can you analyze sales data from Q4?"

# Call master agent
response = master_agent.chat(user_input)
```

#### Step 2: Input Validation

```python
# Security Layer: InputValidator
validation_result = self.input_validator.validate_input(user_input)
# Checks: not empty, length < 10000, no malicious patterns

# Sanitize input
user_input = self.input_validator.sanitize_input(user_input)
# Removes null bytes, normalizes whitespace
```

#### Step 3: Rate Limiting

```python
# Check rate limit (default: 10 requests per 60 seconds)
rate_check = self.rate_limiter.check_rate_limit(session_id="default")
if not rate_check["allowed"]:
    raise RateLimitException(f"Try again in {rate_check['retry_after']}s")
```

#### Step 4: Cache Check

```python
# Check if we've seen this exact request recently
cache_context = str(len(self.conversation_history))  # Context key
cached_response = self.response_cache.get(user_input, cache_context)
if cached_response:
    return cached_response  # Skip processing, return cached
```

#### Step 5: Add to Conversation History

```python
# Add user message to rolling window
self.conversation_history.add_user_message(user_input)
# Now history contains: [...previous 19 messages, user_input]
```

#### Step 6: LangGraph Workflow Execution

```python
# Initialize state
initial_state = {
    "messages": [],
    "user_input": "Can you analyze sales data from Q4?",
    "response": "",
    "error": "",
    "agent_type": "",
    "task_classification": "",
    "agent_responses": {},
    "data_context": {},
    "conversation_history": self.conversation_history.get_messages_for_llm()
}

# Execute workflow
result = self.graph.invoke(initial_state)
```

**Inside the Workflow:**

```python
# Node 1: classify_task
# LLM receives:
"""
System: You are a task classifier.
User: Classify this request: "Can you analyze sales data from Q4?"
      Categories: chat, analysis, grading
"""
# LLM responds: "analysis"
state["task_classification"] = "analysis"

# Conditional edge: should_continue_classification
# No error detected → route to "route_to_agent"

# Node 2: route_to_agent
agent = self.specialized_agents["analysis"]  # Get AnalysisAgent
response = agent.process_with_history(user_input, conversation_history)

# Inside AnalysisAgent.process_with_history():
history_messages = conversation_history.get_langchain_messages()
# Returns: [HumanMessage("previous input"), AIMessage("previous response"), ...]

all_messages = [
    SystemMessage("You are a data analysis AI..."),
    *history_messages,  # Last 20 messages
    HumanMessage("Can you analyze sales data from Q4?")
]

response = self.llm.invoke(all_messages)
# LLM sees full context and responds appropriately

state["agent_responses"] = {"analysis": response.content}

# Node 3: manage_data
# Store interaction
self.data_manager.store_interaction({
    "user_input": "Can you analyze sales data from Q4?",
    "task_type": "analysis",
    "agent_responses": state["agent_responses"],
    "timestamp": "2025-10-01T09:20:00"
})
# Saved to data/interactions.jsonl

# Node 4: synthesize_response
state["response"] = state["agent_responses"]["analysis"]
```

#### Step 7: Post-Processing

```python
# Cache the response
self.response_cache.set(user_input, response, cache_context)

# Add assistant response to history
self.conversation_history.add_assistant_message(
    response,
    agent_type="analysis"
)

# Record metrics
response_time = time.time() - start_time
self.monitor.log_request("analysis", response_time, success=True)
```

#### Step 8: Return to User

```python
# Display in CLI
print(f"🤖 Master Assistant: {response}")
```

**Key Insights:**
- **Multiple LLM calls**: One for classification, one for the actual response
- **Context propagation**: History flows through all stages
- **Stateful processing**: State object tracks everything
- **Layered architecture**: Security → Cache → Processing → Storage → Return

---

## Adding New Agents

### Step-by-Step Guide: Creating a CodeReviewAgent

Let's create a complete new agent from scratch. We'll build a **CodeReviewAgent** that specializes in reviewing code for bugs, security issues, and best practices.

#### Step 1: Create the Agent File

Create `modules/agents/code_review_agent.py`:

```python
"""
Code Review Agent - Specialized for code review and quality analysis.
"""
from typing import Dict, Any, TYPE_CHECKING
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..config import config
import logging

if TYPE_CHECKING:
    from ..conversation_history import ConversationHistory

logger = logging.getLogger(__name__)

class CodeReviewAgent:
    """Specialized agent for code review and quality analysis."""
    
    def __init__(self):
        """Initialize the code review agent."""
        self.llm = self._create_llm()
        self.agent_type = "code_review"
        logger.info("Code Review Agent initialized")
    
    def _create_llm(self) -> AzureChatOpenAI:
        """Create Azure OpenAI LLM instance for code review.
        
        Note: Lower temperature for more consistent reviews.
        """
        return AzureChatOpenAI(
            **config.get_azure_openai_kwargs(),
            temperature=0.3,  # Lower for deterministic reviews
        )
    
    def process(self, user_input: str) -> str:
        """Process code review requests without history.
        
        Args:
            user_input: User's request containing code to review
            
        Returns:
            Code review feedback and recommendations
        """
        try:
            system_message = """You are a specialized code review AI assistant.
            
            Your expertise includes:
            - Identifying bugs and logic errors
            - Detecting security vulnerabilities (SQL injection, XSS, etc.)
            - Suggesting performance optimizations
            - Enforcing best practices and design patterns
            - Improving code readability and maintainability
            - Checking for proper error handling
            
            When reviewing code:
            1. Be specific - point to exact lines or patterns
            2. Be constructive - explain WHY changes improve the code
            3. Prioritize issues by severity (critical, important, minor)
            4. Provide code examples for suggested fixes
            5. Consider the broader context and architecture
            
            Always be professional and educational in your feedback."""
            
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            logger.info("Code review agent processed request successfully")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in code review agent: {e}")
            return f"I apologize, but I encountered an error during code review: {str(e)}"
    
    def process_with_history(self, user_input: str, 
                            conversation_history: 'ConversationHistory') -> str:
        """Process code review requests with conversation history.
        
        Args:
            user_input: User's request
            conversation_history: Shared conversation history
            
        Returns:
            Code review with context awareness
        """
        try:
            system_message = """You are a specialized code review AI assistant.
            
            Your expertise includes:
            - Identifying bugs and logic errors
            - Detecting security vulnerabilities
            - Suggesting performance optimizations
            - Enforcing best practices and design patterns
            
            You have access to conversation history, which allows you to:
            - Reference previously reviewed code
            - Track improvements over time
            - Maintain consistent coding standards
            - Build on earlier feedback
            
            Use this context to provide more coherent and personalized reviews."""
            
            # Get conversation history messages
            history_messages = conversation_history.get_langchain_messages()
            
            # Create current message set
            current_messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_input)
            ]
            
            # Combine: system prompt + history + current input
            all_messages = [current_messages[0]] + history_messages + [current_messages[1]]
            
            response = self.llm.invoke(all_messages)
            logger.info("Code review agent processed with history successfully")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in code review agent with history: {e}")
            return f"I apologize, but I encountered an error during code review: {str(e)}"
    
    def get_status(self) -> str:
        """Get the status of the code review agent.
        
        Returns:
            Status string ("active" if operational)
        """
        return "active"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the code review agent.
        
        Returns:
            Dictionary describing agent capabilities
        """
        return {
            "agent_type": self.agent_type,
            "capabilities": [
                "Bug detection and logic error identification",
                "Security vulnerability analysis",
                "Performance optimization suggestions",
                "Best practices enforcement",
                "Code readability improvements",
                "Design pattern recommendations",
                "Error handling review",
                "Conversation history for consistent reviews"
            ],
            "specialization": "Code review and quality analysis with context awareness",
            "temperature": 0.3,
            "supports_history": True
        }
```

**Key Implementation Details:**

1. **Temperature**: Set to `0.3` for consistent, deterministic reviews
2. **System Prompt**: Detailed instructions with specific review criteria
3. **Error Handling**: Wrapped in try-except with proper logging
4. **TYPE_CHECKING**: Avoids circular import issues
5. **Documentation**: Comprehensive docstrings for all methods

#### Step 2: Register the Agent with MasterAgent

Edit `modules/master_agent.py` in the `_initialize_agents()` method:

```python
def _initialize_agents(self):
    """Initialize specialized agents."""
    try:
        # Import existing agents
        from .agents.chat_agent import ChatAgent
        from .agents.analysis_agent import AnalysisAgent
        from .agents.grading_agent import GradingAgent
        
        # Import your new agent
        from .agents.code_review_agent import CodeReviewAgent
        
        from .data_manager import DataManager
        
        # Register all agents
        self.specialized_agents = {
            "chat": ChatAgent(),
            "analysis": AnalysisAgent(),
            "grading": GradingAgent(),
            "code_review": CodeReviewAgent(),  # ← Add your agent here
        }
        
        self.data_manager = DataManager()
        logger.info("Specialized agents and data manager initialized successfully")
        
    except ImportError as e:
        logger.warning(f"Some specialized agents not available: {e}")
        self.specialized_agents = {}
        logger.info("Running with basic master agent only")
```

#### Step 3: Update Task Classification

Edit the `_classify_task()` method in `modules/master_agent.py`:

```python
def _classify_task(self, state: MasterAgentState) -> MasterAgentState:
    """Classify the user's task to determine which agent to use."""
    try:
        user_input = state.get("user_input", "")
        if not user_input.strip():
            state["error"] = "Empty input provided"
            return state
        
        # Updated classification prompt with new category
        classification_prompt = f"""
        Classify the following user request into one of these categories:
        - chat: General conversation, questions, or assistance
        - analysis: Data analysis, file processing, or computational tasks
        - grading: Educational assessment, grading, or evaluation tasks
        - code_review: Code review, refactoring, or code quality analysis
        
        User request: "{user_input}"
        
        Respond with only the category name (chat, analysis, grading, or code_review).
        """
        
        messages = [
            {"role": "system", "content": "You are a task classifier. Respond with only the category name."},
            {"role": "user", "content": classification_prompt}
        ]
        
        # Convert to LangChain message format
        from langchain_core.messages import HumanMessage, SystemMessage
        langchain_messages = [
            SystemMessage(content=messages[0]["content"]),
            HumanMessage(content=messages[1]["content"])
        ]
        
        response = self.llm.invoke(langchain_messages)
        task_type = response.content.strip().lower()
        
        # Updated valid types
        valid_types = ["chat", "analysis", "grading", "code_review"]
        if task_type not in valid_types:
            task_type = "chat"  # Default fallback
        
        state["task_classification"] = task_type
        state["agent_type"] = task_type
        state["messages"] = [
            {"role": "system", "content": f"You are handling a {task_type} task."},
            {"role": "user", "content": user_input}
        ]
        
        logger.info(f"Task classified as: {task_type}")
        return state
        
    except Exception as e:
        state["error"] = f"Error classifying task: {str(e)}"
        logger.error(f"Error in _classify_task: {e}")
        return state
```

#### Step 4: Create Tests

Create `tests/test_code_review_agent.py`:

```python
"""
Tests for Code Review Agent.
"""
import pytest
from modules.agents.code_review_agent import CodeReviewAgent
from modules.conversation_history import ConversationHistory

def test_code_review_agent_initialization():
    """Test that agent initializes correctly."""
    agent = CodeReviewAgent()
    assert agent.agent_type == "code_review"
    assert agent.get_status() == "active"
    assert agent.llm is not None

def test_code_review_basic_process():
    """Test basic processing without history."""
    agent = CodeReviewAgent()
    
    code_to_review = """
    def calculate_total(prices):
        total = 0
        for price in prices:
            total = total + price
        return total
    """
    
    user_input = f"Please review this Python function:\n{code_to_review}"
    response = agent.process(user_input)
    
    assert response
    assert isinstance(response, str)
    assert len(response) > 0

def test_code_review_with_history():
    """Test processing with conversation history."""
    agent = CodeReviewAgent()
    history = ConversationHistory(max_messages=5)
    
    # Add some context
    history.add_user_message("Review my authentication function")
    history.add_assistant_message(
        "I've reviewed your authentication function. Consider adding rate limiting.",
        "code_review"
    )
    
    # New request that references history
    response = agent.process_with_history(
        "Can you elaborate on the rate limiting suggestion?",
        history
    )
    
    assert response
    assert isinstance(response, str)

def test_get_capabilities():
    """Test capabilities reporting."""
    agent = CodeReviewAgent()
    capabilities = agent.get_capabilities()
    
    assert capabilities["agent_type"] == "code_review"
    assert "capabilities" in capabilities
    assert len(capabilities["capabilities"]) > 0
    assert capabilities["supports_history"] == True
    assert capabilities["temperature"] == 0.3

def test_error_handling():
    """Test that errors are handled gracefully."""
    agent = CodeReviewAgent()
    # This should not crash even with unusual input
    response = agent.process("")
    assert isinstance(response, str)
```

#### Step 5: Run and Test

```bash
# Run unit tests
pytest tests/test_code_review_agent.py -v

# Run all tests to ensure no regression
pytest -v

# Test interactively
python main.py

# In the chat interface:
You: Please review this code: def add(a,b): return a+b

# Should classify as "code_review" and route to CodeReviewAgent
# Response will include code review feedback
```

### Agent Design Best Practices

#### 1. Temperature Settings by Use Case

```python
# Creative/Conversational Tasks
temperature=1.0   # ChatAgent, creative writing

# Balanced Tasks
temperature=0.7   # General purpose, mixed tasks

# Analytical/Deterministic Tasks
temperature=0.3   # CodeReviewAgent, grading, analysis
temperature=0.1   # Highly consistent outputs needed
```

#### 2. System Prompt Engineering

**Good System Prompt Structure:**

```python
system_prompt = """You are a [role/identity].

Your expertise includes:
- [Capability 1]
- [Capability 2]
- [Capability 3]

When [performing task]:
1. [Step or principle 1]
2. [Step or principle 2]
3. [Step or principle 3]

[Additional context about conversation history if applicable]

[Tone/style guidelines]
"""
```

**Example - Effective vs Ineffective:**

❌ **Ineffective:**
```python
"You help with code."
```

✅ **Effective:**
```python
"""You are a specialized code review AI assistant with expertise in
security vulnerabilities, performance optimization, and best practices.

When reviewing code:
1. Prioritize security issues first
2. Explain WHY each suggestion improves the code
3. Provide specific code examples for fixes
4. Consider maintainability and readability

Be constructive and educational in your feedback."""
```

#### 3. Error Handling Pattern

Always follow this pattern:

```python
def process(self, user_input: str) -> str:
    try:
        # Main logic here
        response = self.llm.invoke(messages)
        logger.info(f"{self.agent_type} processed successfully")
        return response.content
        
    except Exception as e:
        # Log the error
        logger.error(f"Error in {self.agent_type}: {e}")
        
        # Return user-friendly message
        return f"I apologize, error occurred: {str(e)}"
```

#### 4. Logging Best Practices

```python
# At agent initialization
logger.info(f"{self.agent_type} Agent initialized")

# Before processing
logger.debug(f"Processing request: {user_input[:50]}...")

# After successful processing
logger.info(f"{self.agent_type} processed successfully")

# On errors
logger.error(f"Error in {self.agent_type}: {e}", exc_info=True)

# Performance tracking
logger.debug(f"Response generated in {elapsed_time:.2f}s")
```

#### 5. Type Hints and Documentation

```python
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..conversation_history import ConversationHistory

def process_with_history(
    self, 
    user_input: str, 
    conversation_history: 'ConversationHistory'
) -> str:
    """Process with conversation history context.
    
    Args:
        user_input: The user's request
        conversation_history: Shared conversation history object
        
    Returns:
        Agent's response as string
        
    Raises:
        Exception: If LLM invocation fails
    """
    pass
```

### Testing Your Agent

#### Unit Test Checklist:
- ✅ Agent initializes correctly
- ✅ `process()` returns valid response
- ✅ `process_with_history()` works with history
- ✅ `get_status()` returns "active"
- ✅ `get_capabilities()` returns correct info
- ✅ Error handling works gracefully
- ✅ Temperature is set correctly
- ✅ System prompt is appropriate

#### Integration Test Checklist:
- ✅ Master agent can route to new agent
- ✅ Classification works for agent's domain
- ✅ Conversation history flows correctly
- ✅ Data manager stores interactions
- ✅ Metrics are recorded
- ✅ No regression in existing agents

---

## Tools & Utilities You Can Add

### Overview

The system is designed for extensibility through tools and utilities. Tools can be:
- **External API integrations** (weather, databases, file systems)
- **Processing utilities** (data transformation, file handling)
- **Memory systems** (vector databases, RAG)
- **Monitoring tools** (analytics, metrics, alerts)

### 1. External API Integration Tool

Create agents that interact with external services:

```python
# modules/tools/weather_tool.py
import requests
from typing import Dict, Any

class WeatherTool:
    """Tool for fetching weather data."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.weatherapi.com/v1"
    
    def get_weather(self, location: str) -> Dict[str, Any]:
        """Fetch weather data for a location."""
        url = f"{self.base_url}/current.json"
        params = {"key": self.api_key, "q": location}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def format_weather_response(self, weather_data: Dict[str, Any]) -> str:
        """Format weather data for user display."""
        current = weather_data["current"]
        location = weather_data["location"]
        
        return f"""Weather in {location['name']}, {location['country']}:
        Temperature: {current['temp_c']}°C / {current['temp_f']}°F
        Condition: {current['condition']['text']}
        Humidity: {current['humidity']}%
        Wind: {current['wind_kph']} km/h"""

# Usage in an agent:
def process_weather_request(self, location: str) -> str:
    weather_tool = WeatherTool(config.weather_api_key)
    data = weather_tool.get_weather(location)
    return weather_tool.format_weather_response(data)
```

### 2. Database Query Tool

SQL generation and execution with safety checks:

```python
# modules/tools/database_tool.py
import sqlite3
from typing import List, Dict, Any

class DatabaseTool:
    """Tool for natural language database queries."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.llm = AzureChatOpenAI(**config.get_azure_openai_kwargs())
    
    def text_to_sql(self, question: str, schema: str) -> str:
        """Convert natural language to SQL."""
        prompt = f"""Given this database schema:
        {schema}
        
        Convert this question to SQL:
        {question}
        
        Return only the SQL query."""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    
    def is_safe_query(self, sql: str) -> bool:
        """Validate SQL for safety."""
        dangerous = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT']
        sql_upper = sql.upper()
        
        for keyword in dangerous:
            if keyword in sql_upper:
                return False
        
        return True
    
    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute safe SELECT queries."""
        if not self.is_safe_query(sql):
            raise ValueError("Unsafe query detected")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
```

### 3. File Processing Tool

Handle various file formats with LLM assistance:

```python
# modules/tools/file_processor.py
import pandas as pd
from pathlib import Path

class FileProcessorTool:
    """Tool for intelligent file processing."""
    
    SUPPORTED_FORMATS = {
        '.csv': 'process_csv',
        '.json': 'process_json',
        '.txt': 'process_text'
    }
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process file and extract relevant data."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        processor_method = self.SUPPORTED_FORMATS.get(path.suffix)
        if not processor_method:
            raise ValueError(f"Unsupported format: {path.suffix}")
        
        return getattr(self, processor_method)(path)
    
    def process_csv(self, path: Path) -> Dict[str, Any]:
        """Extract data and statistics from CSV."""
        df = pd.read_csv(path)
        return {
            "type": "csv",
            "rows": len(df),
            "columns": list(df.columns),
            "sample": df.head(5).to_dict(),
            "stats": df.describe().to_dict()
        }
```

---

## Conversation History System

### The ConversationHistory Class

**Purpose**: Maintains a rolling window of recent messages shared across all agents.

**Key Features**:
- **Rolling Window**: Keeps last 20 messages (configurable)
- **Agent Attribution**: Tracks which agent generated each response
- **Persistence**: Saves to `data/conversation_history.json`
- **Cross-Session**: Restores on startup
- **LangChain Integration**: Formats messages for LLM consumption

**Core Implementation**:

```python
# modules/conversation_history.py
class ConversationHistory:
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: List[ChatMessage] = []
    
    def add_user_message(self, content: str):
        """Add user message to history."""
        message = ChatMessage(
            role="user",
            content=content,
            timestamp=datetime.now()
        )
        self._add_message(message)
    
    def add_assistant_message(self, content: str, agent_type: str):
        """Add assistant message with agent attribution."""
        message = ChatMessage(
            role="assistant",
            content=content,
            timestamp=datetime.now(),
            agent_type=agent_type
        )
        self._add_message(message)
    
    def _add_message(self, message: ChatMessage):
        """Add message and maintain rolling window."""
        self.messages.append(message)
        
        # Keep only last N messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_langchain_messages(self):
        """Get messages formatted for LangChain."""
        from langchain_core.messages import HumanMessage, AIMessage
        
        langchain_messages = []
        for message in self.messages:
            content = message.content
            
            # Add agent context for assistant messages
            if message.role == "assistant" and message.agent_type:
                content = f"[{message.agent_type} agent]: {content}"
            
            if message.role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif message.role == "assistant":
                langchain_messages.append(AIMessage(content=content))
        
        return langchain_messages
```

**Usage in Agents**:

```python
def process_with_history(self, user_input: str, conversation_history):
    # Get last 20 messages
    history_messages = conversation_history.get_langchain_messages()
    
    # Build complete message list
    all_messages = [
        SystemMessage(content=self.system_prompt),
        *history_messages,
        HumanMessage(content=user_input)
    ]
    
    # LLM sees full context
    response = self.llm.invoke(all_messages)
    return response.content
```

---

## Data Management & Persistence

### The DataManager Class

**Purpose**: Persistent storage of interactions and context retrieval.

**Storage Format**: JSONL (JSON Lines) in `data/interactions.jsonl`

**Each Interaction Contains**:
```json
{
  "id": "unique-uuid",
  "user_input": "User's request",
  "task_type": "chat/analysis/grading",
  "agent_responses": {"agent_type": "response"},
  "timestamp": "2025-10-01T09:20:00",
  "stored_at": "2025-10-01T09:20:01"
}
```

**Key Methods**:

```python
class DataManager:
    def store_interaction(self, interaction_data: Dict[str, Any]) -> bool:
        """Store interaction to JSONL file."""
        interaction_data["id"] = str(uuid4())
        interaction_data["stored_at"] = datetime.now().isoformat()
        
        with open(self.interactions_file, "a") as f:
            f.write(json.dumps(interaction_data) + "\n")
        
        return True
    
    def get_relevant_context(self, user_input: str) -> Dict[str, Any]:
        """Retrieve relevant past interactions."""
        keywords = user_input.lower().split()
        relevant = []
        
        for interaction in self.get_recent_interactions(50):
            text = interaction.get("user_input", "") + str(interaction.get("agent_responses", {}))
            score = sum(1 for kw in keywords if kw in text.lower())
            
            if score > 0:
                interaction["relevance_score"] = score
                relevant.append(interaction)
        
        relevant.sort(key=lambda x: x["relevance_score"], reverse=True)
        return {"relevant_interactions": relevant[:5]}
```

---

## Security & Performance Features

### Security Components

#### 1. InputValidator

**Purpose**: Validate and sanitize user input

```python
class InputValidator:
    @staticmethod
    def validate_input(user_input: str) -> Dict[str, Any]:
        """Validate user input for security."""
        # Check length
        if len(user_input) > config.max_input_length:
            return {"valid": False, "error": "Input too long"}
        
        # Check for suspicious patterns
        suspicious = [
            r'<script[^>]*>.*?</script>',  # XSS
            r'javascript:',
            r'on\w+\s*='  # Event handlers
        ]
        
        for pattern in suspicious:
            if re.search(pattern, user_input, re.IGNORECASE):
                return {"valid": False, "error": "Unsafe content"}
        
        return {"valid": True}
    
    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """Sanitize input by removing harmful content."""
        sanitized = user_input.strip()
        sanitized = sanitized.replace('\x00', '')
        sanitized = re.sub(r'\s+', ' ', sanitized)
        return sanitized
```

#### 2. RateLimiter

**Purpose**: Prevent abuse through rate limiting

```python
class RateLimiter:
    def __init__(self, max_calls: int = 10, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window  # seconds
        self.calls: Dict[str, list] = {}
    
    def check_rate_limit(self, identifier: str = "default") -> Dict[str, Any]:
        """Check if rate limit exceeded."""
        now = time.time()
        
        if identifier not in self.calls:
            self.calls[identifier] = []
        
        # Remove old calls outside window
        self.calls[identifier] = [
            t for t in self.calls[identifier]
            if t > now - self.time_window
        ]
        
        # Check limit
        if len(self.calls[identifier]) >= self.max_calls:
            oldest = min(self.calls[identifier])
            retry_after = int(self.time_window - (now - oldest))
            return {"allowed": False, "retry_after": retry_after}
        
        self.calls[identifier].append(now)
        return {"allowed": True, "retry_after": 0}
```

### Performance Components

#### 1. ResponseCache

**Purpose**: Cache responses to reduce duplicate LLM calls

```python
class ResponseCache:
    def __init__(self, max_size: int = 100, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl  # Time-to-live in seconds
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, float] = {}
    
    def get(self, user_input: str, context: str = None) -> Optional[str]:
        """Get cached response if not expired."""
        key = self._generate_key(user_input, context)
        
        if key in self.cache:
            timestamp = self.timestamps[key]
            if time.time() - timestamp < self.ttl:
                self.cache.move_to_end(key)  # LRU
                return self.cache[key]
            else:
                # Expired
                del self.cache[key]
                del self.timestamps[key]
        
        return None
```

#### 2. TokenOptimizer

**Purpose**: Estimate and optimize token usage

```python
class TokenOptimizer:
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough token estimation (4 chars ≈ 1 token)."""
        return len(text) // 4
    
    @staticmethod
    def get_optimized_history(messages: List[Dict], max_tokens: int = 2000):
        """Trim history to fit token budget."""
        optimized = []
        total_tokens = 0
        
        for message in reversed(messages):
            tokens = TokenOptimizer.estimate_tokens(message["content"])
            if total_tokens + tokens > max_tokens:
                break
            optimized.insert(0, message)
            total_tokens += tokens
        
        return optimized
```

---

## Synopsis & Future Directions

### What We've Built

The grading-agent system demonstrates a **production-ready multi-agent architecture** with:

**✅ Core Features:**
- Multi-agent orchestration with LangGraph
- Intelligent task classification and routing
- Shared conversation history across agents
- Persistent data storage and retrieval
- Security (validation, rate limiting)
- Performance (caching, token optimization)
- Comprehensive monitoring and health checks

**✅ Key Patterns:**
- **Orchestrator Pattern**: MasterAgent coordinates specialized agents
- **Worker Pattern**: Each agent has specific expertise
- **State Machine**: LangGraph manages complex workflows
- **Rolling Window**: Conversation history with configurable limits
- **Layered Architecture**: Security → Cache → Processing → Storage

### Future Enhancements

#### 1. Advanced Agent Capabilities
- **Tool-using agents**: Give agents ability to call functions/APIs
- **Multi-step reasoning**: Agents that break down complex tasks
- **Parallel agent execution**: Multiple agents working simultaneously
- **Agent collaboration**: Agents consulting each other

#### 2. Enhanced Memory Systems
- **Vector database integration**: Semantic search over past interactions
- **Long-term memory**: Persistent knowledge beyond rolling window
- **User profiles**: Remember preferences and context per user
- **Knowledge graphs**: Structure relationships between concepts

#### 3. Improved Monitoring
- **Real-time dashboards**: Visualize system performance
- **Alert systems**: Notify on errors or anomalies
- **A/B testing**: Compare agent configurations
- **Cost tracking**: Monitor Azure OpenAI token usage

#### 4. Production Features
- **API endpoints**: REST/GraphQL API for programmatic access
- **Authentication**: User management and access control
- **Deployment**: Docker containers, Kubernetes orchestration
- **Scaling**: Horizontal scaling for high traffic

#### 5. Agent Marketplace
- **Plugin system**: Hot-load agents without restart
- **Agent registry**: Discover and install community agents
- **Version management**: Handle agent updates
- **Testing framework**: Automated agent validation

### Building Your Next Agent: Quick Reference

1. **Create Agent File**: `modules/agents/your_agent.py`
2. **Implement Required Methods**: `__init__`, `process`, `process_with_history`
3. **Register in MasterAgent**: Add to `specialized_agents` dict
4. **Update Classification**: Add category to `_classify_task`
5. **Write Tests**: Create `tests/test_your_agent.py`
6. **Test**: Run `pytest` and interactive testing

**Agent Template**:
```python
class YourAgent:
    def __init__(self):
        self.llm = AzureChatOpenAI(...)
        self.agent_type = "your_type"
    
    def process(self, user_input: str) -> str:
        # Basic processing
        pass
    
    def process_with_history(self, user_input: str, history) -> str:
        # With conversation context
        pass
    
    def get_status(self) -> str:
        return "active"
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {...}
```

### Learning Resources

- **LangChain Docs**: https://python.langchain.com/
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Azure OpenAI**: https://learn.microsoft.com/azure/ai-services/openai/
- **System Design Patterns**: Multi-agent orchestration, state machines

### Contributing

When adding new features:
1. Follow existing code patterns
2. Add comprehensive tests
3. Document in docstrings
4. Update this guide
5. Consider backward compatibility

---

**End of Developer Guide**

*Last Updated: October 2025*

*For questions or contributions, see the main [README.md](../README.md)*
