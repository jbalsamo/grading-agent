"""
Streamlit UI components for streaming agent responses.

Provides components for real-time streaming display:
- StreamingContainer: Display streaming text with animations
- AgentProgressIndicator: Show agent status and progress
- WorkflowVisualizer: Visual representation of workflow progress
"""
import streamlit as st
from typing import List, Dict, Any, Optional
import time


class StreamingContainer:
    """
    Container for displaying streaming text in Streamlit.
    
    Provides real-time text updates with smooth rendering.
    """
    
    def __init__(self, container_key: str = "streaming"):
        """
        Initialize streaming container.
        
        Args:
            container_key: Unique key for Streamlit container
        """
        self.container_key = container_key
        self.content = ""
    
    def update(self, chunk: str) -> None:
        """
        Update container with new chunk.
        
        Args:
            chunk: New text chunk to append
        """
        self.content += chunk
    
    def render(self, placeholder) -> None:
        """
        Render current content to placeholder.
        
        Args:
            placeholder: Streamlit placeholder to render into
        """
        placeholder.markdown(self.content)
    
    def clear(self) -> None:
        """Clear container content."""
        self.content = ""
    
    def get_content(self) -> str:
        """Get current content."""
        return self.content


class AgentProgressIndicator:
    """
    Shows progress and status for individual agents.
    
    Displays:
    - Agent name
    - Current status (pending, streaming, complete, error)
    - Progress indicators
    - Timing information
    """
    
    STATUS_ICONS = {
        'pending': '⏳',
        'streaming': '🔄',
        'complete': '✅',
        'error': '❌',
        'unknown': '❓'
    }
    
    STATUS_COLORS = {
        'pending': 'gray',
        'streaming': 'blue',
        'complete': 'green',
        'error': 'red',
        'unknown': 'gray'
    }
    
    @staticmethod
    def render(
        agent_name: str,
        status: str = 'pending',
        details: Optional[str] = None,
        duration: Optional[float] = None
    ) -> None:
        """
        Render agent progress indicator.
        
        Args:
            agent_name: Name of the agent
            status: Current status
            details: Optional details text
            duration: Optional duration in seconds
        """
        icon = AgentProgressIndicator.STATUS_ICONS.get(status, '❓')
        
        # Build status text
        status_text = f"{icon} **{agent_name}**"
        
        if status == 'streaming':
            status_text += " _is processing..._"
        elif status == 'complete':
            status_text += " _complete_"
            if duration:
                status_text += f" ({duration:.1f}s)"
        elif status == 'error':
            status_text += " _error_"
        
        if details:
            status_text += f" - {details}"
        
        # Render with appropriate styling
        if status == 'streaming':
            st.info(status_text)
        elif status == 'complete':
            st.success(status_text)
        elif status == 'error':
            st.error(status_text)
        else:
            st.write(status_text)


class WorkflowVisualizer:
    """
    Visualizes multi-agent workflow progress.
    
    Shows the workflow path with visual indicators for each step.
    """
    
    @staticmethod
    def render(
        workflow_steps: List[str],
        current_step: Optional[str] = None,
        completed_steps: Optional[List[str]] = None
    ) -> None:
        """
        Render workflow visualization.
        
        Args:
            workflow_steps: List of workflow step names
            current_step: Currently active step
            completed_steps: List of completed steps
        """
        if not workflow_steps:
            return
        
        completed = completed_steps or []
        
        # Build workflow visualization
        workflow_display = []
        
        for i, step in enumerate(workflow_steps):
            # Determine step status
            if step in completed:
                icon = "✅"
                style = "**"
            elif step == current_step:
                icon = "🔄"
                style = "**"
            else:
                icon = "⏳"
                style = ""
            
            # Add step to display
            if style:
                workflow_display.append(f"{icon} {style}{step}{style}")
            else:
                workflow_display.append(f"{icon} {step}")
            
            # Add arrow between steps (except last)
            if i < len(workflow_steps) - 1:
                workflow_display.append("→")
        
        # Render
        st.write(" ".join(workflow_display))


