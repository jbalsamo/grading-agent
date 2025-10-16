"""
Master Agent Controller for managing multiple specialized agents and data management.
"""
from typing import Dict, Any, TypedDict, List, Optional
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END
from .config import config
from .utils import SystemMonitor
from .conversation_history import ConversationHistory
from .security import InputValidator, RateLimiter, InputValidationException, RateLimitException
from .performance import ResponseCache, TokenOptimizer, PerformanceMonitor
from .monitoring import metrics_collector
import logging
import json
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MasterAgentState(TypedDict):
    """State definition for the master agent.
    
    This TypedDict defines the state structure used throughout the LangGraph workflow.
    It tracks all information needed for processing user requests through the multi-agent system.
    
    Attributes:
        messages: List of chat messages in LangChain format
        user_input: The original user input string
        response: The final synthesized response
        error: Any error message encountered during processing
        agent_type: Type of agent handling the request (chat, analysis, grading, code_review)
        task_classification: Classification result from the task classifier
        agent_responses: Dictionary mapping agent names to their responses
        data_context: Contextual data retrieved from the data manager
        conversation_history: List of previous conversation messages
    """
    messages: list
    user_input: str
    response: str
    error: str
    agent_type: str
    task_classification: str
    agent_responses: dict
    data_context: dict
    conversation_history: list

