"""
Formatting Agent - Specialized for converting grading results to spreadsheet format.

This agent takes raw grading results and formats them into well-structured
markdown tables suitable for display or export.
"""
from typing import Dict, Any, Optional, TYPE_CHECKING, AsyncGenerator
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..config import config
import logging
import json

if TYPE_CHECKING:
    from ..conversation_history import ConversationHistory

logger = logging.getLogger(__name__)

# System prompt for formatting agent (PRESERVE THIS EXACTLY)
FORMATTING_SYSTEM_PROMPT = """You are a specialized formatting agent that converts grading results into professional, well-structured grading reports.

Your responsibilities:
- Convert grading results into clear, professional reports with distinct sections
- Calculate and display TOTAL GRADE as percentage and points
- Organize data with proper headers and visual hierarchy
- Format scores, deltas, and rubric items consistently
- Create markdown tables that render beautifully in Streamlit
- Maintain data integrity during formatting

REPORT STRUCTURE (Follow this order exactly):

1. **STUDENT GRADING REPORT** (Header)
   - If student info available, show: Student Name/ID, Date, etc.

2. **📊 GRADE SUMMARY** (Primary table - most important!)
   | Metric | Value |
   |:-------|------:|
   | Total Score | XX / YY points |
   | Percentage | XX.X% |
   | Grade Status | Pass/Fail/etc |

3. **📋 SECTION SCORES** (Detailed breakdown)
   | Section | AI Score | Human Score | Max Points | Δ | Status |
   |:--------|-------:|-----------:|---------:|:--:|:-----:|
   | Section name | X | Y | Z | ±N | ✅/⚠️/❌ |
   | **TOTALS** | **X** | **Y** | **Z** | **-** | **-** |

4. **✓ RUBRIC ITEMS** (What was checked)
   | Item | Checked | Points |
   |:-----|:-------:|-------:|
   | Item description | ✓/✗ | N |

5. **ℹ️ ADDITIONAL NOTES** (If applicable)
   - Ignored items
   - Missing requirements
   - Special conditions

Formatting Rules:
1. Use bold headers with emoji for each section (📊, 📋, ✓, ℹ️)
2. TOTAL SCORE must be prominently displayed at the top
3. Calculate percentage: (Total Score / Max Points) × 100
4. Scores should be right-aligned
5. Deltas (Δ): Show ±N with emoji (✅ perfect match ±0-1, ⚠️ close ±2-5, ❌ large gap ±6+)
6. Use horizontal rules (---) between major sections
7. Rubric items: ✓ (checked/correct), ✗ (not checked/incorrect)
8. Preserve all data from grading results
9. For multiple students, create complete separate reports for each

Visual Polish:
- Use **bold** for totals and important values
- Align numbers right for easier comparison
- Keep tables clean and readable
- Add blank lines between sections for clarity

Always format data clearly, professionally, and ready for presentation or export."""


class FormattingAgent:
    """Specialized agent for formatting grading results as spreadsheets."""
    
    def __init__(self):
        """Initialize the formatting agent."""
        self.llm = self._create_llm()
        self.agent_type = "formatting"
        logger.info("Formatting Agent initialized")
    
    def _create_llm(self) -> AzureChatOpenAI:
        """Create Azure OpenAI LLM instance for formatting."""
        return AzureChatOpenAI(
            **config.get_azure_openai_kwargs(),
            temperature=1.0,  # Explicitly set to 1.0 as required by gpt-5 model
        )
    
    def process(self, grading_results: Any) -> str:
        """
        Process grading results and format as spreadsheet (non-streaming).
        
        Args:
            grading_results: Dictionary or string containing grading data to format
            
        Returns:
            Formatted markdown string with tables and structure
        """
        try:
            # Handle both dict and string inputs
            if isinstance(grading_results, dict):
                results_text = json.dumps(grading_results, indent=2)
            else:
                results_text = str(grading_results)
            
            user_message = f"""Format as professional grading report:

{results_text}

REQUIRED:
1. 📊 GRADE SUMMARY: Total (X/Y pts), Percentage, Status
2. 📋 SECTION SCORES: Section | AI | Human | Max | Δ | Status (+ TOTALS row)
3. ✓ RUBRIC ITEMS: Item | Checked | Points
4. ℹ️ NOTES: Additional info if any

Follow system prompt structure. Bold totals."""
            
            messages = [
                SystemMessage(content=FORMATTING_SYSTEM_PROMPT),
                HumanMessage(content=user_message)
            ]
            
            response = self.llm.invoke(messages)
            logger.info("Formatting agent processed results successfully")
            return response.content
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in formatting agent: {error_msg}")
            
            # Provide helpful error message for timeouts
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return """## ⚠️ Formatting Timeout
                
The formatting request took too long. Here's the raw grading data:

""" + results_text + """

**Tip:** For large grading outputs, consider processing fewer students at once."""
            
            return f"Error formatting results: {error_msg}"
    
    async def stream_process(
        self, 
        grading_results: Any,
        conversation_history: Optional['ConversationHistory'] = None
    ) -> AsyncGenerator[str, None]:
        """
        Process grading results with streaming output.
        
        Args:
            grading_results: Dictionary or string containing grading data to format
            conversation_history: Optional conversation history (for future use)
            
        Yields:
            String chunks of formatted output
        """
        try:
            # Handle both dict and string inputs
            if isinstance(grading_results, dict):
                results_text = json.dumps(grading_results, indent=2)
            else:
                results_text = str(grading_results)
            
            user_message = f"""Format as professional grading report:

{results_text}

REQUIRED:
1. 📊 GRADE SUMMARY: Total (X/Y pts), Percentage, Status
2. 📋 SECTION SCORES: Section | AI | Human | Max | Δ | Status (+ TOTALS row)
3. ✓ RUBRIC ITEMS: Item | Checked | Points
4. ℹ️ NOTES: Additional info if any

Follow system prompt structure. Bold totals."""
            
            messages = [
                SystemMessage(content=FORMATTING_SYSTEM_PROMPT),
                HumanMessage(content=user_message)
            ]
            
            # Stream the response
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    yield chunk.content
            
            logger.info("Formatting agent completed streaming")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in formatting agent streaming: {error_msg}")
            
            # Provide helpful error message for timeouts
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                yield "## ⚠️ Formatting Timeout\n\n"
                yield "The formatting request took too long. Here's the raw grading data:\n\n"
                yield results_text + "\n\n"
                yield "**Tip:** For large grading outputs, consider processing fewer students at once."
            else:
                yield f"Error formatting results: {error_msg}"
    
    def format_grading_results(
        self, 
        results: Any
    ) -> str:
        """
        Specialized method for grading result formatting.
        Alias for process() method for clarity.
        
        Args:
            results: Grading results dictionary or string
            
        Returns:
            Formatted markdown string
        """
        return self.process(results)
    
    def get_status(self) -> str:
        """Get the status of the formatting agent."""
        return "active"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the formatting agent."""
        return {
            "agent_type": self.agent_type,
            "capabilities": [
                "Convert grading data to markdown tables",
                "Create spreadsheet-style layouts",
                "Format scores and deltas consistently",
                "Generate rubric item lists",
                "Streaming output support"
            ],
            "specialization": "Converting grading data to structured spreadsheet formats",
            "temperature": "default"  # Uses model default for compatibility
        }