# Helper functions for common rendering patterns

def render_streaming_response(
    agent_name: str,
    generator,
    show_progress: bool = True
) -> str:
    """
    Render a streaming response from an agent.
    
    Args:
        agent_name: Name of the agent
        generator: Async generator yielding chunks
        show_progress: Whether to show progress indicator
        
    Returns:
        Complete response text
    """
    # Create placeholder for streaming content
    placeholder = st.empty()
    
    # Show progress indicator
    if show_progress:
        with st.status(f"{agent_name} is processing...", expanded=True):
            st.write("Generating response...")
    
    # Stream content
    container = StreamingContainer()
    
    try:
        for chunk in generator:
            container.update(chunk)
            container.render(placeholder)
            time.sleep(0.01)  # Small delay for smooth rendering
        
        if show_progress:
            st.success(f"{agent_name} completed!")
        
        return container.get_content()
        
    except Exception as e:
        st.error(f"Error during streaming: {e}")
        return container.get_content()


def render_agent_status(
    agents: Dict[str, Dict[str, Any]],
    layout: str = 'vertical'
) -> None:
    """
    Render status for multiple agents.
    
    Args:
        agents: Dictionary of agent_name -> status_info
        layout: 'vertical' or 'horizontal' layout
    """
    if layout == 'horizontal':
        cols = st.columns(len(agents))
        for col, (agent_name, info) in zip(cols, agents.items()):
            with col:
                AgentProgressIndicator.render(
                    agent_name=agent_name,
                    status=info.get('status', 'unknown'),
                    details=info.get('details'),
                    duration=info.get('duration')
                )
    else:
        for agent_name, info in agents.items():
            AgentProgressIndicator.render(
                agent_name=agent_name,
                status=info.get('status', 'unknown'),
                details=info.get('details'),
                duration=info.get('duration')
            )


def render_workflow_progress(
    workflow_name: str,
    steps: List[str],
    current_step: Optional[str] = None,
    completed_steps: Optional[List[str]] = None,
    show_in_sidebar: bool = False
) -> None:
    """
    Render workflow progress visualization.
    
    Args:
        workflow_name: Name of the workflow
        steps: List of workflow steps
        current_step: Currently active step
        completed_steps: Completed steps
        show_in_sidebar: Whether to show in sidebar
    """
    render_location = st.sidebar if show_in_sidebar else st
    
    with render_location:
        st.subheader(f"📊 {workflow_name}")
        WorkflowVisualizer.render(
            workflow_steps=steps,
            current_step=current_step,
            completed_steps=completed_steps
        )
        
        # Show progress percentage
        if steps:
            completed = completed_steps or []
            progress = len(completed) / len(steps)
            st.progress(progress)
            st.caption(f"{len(completed)}/{len(steps)} steps complete")


def create_streaming_expander(
    title: str,
    agent_name: str,
    content: str,
    expanded: bool = False
) -> None:
    """
    Create an expander with streaming content.
    
    Args:
        title: Expander title
        agent_name: Name of the agent
        content: Content to display
        expanded: Whether to start expanded
    """
    with st.expander(f"{title} - {agent_name}", expanded=expanded):
        st.markdown(content)


def render_streaming_metrics(
    metrics: Dict[str, Any],
    show_in_sidebar: bool = True
) -> None:
    """
    Render streaming performance metrics.
    
    Args:
        metrics: Dictionary of metrics
        show_in_sidebar: Whether to show in sidebar
    """
    render_location = st.sidebar if show_in_sidebar else st
    
    with render_location:
        st.subheader("📈 Streaming Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Chunks",
                metrics.get('total_chunks', 0)
            )
            st.metric(
                "Duration",
                f"{metrics.get('duration', 0):.1f}s"
            )
        
        with col2:
            st.metric(
                "Characters",
                metrics.get('total_chars', 0)
            )
            st.metric(
                "Speed",
                f"{metrics.get('chars_per_sec', 0):.0f} c/s"
            )