class MasterAgent:
    """Master Agent Controller for managing specialized agents and data.
    
    The MasterAgent serves as the central orchestrator for the multi-agent system.
    It uses LangGraph to manage a workflow that classifies tasks, routes them to
    specialized agents, manages data persistence, and synthesizes responses.
    
    Key Features:
        - Task classification using LLM
        - Routing to specialized agents (chat, analysis, grading, code review)
        - Conversation history management with persistence
        - Data storage and retrieval
        - Performance monitoring and health checks
        - Security features (input validation, rate limiting)
        - Response caching for improved performance
    
    Attributes:
        llm: Azure OpenAI LLM instance
        graph: LangGraph compiled workflow
        specialized_agents: Dictionary of initialized specialized agents
        data_manager: Data persistence manager
        monitor: System performance monitor
        conversation_history: Conversation history manager with rolling window
        input_validator: Input validation and sanitization
        rate_limiter: Request rate limiting
        response_cache: Response caching for common queries
        performance_monitor: Performance metrics tracker
    """
    
    def __init__(self):
        """Initialize the master agent with Azure OpenAI configuration.
        
        This constructor:
        1. Creates the Azure OpenAI LLM instance
        2. Builds the LangGraph workflow
        3. Initializes specialized agents (chat, analysis, grading, code review)
        4. Sets up data management
        5. Configures security and performance components
        6. Loads previous conversation history from disk if available
        
        Raises:
            ValueError: If required configuration is missing or invalid
            Exception: If Azure OpenAI initialization fails
        """
        self.llm = self._create_llm()
        self.graph = self._create_graph()
        self.specialized_agents = {}
        self.data_manager = None
        self.monitor = SystemMonitor()
        self.conversation_history = ConversationHistory(max_messages=config.max_conversation_messages)
        
        # Security and performance components
        self.input_validator = InputValidator()
        self.rate_limiter = RateLimiter()
        self.response_cache = ResponseCache()
        self.performance_monitor = PerformanceMonitor()
        
        self._initialize_agents()
        
        # Load previous conversation history if available
        self._load_conversation_history()
    
    def _create_llm(self) -> AzureChatOpenAI:
        """Create Azure OpenAI LLM instance.
        
        Initializes the LangChain Azure OpenAI chat model with configuration
        from the config module.
        
        Returns:
            AzureChatOpenAI: Configured LLM instance
            
        Raises:
            Exception: If Azure OpenAI initialization fails
        """
        try:
            llm = AzureChatOpenAI(
                **config.get_azure_openai_kwargs(),
                temperature=1.0,
            )
            logger.info(f"Master Agent initialized with Azure OpenAI deployment: {config.chat_deployment}")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI: {e}")
            raise
    
    def _initialize_agents(self):
        """Initialize specialized agents.
        
        Attempts to import and initialize all specialized agents:
        - ChatAgent: General conversation and questions
        - AnalysisAgent: Data analysis and computational tasks
        - GradingAgent: Educational assessment and grading
        - CodeReviewAgent: Code review and quality analysis
        
        Also initializes the DataManager for persistent storage.
        
        If any agents fail to import, logs a warning and continues with
        available agents only.
        """
        try:
            # Import and initialize specialized agents
            from .agents.chat_agent import ChatAgent
            from .agents.analysis_agent import AnalysisAgent
            from .agents.grading_agent import GradingAgent
            from .data_manager import DataManager
            
            self.specialized_agents = {
                "chat": ChatAgent(),
                "analysis": AnalysisAgent(),
                "grading": GradingAgent()
            }
            
            self.data_manager = DataManager()
            logger.info("Specialized agents and data manager initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Some specialized agents not available: {e}")
            # Initialize with basic fallback
            self.specialized_agents = {}
            logger.info("Running with basic master agent only")
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow for the master agent.
        
        Builds a LangGraph state machine with the following nodes:
        - classify_task: Classify user request into task type
        - route_to_agent: Route to appropriate specialized agent
        - manage_data: Store interaction and retrieve context
        - synthesize_response: Combine agent response with context
        - handle_error: Handle any errors in the workflow
        
        The workflow uses conditional edges to handle different paths
        based on task classification and error states.
        
        Returns:
            StateGraph: Compiled LangGraph workflow
        """
        workflow = StateGraph(MasterAgentState)
        
        # Add nodes
        workflow.add_node("classify_task", self._classify_task)
        workflow.add_node("route_to_agent", self._route_to_agent)
        workflow.add_node("manage_data", self._manage_data)
        workflow.add_node("synthesize_response", self._synthesize_response)
        workflow.add_node("handle_error", self._handle_error)
        
        # Set entry point
        workflow.set_entry_point("classify_task")
        
        # Add edges
        workflow.add_conditional_edges(
            "classify_task",
            self._should_continue_classification,
            {
                "route": "route_to_agent",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "route_to_agent",
            self._should_manage_data,
            {
                "data": "manage_data",
                "synthesize": "synthesize_response",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("manage_data", "synthesize_response")
        workflow.add_edge("synthesize_response", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    def _classify_task(self, state: MasterAgentState) -> MasterAgentState:
        """Classify the user's task to determine which agent to use.
        
        Uses the LLM to analyze the user input and classify it into one of:
        - chat: General conversation, questions, or assistance
        - analysis: Data analysis, file processing, or computational tasks
        - grading: Educational assessment, grading, or evaluation
        - code_review: Code review, refactoring, or quality analysis
        
        Args:
            state: Current agent state containing user input
            
        Returns:
            Updated state with task_classification and agent_type set
        """
        try:
            user_input = state.get("user_input", "")
            if not user_input.strip():
                state["error"] = "Empty input provided"
                return state
            
            # Use LLM to classify the task
            classification_prompt = f"""
            Classify the following user request into one of these categories:
            - chat: General conversation, questions, or assistance
            - analysis: Data analysis, file processing, or computational tasks
            - grading: Educational assessment, grading, or evaluation tasks
            - code_review: Code review, refactoring, or code quality analysis
            
            User request: "{user_input}"
            
            Respond with only the category name (chat, analysis, or grading).
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
    
    def _route_to_agent(self, state: MasterAgentState) -> MasterAgentState:
        """Route the task to the appropriate specialized agent.
        
        Sends the user request to the specialized agent determined by task
        classification. If the agent supports conversation history, it is
        passed along for context-aware responses. Falls back to master agent
        if no specialized agent is available.
        
        Args:
            state: Current agent state with task classification
            
        Returns:
            Updated state with agent_responses containing the agent's output
        """
        try:
            agent_type = state.get("agent_type", "chat")
            user_input = state.get("user_input", "")
            
            if agent_type in self.specialized_agents:
                # Use specialized agent with conversation history
                specialized_agent = self.specialized_agents[agent_type]
                
                # Check if agent supports conversation history
                if hasattr(specialized_agent, 'process_with_history'):
                    response = specialized_agent.process_with_history(user_input, self.conversation_history)
                else:
                    # Fallback to original method for backward compatibility
                    response = specialized_agent.process(user_input)
                
                state["agent_responses"] = {agent_type: response}
                logger.info(f"Task routed to {agent_type} agent")
            else:
                # Fallback to master agent direct processing with history
                # Get conversation history for context
                history_messages = self.conversation_history.get_langchain_messages()
                
                # Add current user message
                from langchain_core.messages import HumanMessage, SystemMessage
                current_messages = [
                    SystemMessage(content=f"You are handling a {agent_type} task."),
                    HumanMessage(content=user_input)
                ]
                
                # Combine history with current message
                all_messages = history_messages + current_messages
                
                response = self.llm.invoke(all_messages)
                state["agent_responses"] = {"master": response.content}
                logger.info("Task handled by master agent directly with conversation history")
            
            return state
            
        except Exception as e:
            state["error"] = f"Error routing to agent: {str(e)}"
            logger.error(f"Error in _route_to_agent: {e}")
            return state
    
    def _manage_data(self, state: MasterAgentState) -> MasterAgentState:
        """Manage data context and storage.
        
        Stores the current interaction in the data manager and retrieves
        relevant historical context based on the user input. This enables
        the system to maintain long-term memory beyond the conversation window.
        
        Args:
            state: Current agent state with user input and agent responses
            
        Returns:
            Updated state with data_context containing relevant historical interactions
        """
        try:
            if self.data_manager:
                user_input = state.get("user_input", "")
                agent_responses = state.get("agent_responses", {})
                
                # Store interaction data
                interaction_data = {
                    "user_input": user_input,
                    "task_type": state.get("task_classification", "unknown"),
                    "agent_responses": agent_responses,
                    "timestamp": self._get_timestamp()
                }
                
                self.data_manager.store_interaction(interaction_data)
                
                # Get relevant context if needed
                context = self.data_manager.get_relevant_context(user_input)
                state["data_context"] = context
                
                logger.info("Data management completed")
            else:
                state["data_context"] = {}
                logger.info("No data manager available, skipping data management")
            
            return state
            
        except Exception as e:
            state["error"] = f"Error managing data: {str(e)}"
            logger.error(f"Error in _manage_data: {e}")
            return state
    
    def _synthesize_response(self, state: MasterAgentState) -> MasterAgentState:
        """Synthesize the final response from agent outputs and data context.
        
        Combines the agent's response with any relevant historical context
        to create the final response. Optionally enhances the response with
        context information when relevant interactions are found.
        
        Args:
            state: Current agent state with agent responses and data context
            
        Returns:
            Updated state with final response ready for user
        """
        try:
            agent_responses = state.get("agent_responses", {})
            data_context = state.get("data_context", {})
            
            if not agent_responses:
                state["error"] = "No agent responses to synthesize"
                return state
            
            # For now, use the primary agent response
            primary_response = list(agent_responses.values())[0]
            
            # If there's relevant context, enhance the response
            if data_context and data_context.get("relevant_interactions"):
                context_info = f"\n\n[Context: Based on {len(data_context['relevant_interactions'])} previous interactions]"
                primary_response += context_info
            
            state["response"] = primary_response
            logger.info("Response synthesized successfully")
            return state
            
        except Exception as e:
            state["error"] = f"Error synthesizing response: {str(e)}"
            logger.error(f"Error in _synthesize_response: {e}")
            return state
    
    def _handle_error(self, state: MasterAgentState) -> MasterAgentState:
        """Handle errors in the workflow.
        
        Creates a user-friendly error response when any step in the
        workflow encounters an error.
        
        Args:
            state: Current agent state with error message
            
        Returns:
            Updated state with error response
        """
        error_msg = state.get("error", "Unknown error occurred")
        state["response"] = f"I apologize, but I encountered an error: {error_msg}"
        logger.error(f"Handled error: {error_msg}")
        return state
    
    def _should_continue_classification(self, state: MasterAgentState) -> str:
        """Determine whether to continue after classification.
        
        Conditional edge function that routes to error handler if classification
        failed, otherwise routes to agent routing.
        
        Args:
            state: Current agent state
            
        Returns:
            'error' if error exists, 'route' otherwise
        """
        if state.get("error"):
            return "error"
        return "route"
    
    def _should_manage_data(self, state: MasterAgentState) -> str:
        """Determine whether to manage data after routing.
        
        Conditional edge function that routes to error handler if routing failed,
        to data management if data manager is available, or directly to response
        synthesis otherwise.
        
        Args:
            state: Current agent state
            
        Returns:
            'error', 'data', or 'synthesize' depending on state and availability
        """
        if state.get("error"):
            return "error"
        if self.data_manager:
            return "data"
        return "synthesize"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format.
        
        Returns:
            Current timestamp as ISO 8601 formatted string
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def chat(self, user_input: str, session_id: str = "default") -> str:
        """Main chat method to interact with the master agent.
        
        Args:
            user_input: The user's input message
            session_id: Session identifier for rate limiting (default: "default")
            
        Returns:
            The agent's response
            
        Raises:
            InputValidationException: If input validation fails
            RateLimitException: If rate limit is exceeded
        """
        start_time = time.time()
        success = True
        agent_type = "unknown"
        
        try:
            # Step 1: Validate input
            validation_result = self.input_validator.validate_input(user_input)
            if not validation_result["valid"]:
                raise InputValidationException(validation_result["error"])
            
            # Sanitize input
            user_input = self.input_validator.sanitize_input(user_input)
            
            # Step 2: Check rate limit
            rate_check = self.rate_limiter.check_rate_limit(session_id)
            if not rate_check["allowed"]:
                raise RateLimitException(
                    f"Rate limit exceeded. Please try again in {rate_check['retry_after']} seconds."
                )
            
            # Step 3: Check cache
            cache_context = str(len(self.conversation_history))  # Simple context key
            cached_response = self.response_cache.get(user_input, cache_context)
            if cached_response:
                logger.info("Returning cached response")
                return cached_response
            
            # Step 4: Add user message to conversation history
            self.conversation_history.add_user_message(user_input)
            
            # Step 5: Initialize state
            initial_state = {
                "messages": [],
                "user_input": user_input,
                "response": "",
                "error": "",
                "agent_type": "",
                "task_classification": "",
                "agent_responses": {},
                "data_context": {},
                "conversation_history": self.conversation_history.get_messages_for_llm()
            }
            
            # Step 6: Run the graph
            result = self.graph.invoke(initial_state)
            agent_type = result.get("task_classification", "unknown")
            
            response = result.get("response", "No response generated")
            
            # Step 7: Cache the response
            self.response_cache.set(user_input, response, cache_context)
            
            # Step 8: Add assistant response to conversation history
            self.conversation_history.add_assistant_message(response, agent_type)
            
            # Step 9: Track performance
            response_time = time.time() - start_time
            self.monitor.log_request(agent_type, response_time, success=True)
            metrics_collector.record_request(agent_type, response_time, success=True)
            
            # Estimate and record token usage
            estimated_tokens = TokenOptimizer.estimate_tokens(user_input + response)
            self.performance_monitor.record_token_usage(estimated_tokens)
            
            return response
            
        except (InputValidationException, RateLimitException) as e:
            # These are expected exceptions, don't log as errors
            logger.warning(f"Request blocked: {e}")
            raise
            
        except Exception as e:
            success = False
            response_time = time.time() - start_time
            self.monitor.log_request(agent_type, response_time, success=False)
            metrics_collector.record_request(agent_type, response_time, success=False, error=str(e))
            
            error_response = f"I apologize, but I encountered an error: {str(e)}"
            # Still add the error response to history for context
            self.conversation_history.add_assistant_message(error_response, "error")
            
            logger.error(f"Error in chat method: {e}")
            return error_response
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the master agent configuration.
        
        Returns:
            Dictionary containing:
                - endpoint: Azure OpenAI endpoint URL
                - deployment: Model deployment name
                - api_version: API version being used
                - model_type: Type of model (Master Agent)
                - specialized_agents: List of available specialized agents
                - data_manager_available: Whether data manager is active
        """
        return {
            "endpoint": config.endpoint,
            "deployment": config.chat_deployment,
            "api_version": config.api_version,
            "model_type": "Azure OpenAI Master Agent",
            "specialized_agents": list(self.specialized_agents.keys()),
            "data_manager_available": self.data_manager is not None
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all managed agents.
        
        Queries each specialized agent for its status and compiles a
        comprehensive status report for the entire system.
        
        Returns:
            Dictionary containing:
                - master_agent: Master agent status (always 'active')
                - specialized_agents: Status of each specialized agent
                - data_manager: Data manager status ('active' or 'inactive')
        """
        status = {
            "master_agent": "active",
            "specialized_agents": {},
            "data_manager": "active" if self.data_manager else "inactive"
        }
        
        for agent_name, agent in self.specialized_agents.items():
            try:
                # Try to get status from agent if it has a status method
                if hasattr(agent, 'get_status'):
                    status["specialized_agents"][agent_name] = agent.get_status()
                else:
                    status["specialized_agents"][agent_name] = "active"
            except Exception as e:
                status["specialized_agents"][agent_name] = f"error: {str(e)}"
        
        return status
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics from the system monitor.
        
        Returns:
            Dictionary containing:
                - uptime_formatted: Human-readable uptime
                - total_requests: Total number of requests processed
                - error_rate: Percentage of failed requests
                - average_response_time: Average response time in seconds
                - requests_per_minute: Request rate
                - agent_usage: Per-agent usage statistics
        """
        return self.monitor.get_stats()
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run a comprehensive health check.
        
        Checks configuration, data directory, connectivity, and system resources.
        
        Returns:
            Dictionary containing:
                - overall_status: 'healthy', 'degraded', or 'unhealthy'
                - checks: Individual check results with status for each component
        """
        from .utils import SystemHealthChecker
        health_checker = SystemHealthChecker(self)
        return health_checker.run_health_check()
    
    def get_conversation_history(self) -> Dict[str, Any]:
        """Get conversation history statistics and recent messages.
        
        Returns:
            Dictionary containing:
                - stats: Message count statistics and agent usage
                - recent_context: Formatted recent conversation context
                - total_messages: Total number of messages in history
        """
        return {
            "stats": self.conversation_history.get_stats(),
            "recent_context": self.conversation_history.get_recent_context(10),
            "total_messages": len(self.conversation_history)
        }
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history.
        
        Removes all messages from the conversation history. This does not
        delete the saved history file; use conversation_history.delete_saved_history()
        for that.
        """
        self.conversation_history.clear_history()
        logger.info("Conversation history cleared by user request")
    
    def set_conversation_history_limit(self, max_messages: int) -> None:
        """Set the maximum number of messages to keep in conversation history.
        
        Updates the rolling window size and trims existing messages if necessary.
        
        Args:
            max_messages: Maximum number of messages to retain (must be > 0)
        """
        if max_messages > 0:
            self.conversation_history.max_messages = max_messages
            # Trim if necessary
            if len(self.conversation_history.messages) > max_messages:
                self.conversation_history.messages = self.conversation_history.messages[-max_messages:]
            logger.info(f"Conversation history limit set to {max_messages}")
        else:
            logger.warning("Invalid conversation history limit. Must be greater than 0.")
    
    def _load_conversation_history(self) -> None:
        """Load conversation history from disk on startup.
        
        Attempts to restore the previous conversation session from the saved
        history file. If no file exists or loading fails, starts with a fresh
        conversation history.
        """
        try:
            if self.conversation_history.load_from_disk():
                loaded_count = len(self.conversation_history)
                if loaded_count > 0:
                    logger.info(f"Restored previous conversation with {loaded_count} messages")
                    print(f"💾 Restored previous conversation with {loaded_count} messages")
            else:
                logger.info("Starting with fresh conversation history")
        except Exception as e:
            logger.warning(f"Could not load conversation history: {e}")
            print(f"⚠️  Could not restore previous conversation, starting fresh")
    
    def save_conversation_history(self) -> bool:
        """Save current conversation history to disk.
        
        Returns:
            True if save was successful, False otherwise
        """
        try:
            success = self.conversation_history.save_to_disk()
            if success:
                logger.info("Conversation history saved successfully")
            return success
        except Exception as e:
            logger.error(f"Error saving conversation history: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get response cache statistics.
        
        Returns:
            Dictionary containing cache metrics:
                - enabled: Whether caching is enabled
                - size: Current number of cached entries
                - max_size: Maximum cache capacity
                - hits: Number of cache hits
                - misses: Number of cache misses
                - hit_rate: Cache hit rate percentage
                - ttl: Time-to-live in seconds
        """
        return self.response_cache.get_stats()
    
    def get_performance_stats_detailed(self) -> Dict[str, Any]:
        """Get detailed performance statistics including token usage.
        
        Returns:
            Dictionary containing detailed performance metrics including
            token consumption and processing times
        """
        return self.performance_monitor.get_stats()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics for monitoring.
        
        Returns:
            Dictionary containing system-wide metrics:
                - uptime_seconds: System uptime
                - total_requests: Total requests processed
                - total_errors: Total errors encountered
                - overall_error_rate: System-wide error rate
                - agents: Per-agent metrics
        """
        return metrics_collector.get_metrics()
    
    def export_metrics(self, filepath: str = "metrics.json"):
        """Export metrics to file.
        
        Saves current metrics to a JSON file for analysis or monitoring.
        
        Args:
            filepath: Path to save metrics file (default: 'metrics.json')
        """
        metrics_collector.export_to_file(filepath)
    
    def clear_cache(self):
        """Clear the response cache.
        
        Removes all cached responses, forcing fresh processing for all
        subsequent requests.
        """
        self.response_cache.clear()
        logger.info("Response cache cleared")
    
    def shutdown(self) -> None:
        """Perform cleanup operations before shutdown.
        
        Saves conversation history to disk and exports metrics if enabled.
        Should be called before the application exits to preserve session data.
        """
        logger.info("Shutting down Master Agent...")
        
        # Save conversation history
        if len(self.conversation_history) > 0:
            print("💾 Saving conversation history...")
            if self.save_conversation_history():
                print(f"✅ Saved {len(self.conversation_history)} messages for next session")
            else:
                print("⚠️  Could not save conversation history")
        
        # Export metrics before shutdown
        if config.enable_metrics:
            try:
                self.export_metrics()
                print("📊 Metrics exported to metrics.json")
            except Exception as e:
                logger.warning(f"Failed to export metrics: {e}")
        
        logger.info("Master Agent shutdown complete")
