"""
Master Agent Controller for managing multiple specialized agents and data management.
"""
from typing import Dict, Any, TypedDict, List, Optional
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END
from config import config
from utils import SystemMonitor
import logging
import json
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MasterAgentState(TypedDict):
    """State definition for the master agent."""
    messages: list
    user_input: str
    response: str
    error: str
    agent_type: str
    task_classification: str
    agent_responses: dict
    data_context: dict

class MasterAgent:
    """Master Agent Controller for managing specialized agents and data."""
    
    def __init__(self):
        """Initialize the master agent with Azure OpenAI configuration."""
        self.llm = self._create_llm()
        self.graph = self._create_graph()
        self.specialized_agents = {}
        self.data_manager = None
        self.monitor = SystemMonitor()
        self._initialize_agents()
    
    def _create_llm(self) -> AzureChatOpenAI:
        """Create Azure OpenAI LLM instance."""
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
        """Initialize specialized agents."""
        try:
            # Import and initialize specialized agents
            from agents.chat_agent import ChatAgent
            from agents.analysis_agent import AnalysisAgent
            from agents.grading_agent import GradingAgent
            from data_manager import DataManager
            
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
        """Create the LangGraph workflow for the master agent."""
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
        """Classify the user's task to determine which agent to use."""
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
            
            # Validate classification
            valid_types = ["chat", "analysis", "grading"]
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
        """Route the task to the appropriate specialized agent."""
        try:
            agent_type = state.get("agent_type", "chat")
            user_input = state.get("user_input", "")
            
            if agent_type in self.specialized_agents:
                # Use specialized agent
                specialized_agent = self.specialized_agents[agent_type]
                response = specialized_agent.process(user_input)
                state["agent_responses"] = {agent_type: response}
                logger.info(f"Task routed to {agent_type} agent")
            else:
                # Fallback to master agent direct processing
                messages = state.get("messages", [])
                from langchain_core.messages import HumanMessage, SystemMessage
                
                langchain_messages = []
                for msg in messages:
                    if msg["role"] == "system":
                        langchain_messages.append(SystemMessage(content=msg["content"]))
                    elif msg["role"] == "user":
                        langchain_messages.append(HumanMessage(content=msg["content"]))
                
                response = self.llm.invoke(langchain_messages)
                state["agent_responses"] = {"master": response.content}
                logger.info("Task handled by master agent directly")
            
            return state
            
        except Exception as e:
            state["error"] = f"Error routing to agent: {str(e)}"
            logger.error(f"Error in _route_to_agent: {e}")
            return state
    
    def _manage_data(self, state: MasterAgentState) -> MasterAgentState:
        """Manage data context and storage."""
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
        """Synthesize the final response from agent outputs and data context."""
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
        """Handle errors in the workflow."""
        error_msg = state.get("error", "Unknown error occurred")
        state["response"] = f"I apologize, but I encountered an error: {error_msg}"
        logger.error(f"Handled error: {error_msg}")
        return state
    
    def _should_continue_classification(self, state: MasterAgentState) -> str:
        """Determine whether to continue after classification."""
        if state.get("error"):
            return "error"
        return "route"
    
    def _should_manage_data(self, state: MasterAgentState) -> str:
        """Determine whether to manage data after routing."""
        if state.get("error"):
            return "error"
        if self.data_manager:
            return "data"
        return "synthesize"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def chat(self, user_input: str) -> str:
        """Main chat method to interact with the master agent."""
        start_time = time.time()
        success = True
        agent_type = "unknown"
        
        try:
            # Initialize state
            initial_state = {
                "messages": [],
                "user_input": user_input,
                "response": "",
                "error": "",
                "agent_type": "",
                "task_classification": "",
                "agent_responses": {},
                "data_context": {}
            }
            
            # Run the graph
            result = self.graph.invoke(initial_state)
            agent_type = result.get("task_classification", "unknown")
            
            response = result.get("response", "No response generated")
            
            # Log successful request
            response_time = time.time() - start_time
            self.monitor.log_request(agent_type, response_time, success=True)
            
            return response
            
        except Exception as e:
            success = False
            response_time = time.time() - start_time
            self.monitor.log_request(agent_type, response_time, success=False)
            
            logger.error(f"Error in chat method: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the master agent configuration."""
        return {
            "endpoint": config.endpoint,
            "deployment": config.chat_deployment,
            "api_version": config.api_version,
            "model_type": "Azure OpenAI Master Agent",
            "specialized_agents": list(self.specialized_agents.keys()),
            "data_manager_available": self.data_manager is not None
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all managed agents."""
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
        """Get performance statistics from the system monitor."""
        return self.monitor.get_stats()
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run a comprehensive health check."""
        from utils import SystemHealthChecker
        health_checker = SystemHealthChecker(self)
        return health_checker.run_health_check()
