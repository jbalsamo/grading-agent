"""
State definitions for the grading agent application.

This module defines TypedDict schemas used throughout the LangGraph workflow.
All state definitions support both streaming and non-streaming operations.
"""
from typing import TypedDict, Annotated, List, Dict, Any, Optional
import operator


class StreamingState(TypedDict, total=False):
    """
    Base state for streaming operations.
    
    This state includes fields common to all streaming workflows:
    - Message history
    - User input
    - Streaming chunk tracking
    - Agent routing
    - Error handling
    
    Attributes:
        messages: List of chat messages in LangChain format
        user_input: The original user input string
        response: The final synthesized response
        error: Any error message encountered during processing
        streaming_chunks: Accumulated chunks during streaming
        current_agent: Name of currently active agent
        stream_status: Status of streaming ('idle', 'streaming', 'complete', 'error')
        stream_start_time: Timestamp when streaming started
        stream_end_time: Timestamp when streaming completed
        conversation_history: List of previous conversation messages
        message_id: Unique identifier for the current message
    """
    # Core fields (inherited from original MasterAgentState)
    messages: Annotated[List[Dict[str, str]], operator.add]
    user_input: str
    response: str
    error: str
    
    # Streaming-specific fields
    streaming_chunks: Annotated[List[str], operator.add]
    current_agent: str
    stream_status: str  # 'idle', 'streaming', 'complete', 'error'
    stream_start_time: float
    stream_end_time: float
    
    # History tracking
    conversation_history: List[Dict[str, Any]]
    message_id: str  # Unique ID for the current message


class GradingWorkflowState(StreamingState):
    """
    Enhanced state for grading-specific workflow.
    
    Extends StreamingState with grading-specific fields for the multi-agent
    workflow: Master → Grading → Formatting → (optional) Chat.
    
    This state supports:
    - Task classification and routing
    - Multiple agent responses in sequence
    - Grading result parsing and formatting
    - Optional additional notes
    - Data context retrieval
    - Workflow path tracking
    
    Attributes:
        task_classification: Classification result (chat, analysis, grading)
        agent_type: Type of agent handling the request
        agent_responses: Dictionary mapping agent names to their responses
        grading_results: Parsed grading data structure
        formatted_output: Spreadsheet-formatted grading results
        additional_notes: Optional notes from ChatAgent
        data_context: Contextual data retrieved from DataManager
        rubric_data: Rubric information for grading
        student_data: List of student data for batch grading
        scoring_metadata: Metadata about scoring thresholds and settings
        workflow_path: List of nodes visited in this workflow
        workflow_complete: Boolean indicating workflow completion
    """
    # Task routing (from original MasterAgentState)
    task_classification: str
    agent_type: str
    
    # Agent responses (enhanced to support multiple agents)
    agent_responses: Dict[str, Any]  # {agent_name: response}
    
    # Grading-specific fields
    grading_results: Dict[str, Any]  # Parsed grading data
    formatted_output: str  # Spreadsheet-formatted results
    additional_notes: str  # Optional notes from ChatAgent
    
    # Data context (from original MasterAgentState)
    data_context: Dict[str, Any]
    
    # Grading-specific data structures
    rubric_data: Optional[Dict[str, Any]]
    student_data: Optional[List[Dict[str, Any]]]
    scoring_metadata: Optional[Dict[str, Any]]
    
    # Workflow tracking
    workflow_path: List[str]  # Track agent sequence for debugging
    workflow_complete: bool


# Type aliases for clarity and code documentation
AgentResponse = Dict[str, Any]
GradingResults = Dict[str, Any]
StudentData = Dict[str, Any]
RubricData = Dict[str, Any]


# Legacy compatibility - MasterAgentState is now an alias
# This ensures backward compatibility with existing code
MasterAgentState = GradingWorkflowState


def create_initial_state(user_input: str) -> GradingWorkflowState:
    """
    Create an initial state for workflow execution.
    
    This helper function creates a properly initialized state with all
    required fields set to safe defaults.
    
    Args:
        user_input: The user's input message
        
    Returns:
        Initialized GradingWorkflowState ready for workflow execution
    """
    return GradingWorkflowState(
        # Core fields
        messages=[],
        user_input=user_input,
        response="",
        error="",
        
        # Streaming fields
        streaming_chunks=[],
        current_agent="",
        stream_status="idle",
        stream_start_time=0.0,
        stream_end_time=0.0,
        
        # History
        conversation_history=[],
        message_id="",
        
        # Task routing
        task_classification="",
        agent_type="",
        
        # Agent responses
        agent_responses={},
        grading_results={},
        formatted_output="",
        additional_notes="",
        
        # Data context
        data_context={},
        
        # Grading-specific
        rubric_data=None,
        student_data=None,
        scoring_metadata=None,
        
        # Workflow tracking
        workflow_path=[],
        workflow_complete=False
    )


def validate_state(state: GradingWorkflowState) -> bool:
    """
    Validate that a state has all required fields.
    
    Useful for debugging and ensuring state integrity during
    workflow execution.
    
    Args:
        state: State to validate
        
    Returns:
        True if state is valid, False otherwise
    """
    required_fields = [
        'user_input',
        'response',
        'error',
        'agent_type',
        'task_classification'
    ]
    
    for field in required_fields:
        if field not in state:
            return False
    
    return True


def get_state_summary(state: GradingWorkflowState) -> str:
    """
    Get a human-readable summary of the current state.
    
    Useful for logging and debugging workflow execution.
    
    Args:
        state: State to summarize
        
    Returns:
        String summary of key state fields
    """
    return f"""State Summary:
  User Input: {state.get('user_input', 'N/A')[:50]}...
  Agent Type: {state.get('agent_type', 'N/A')}
  Current Agent: {state.get('current_agent', 'N/A')}
  Stream Status: {state.get('stream_status', 'N/A')}
  Workflow Path: {' → '.join(state.get('workflow_path', []))}
  Error: {state.get('error', 'None')}
  Response Length: {len(state.get('response', ''))} chars
"""
