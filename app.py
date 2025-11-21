"""
StreamLit Application for the Grading Helper.

This module provides a web-based interface for the Grading Helper, built on the
Azure OpenAI multi-agent system with Google APK-style debugging tools, document
upload capabilities, and real-time token tracking.
"""

import streamlit as st
import os
import sys
import json
import time
import argparse
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Add modules directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.master_agent import MasterAgent
from modules.config import config
from modules.security import InputValidationException, RateLimitException
from modules.ui.streaming_components import AgentProgressIndicator

logger = logging.getLogger(__name__)

# Parse command-line arguments
def parse_args():
    """Parse command-line arguments for the StreamLit app."""
    parser = argparse.ArgumentParser(
        description='Azure OpenAI Master Agent - StreamLit Web Interface'
    )
    parser.add_argument(
        '-D', '--debug',
        action='store_true',
        help='Enable debug mode (shows debugging tools and metrics)'
    )
    
    # StreamLit passes its own args, so we need to handle that
    try:
        args, unknown = parser.parse_known_args()
        return args
    except:
        # If parsing fails, return defaults
        class DefaultArgs:
            debug = False
        return DefaultArgs()

# Parse arguments once at module level
CLI_ARGS = parse_args()

# Page configuration with dark theme
st.set_page_config(
    page_title="Grading Helper",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme with Google APK styling
st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #252526;
        border-right: 1px solid #3e3e42;
    }
    
    /* Sidebar headers - compact spacing */
    [data-testid="stSidebar"] h1 {
        font-size: 1.4rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        padding-bottom: 4px;
    }
    
    [data-testid="stSidebar"] h2 {
        font-size: 1.1rem;
        margin-top: 0.8rem;
        margin-bottom: 0.4rem;
        padding-bottom: 3px;
    }
    
    [data-testid="stSidebar"] h3 {
        font-size: 1rem;
        margin-top: 0.6rem;
        margin-bottom: 0.3rem;
        padding-bottom: 2px;
    }
    
    /* Sidebar dividers - reduced spacing */
    [data-testid="stSidebar"] hr {
        margin: 0.5rem 0;
    }
    
    /* Sidebar captions and text - compact */
    [data-testid="stSidebar"] .stCaption {
        font-size: 0.7rem;
        margin: 2px 0;
        padding: 0;
        line-height: 1.2;
    }
    
    [data-testid="stSidebar"] p {
        margin: 4px 0;
        font-size: 0.85rem;
        line-height: 1.3;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
    }
    
    /* Input fields */
    .stTextInput input, .stTextArea textarea {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #3e3e42;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #0e639c;
        color: #ffffff;
        border: 1px solid #007acc;
        border-radius: 4px;
    }
    
    .stButton button:hover {
        background-color: #1177bb;
    }
    
    /* Debug panels */
    .debug-panel {
        background-color: #252526;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        padding: 10px;
        margin: 10px 0;
        font-family: 'Consolas', 'Monaco', monospace;
    }
    
    /* Variable viewer */
    .variable-item {
        background-color: #2d2d30;
        border-left: 3px solid #007acc;
        padding: 8px;
        margin: 4px 0;
        font-family: monospace;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
        color: #e0e0e0;
    }
    
    /* Metrics - Compact styling */
    [data-testid="stMetric"] {
        padding: 4px 8px;
        margin: 2px 0;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        margin-bottom: 2px;
        padding-bottom: 0;
    }
    
    [data-testid="stMetricValue"] {
        color: #4ec9b0;
        font-weight: bold;
        font-size: 1.1rem;
        margin: 0;
        padding: 0;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.7rem;
        margin-top: 0;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #2d2d30;
        border: 1px dashed #3e3e42;
        border-radius: 4px;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #1e3a1e;
        border: 1px solid #4ec9b0;
    }
    
    .stError {
        background-color: #3a1e1e;
        border: 1px solid #f48771;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #e0e0e0;
        border-bottom: 1px solid #3e3e42;
        padding-bottom: 8px;
    }
    
    /* Inline code */
    code {
        background-color: #1e1e1e;
        color: #d4d4d4;
        border: 1px solid #3e3e42;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    }
    
    /* Code blocks / Pre-formatted text */
    pre {
        background-color: #1e1e1e;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        padding: 12px;
        overflow-x: auto;
        color: #d4d4d4;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    }
    
    pre code {
        background-color: transparent;
        border: none;
        padding: 0;
        color: inherit;
    }
    
    /* Tables */
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 12px 0;
        background-color: #2d2d30;
        border: 1px solid #3e3e42;
    }
    
    th {
        background-color: #1e1e1e;
        color: #4ec9b0;
        padding: 10px;
        text-align: left;
        border: 1px solid #3e3e42;
        font-weight: bold;
    }
    
    td {
        padding: 8px;
        border: 1px solid #3e3e42;
        color: #e0e0e0;
    }
    
    tr:nth-child(even) {
        background-color: #252526;
    }
    
    tr:hover {
        background-color: #2a2a2e;
    }
    
    /* Lists */
    ul, ol {
        color: #e0e0e0;
        padding-left: 24px;
        margin: 8px 0;
    }
    
    li {
        margin: 4px 0;
        line-height: 1.6;
    }
    
    /* Blockquotes */
    blockquote {
        border-left: 4px solid #007acc;
        padding-left: 16px;
        margin: 12px 0;
        color: #b0b0b0;
        font-style: italic;
        background-color: #252526;
        padding: 12px 16px;
        border-radius: 0 4px 4px 0;
    }
    
    /* Links */
    a {
        color: #4fc3f7;
        text-decoration: none;
        border-bottom: 1px dotted #4fc3f7;
    }
    
    a:hover {
        color: #81d4fa;
        border-bottom: 1px solid #81d4fa;
    }
    
    /* Strong/Bold */
    strong, b {
        color: #4ec9b0;
        font-weight: bold;
    }
    
    /* Emphasis/Italic */
    em, i {
        color: #ce9178;
        font-style: italic;
    }
    
    /* Horizontal rule */
    hr {
        border: none;
        border-top: 1px solid #3e3e42;
        margin: 16px 0;
    }
    
    /* Paragraphs in chat */
    p {
        margin: 8px 0;
        line-height: 1.6;
        color: #e0e0e0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e1e1e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3e3e42;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """
    Initialize StreamLit session state variables.
    
    This function sets up all necessary session state variables for the application,
    including the master agent, conversation history, uploaded documents, and metrics.
    Debug mode is controlled by the -D/--debug CLI flag.
    """
    # TEMPORARY: Force complete reinitialization on EVERY run to clear old agents
    # This ensures no cached agents with temperature settings remain
    # TODO: Remove this aggressive clearing once temperature issue is confirmed fixed
    if 'agent' in st.session_state:
        # Delete old agent to force fresh creation
        del st.session_state['agent']
        st.session_state.agent = None
    
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.messages = []
        st.session_state.agent = None
        st.session_state.uploaded_documents = []
        st.session_state.document_markdown = []
        st.session_state.total_tokens = 0
        # Set debug mode based on CLI flag (default: False)
        st.session_state.debug_enabled = CLI_ARGS.debug
        st.session_state.variable_watch = {}
        st.session_state.request_history = []
        st.session_state.agent_state = {}
        
    # Initialize agent if not exists (use getattr to safely check)
    if not hasattr(st.session_state, 'agent') or st.session_state.agent is None:
        try:
            with st.spinner("Initializing Azure OpenAI Master Agent..."):
                # Force reload of master_agent module to clear any cached code
                import importlib
                import modules.master_agent
                importlib.reload(modules.master_agent)
                from modules.master_agent import MasterAgent as ReloadedMasterAgent
                
                st.session_state.agent = ReloadedMasterAgent()
                st.success("✅ Master Agent initialized successfully!")
        except Exception as e:
            st.error(f"❌ Failed to initialize agent: {e}")
            st.stop()


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for a given text.
    
    Args:
        text: The text to estimate tokens for
        
    Returns:
        Estimated number of tokens (approximately 4 characters per token)
    """
    return len(text) // 4


def _is_grading_request(prompt: str) -> bool:
    """Heuristic check to see if the user prompt is a grading request.

    This helps decide when to apply student-row filtering to uploaded
    markdown documents so that non-student lines are ignored for grading.
    """
    lowered = prompt.lower()
    keywords = [
        "grade ",
        "grading",
        "rubric",
        "student",
        "scores",
        "patient note",
    ]
    return any(k in lowered for k in keywords)


def _extract_valid_student_rows_from_markdown(markdown: str) -> Tuple[str, int, int]:
    """Return only lines that look like valid student info rows.

    A valid student row is heuristically defined as a line that:
    - Starts with a name in the form "Last, First"; and
    - Contains a Diagnosis/Problem #1 marker.

    Args:
        markdown: Full markdown text from an uploaded document.

    Returns:
        A tuple of (filtered_markdown, valid_count, skipped_count).
    """
    import re

    name_pattern = re.compile(r"^[^,\n]+,\s*[^,\n]+")
    diag_pattern = re.compile(r"diagnosis\s*/?\s*problem\s*#\d+:", re.IGNORECASE)

    valid_lines: List[str] = []
    skipped_count = 0

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if name_pattern.search(line) and diag_pattern.search(line):
            valid_lines.append(line)
        else:
            skipped_count += 1
            logger.info("Skipping non-student markdown line: %s", line[:200])

    filtered = "\n".join(valid_lines)
    return filtered, len(valid_lines), skipped_count


def process_uploaded_file(uploaded_file) -> Optional[str]:
    """
    Process an uploaded file and convert it to markdown.
    
    Args:
        uploaded_file: StreamLit uploaded file object
        
    Returns:
        Markdown content as string, or None if conversion fails
    """
    try:
        # Import markitdown
        from markitdown import MarkItDown
        
        # Save file temporarily
        temp_dir = Path("data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / uploaded_file.name
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Convert to markdown
        md = MarkItDown()
        result = md.convert(str(temp_path))
        
        # Clean up temp file
        temp_path.unlink()
        
        return result.text_content
        
    except Exception as e:
        st.error(f"Error converting {uploaded_file.name}: {e}")
        return None


def force_clear_all_caches():
    """Emergency function to completely clear all caches and force agent recreation."""
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Clear Python module cache for agents
    import sys
    modules_to_clear = [k for k in sys.modules.keys() if 'modules.agents' in k or 'modules.master_agent' in k]
    for mod in modules_to_clear:
        del sys.modules[mod]
    
    # Force garbage collection
    import gc
    gc.collect()
    
    st.success("✅ All caches cleared! Page will reload...")
    st.rerun()

def render_sidebar():
    """
    Render the sidebar with document upload, metrics, and debugging tools.
    
    This function creates the sidebar interface including:
    - Document upload functionality
    - Token usage metrics
    - Agent status information
    - Debug controls
    """
    with st.sidebar:
        st.title("📝 Grading Helper")
        
        # Document Upload Section
        st.header("📄 Document Upload")
        uploaded_files = st.file_uploader(
            "Upload documents (PDF, DOCX, TXT, etc.)",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'doc', 'txt', 'md', 'xlsx', 'csv', 'pptx'],
            help="Upload documents to convert to markdown and add to agent context"
        )
        
        if uploaded_files:
            if st.button("🔄 Process Documents"):
                with st.spinner("Converting documents to markdown..."):
                    for uploaded_file in uploaded_files:
                        # Check if already processed
                        if uploaded_file.name not in [d['name'] for d in st.session_state.uploaded_documents]:
                            markdown_content = process_uploaded_file(uploaded_file)
                            
                            if markdown_content:
                                content_length = len(markdown_content)
                                doc_tokens = estimate_tokens(markdown_content)
                                
                                doc_info = {
                                    'name': uploaded_file.name,
                                    'size': uploaded_file.size,
                                    'timestamp': datetime.now().isoformat(),
                                    'tokens': doc_tokens,
                                    'content_length': content_length
                                }
                                
                                st.session_state.uploaded_documents.append(doc_info)
                                st.session_state.document_markdown.append({
                                    'name': uploaded_file.name,
                                    'content': markdown_content
                                })
                                st.session_state.total_tokens += doc_info['tokens']
                                
                                # Success message with debug info
                                st.success(f"✅ {uploaded_file.name} processed")
                                
                                # Debug logging for document processing
                                if st.session_state.debug_enabled:
                                    st.info(f"🔍 **Debug:** Converted to {content_length:,} chars markdown (~{doc_tokens:,} tokens)")
                                    # Show first 200 chars of markdown as preview
                                    st.caption(f"Preview: {markdown_content[:200]}...")
                            else:
                                st.warning(f"⚠️ Failed to process {uploaded_file.name}")
        
        # Display uploaded documents
        if st.session_state.uploaded_documents:
            st.subheader("📚 Loaded Documents")
            for doc in st.session_state.uploaded_documents:
                with st.expander(f"📄 {doc['name']}"):
                    st.write(f"**Original Size:** {doc['size']:,} bytes")
                    st.write(f"**Markdown Length:** {doc.get('content_length', 'N/A'):,} chars")
                    st.write(f"**Estimated Tokens:** {doc['tokens']:,}")
                    st.write(f"**Uploaded:** {doc['timestamp'][:19]}")
                    
                    # Show preview button in debug mode
                    if st.session_state.debug_enabled:
                        if st.button(f"📖 Preview", key=f"preview_{doc['name']}"):
                            # Find the full content
                            for md_doc in st.session_state.document_markdown:
                                if md_doc['name'] == doc['name']:
                                    st.text_area(
                                        "Full Markdown Content",
                                        md_doc['content'],
                                        height=300,
                                        key=f"content_{doc['name']}"
                                    )
                                    break
            
            if st.button("🗑️ Clear All Documents"):
                st.session_state.uploaded_documents = []
                st.session_state.document_markdown = []
                st.session_state.total_tokens = estimate_tokens(
                    ' '.join([m['content'] for m in st.session_state.messages])
                )
                st.rerun()
        
        st.divider()
        
        # Metrics Section - Collapsed by default
        with st.expander("📊 Metrics", expanded=False):
            # Token usage
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Tokens", f"{st.session_state.total_tokens:,}")
            with col2:
                st.metric("Documents", len(st.session_state.uploaded_documents))
            
            # Agent metrics
            if st.session_state.agent:
                try:
                    stats = st.session_state.agent.get_performance_stats()
                    st.metric("Requests", stats.get('total_requests', 0))
                    st.metric("Avg Response", f"{stats.get('average_response_time', 0):.2f}s")
                    
                    # Error rate with color coding
                    error_rate = stats.get('error_rate', 0)
                    st.metric(
                        "Error Rate",
                        f"{error_rate:.1f}%",
                        delta=None,
                        delta_color="inverse" if error_rate > 5 else "normal"
                    )
                except Exception as e:
                    st.warning(f"Could not load metrics: {e}")
        
        st.divider()
        
        # Debug Controls (only show if debug mode enabled via CLI or toggle)
        if CLI_ARGS.debug or st.session_state.debug_enabled:
            st.header("🔧 Debug Tools")
            
            # Show info if debug mode was enabled via CLI
            if CLI_ARGS.debug:
                st.caption("🔍 Debug mode enabled via `-D` flag")
            
            # Allow toggling debug mode on/off
            st.session_state.debug_enabled = st.toggle("Enable Debug Mode", value=st.session_state.debug_enabled)
            
            if st.session_state.debug_enabled:
                if st.button("📊 Show Agent Status"):
                    st.session_state.show_agent_status = True
                
                if st.button("💾 Export Session Data"):
                    export_session_data()
                
                if st.button("🗑️ Clear Conversation"):
                    st.session_state.messages = []
                    if st.session_state.agent:
                        st.session_state.agent.clear_conversation_history()
                    st.rerun()
                
                st.divider()
                st.caption("⚠️ Emergency Tools")
                if st.button("🔥 Force Clear All Caches", type="primary"):
                    force_clear_all_caches()


def export_session_data():
    """
    Export current session data to a JSON file.
    
    Creates a downloadable JSON file containing conversation history,
    uploaded documents, and session metrics.
    """
    session_data = {
        'timestamp': datetime.now().isoformat(),
        'messages': st.session_state.messages,
        'uploaded_documents': st.session_state.uploaded_documents,
        'total_tokens': st.session_state.total_tokens,
        'agent_state': st.session_state.agent_state
    }
    
    export_path = Path("data/session_export.json")
    export_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(export_path, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    st.success(f"✅ Session data exported to {export_path}")


def render_copy_button(text: str) -> None:
    """Render a copy-to-clipboard button for the given text.
    
    Uses a small HTML/JavaScript snippet (via components.html) to copy the
    latest formatted output (typically the grading report) to the user's
    clipboard.
    """
    if not text:
        return
    import uuid
    import streamlit.components.v1 as components

    button_id = f"copy-btn-{uuid.uuid4().hex}"
    # Use json.dumps to safely embed the text as a JS string literal
    text_js = json.dumps(text)
    components.html(
        f"""
<button id="{button_id}">📋 Copy formatted output</button>
<script>
const textToCopy_{button_id.replace('-', '_')} = {text_js};
const btn_{button_id.replace('-', '_')} = document.getElementById("{button_id}");
if (btn_{button_id.replace('-', '_')}) {{
  btn_{button_id.replace('-', '_')}.onclick = async () => {{
    try {{
      await navigator.clipboard.writeText(textToCopy_{button_id.replace('-', '_')});
      console.log('Formatted output copied to clipboard');
    }} catch (err) {{
      console.error('Failed to copy formatted output:', err);
      alert('Failed to copy formatted output to clipboard.');
    }}
  }};
}}
</script>
""",
        height=60,
    )


def stream_agent_response(user_input: str, document_context: str = ""):
    """
    Synchronous generator that yields text chunks from agent streaming response.
    Wraps the async chat_streaming method to work with Streamlit's st.write_stream.
    
    Args:
        user_input: The user's input message
        document_context: Optional document context to prepend
        
    Yields:
        Text chunks from the streaming response
    """
    current_agent = None
    agent_start_time = {}
    
    try:
        # Build full context if documents provided
        if document_context:
            context_prompt = f"{document_context}\n\n**User Question:**\n{user_input}"
        else:
            context_prompt = user_input
        
        # Create async generator
        async_gen = st.session_state.agent.chat_streaming(context_prompt)
        
        # Convert async generator to sync by running in event loop
        import asyncio
        
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Process streaming events
        while True:
            try:
                # Get next event from async generator
                event = loop.run_until_complete(async_gen.__anext__())
                
                event_type = event.get('type')
                agent_name = event.get('agent', 'assistant')
                
                if event_type == 'status':
                    # Track agent start
                    if agent_name not in agent_start_time:
                        agent_start_time[agent_name] = time.time()
                        current_agent = agent_name
                    
                    # Show only selected high-level status messages
                    content = event.get('content', '')
                    allowed_statuses = {
                        'Classifying request...',
                        'Starting grading workflow...',
                        'Analyzing with grading agent...',
                        'Formatting results...'
                    }
                    if content in allowed_statuses:
                        yield f"\n\n🔄 **{agent_name}**: _{content}_\n\n"
                    
                elif event_type == 'chunk':
                    yield event['content']
                    
                elif event_type == 'complete':
                    # Show concise completion message
                    if agent_name in agent_start_time:
                        duration = time.time() - agent_start_time[agent_name]
                        yield f"\n\n✅ **{agent_name}** completed ({duration:.1f}s)\n\n"
                    
                elif event_type == 'error':
                    yield f"\n\n❌ Error: {event['content']}\n"
                    
            except StopAsyncIteration:
                # End of stream
                break
                
    except Exception as e:
        yield f"\n\n❌ Streaming error: {str(e)}\n"


def render_debug_panel():
    """
    Render the debugging panel with variable viewer and request history.
    
    This panel provides Google APK-style debugging tools including:
    - Variable inspection
    - Request/response tracking
    - Agent state monitoring
    """
    if not st.session_state.debug_enabled:
        return
    
    st.divider()
    
    with st.expander("🔍 Debug Panel", expanded=False):
        tab1, tab2, tab3 = st.tabs(["Variables", "Request History", "Agent State"])
        
        with tab1:
            st.subheader("Variable Viewer")
            
            # Session state variables
            variables = {
                'messages_count': len(st.session_state.messages),
                'documents_loaded': len(st.session_state.uploaded_documents),
                'total_tokens': st.session_state.total_tokens,
                'agent_initialized': st.session_state.agent is not None
            }
            
            for var_name, var_value in variables.items():
                st.markdown(
                    f'<div class="variable-item">'
                    f'<strong>{var_name}:</strong> {var_value}'
                    f'</div>',
                    unsafe_allow_html=True
                )
        
        with tab2:
            st.subheader("Request History")
            
            if st.session_state.request_history:
                for i, req in enumerate(reversed(st.session_state.request_history[-10:])):
                    with st.container():
                        st.write(f"**Request {len(st.session_state.request_history) - i}**")
                        st.code(json.dumps(req, indent=2), language='json')
            else:
                st.info("No requests yet")
        
        with tab3:
            st.subheader("Agent State")
            
            if st.session_state.agent:
                try:
                    status = st.session_state.agent.get_agent_status()
                    st.json(status)
                except Exception as e:
                    st.error(f"Error getting agent status: {e}")
            else:
                st.warning("Agent not initialized")


def render_main_chat():
    """
    Render the main chat interface.
    
    This function creates the central chat area where users interact with
    the Grading Helper, displaying message history and handling new inputs.
    """
    st.title("💬 Grading Helper")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Enable HTML rendering and proper markdown formatting
            st.markdown(message["content"], unsafe_allow_html=True)
            
            # Show metadata in debug mode
            if st.session_state.debug_enabled and "metadata" in message:
                with st.expander("📋 Message Metadata"):
                    st.json(message["metadata"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt, unsafe_allow_html=True)
        
        # Estimate tokens
        user_tokens = estimate_tokens(prompt)
        st.session_state.total_tokens += user_tokens
        
        # Get agent response with streaming
        with st.chat_message("assistant"):
            try:
                start_time = time.time()
                
                # Build document context if available
                document_context = ""
                document_info = []
                
                if st.session_state.document_markdown:
                    context = "\n\n**Available Documents:**\n"
                    is_grading = _is_grading_request(prompt)
                    
                    for doc in st.session_state.document_markdown:
                        raw_content = doc['content']
                        doc_content = raw_content
                        valid_rows = 0
                        skipped_rows = 0

                        # For grading-style prompts, filter markdown down to valid student rows
                        if is_grading:
                            filtered, valid_rows, skipped_rows = _extract_valid_student_rows_from_markdown(raw_content)
                            if valid_rows > 0:
                                doc_content = filtered
                                logger.info(
                                    "Applied student-row filter to %s: %d valid, %d skipped",
                                    doc['name'], valid_rows, skipped_rows,
                                )
                            else:
                                # No valid rows detected; fall back to original content
                                doc_content = raw_content
                                if skipped_rows > 0:
                                    logger.info(
                                        "No valid student rows detected in %s; using original markdown",
                                        doc['name'],
                                    )

                        context += f"\n### {doc['name']}\n{doc_content}\n"
                        
                        # Track document info for debug logging
                        document_info.append({
                            'name': doc['name'],
                            'content_length': len(doc_content),
                            'estimated_tokens': estimate_tokens(doc_content),
                            'valid_student_rows': valid_rows,
                            'skipped_lines': skipped_rows,
                        })
                    
                    document_context = context
                    
                    # Debug logging
                    if st.session_state.debug_enabled:
                        st.info(f"🔍 **Debug Info:** Including {len(st.session_state.document_markdown)} document(s) in context")
                        for info in document_info:
                            extra = ""
                            if _is_grading_request(prompt):
                                extra = f", valid rows: {info['valid_student_rows']}, skipped: {info['skipped_lines']}"
                            st.caption(
                                f"📄 {info['name']}: {info['content_length']:,} chars, ~{info['estimated_tokens']:,} tokens{extra}"
                            )
                
                # Validate input before streaming
                if document_context:
                    context_prompt = f"{document_context}\n\n**User Question:**\n{prompt}"
                    
                    if st.session_state.debug_enabled:
                        total_context_tokens = estimate_tokens(context_prompt)
                        st.caption(f"📊 Total context size: {len(context_prompt):,} chars, ~{total_context_tokens:,} tokens")
                    
                    # Validate only the user's actual prompt
                    from modules.security import InputValidator
                    validator = InputValidator()
                    validation_result = validator.validate_input(prompt)
                    if not validation_result["valid"]:
                        raise InputValidationException(validation_result["error"])
                
                # Stream the response using Streamlit's write_stream
                response = st.write_stream(stream_agent_response(prompt, document_context))
                response_time = time.time() - start_time

                # Render a copy-to-clipboard button for the full formatted response
                render_copy_button(response)

                # Update tokens
                response_tokens = estimate_tokens(response)
                st.session_state.total_tokens += response_tokens
                
                # Store message with metadata
                message_data = {
                    "role": "assistant",
                    "content": response,
                    "metadata": {
                        "response_time": response_time,
                        "tokens": response_tokens,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                st.session_state.messages.append(message_data)
                
                # Log request with document context info
                # Build context_prompt for logging
                context_prompt = document_context + "\n\n**User Question:**\n" + prompt if document_context else prompt
                request_log = {
                    "user_input": prompt,
                    "response": response,
                    "response_time": response_time,
                    "tokens": user_tokens + response_tokens,
                    "timestamp": datetime.now().isoformat(),
                    "documents_used": len(document_info) if document_info else 0,
                    "document_details": document_info if document_info else None,
                    "full_context_length": len(context_prompt),
                    "full_context_tokens": estimate_tokens(context_prompt)
                }
                st.session_state.request_history.append(request_log)
                
            except InputValidationException as e:
                st.error(f"⚠️ Input validation error: {e}")
            except RateLimitException as e:
                st.warning(f"⏱️ {e}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"I encountered an error: {e}"
                })


def main():
    """
    Main application entry point.
    
    Initializes the session state, renders the UI components, and manages
    the application lifecycle.
    """
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main chat area
    render_main_chat()
    
    # Render debug panel
    render_debug_panel()
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.caption(f"🔗 Endpoint: {config.endpoint.split('.')[0]}...")
    with col2:
        st.caption(f"🤖 Model: {config.chat_deployment}")
    with col3:
        if st.session_state.agent:
            uptime_stats = st.session_state.agent.get_performance_stats()
            st.caption(f"⏱️ Uptime: {uptime_stats.get('uptime_formatted', 'N/A')}")


if __name__ == "__main__":
    main()
