"""
Grading Agent - Specialized for educational assessment and grading tasks.
"""
from typing import Dict, Any, TYPE_CHECKING, AsyncGenerator, Optional
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..config import config
import logging

if TYPE_CHECKING:
    from ..conversation_history import ConversationHistory

logger = logging.getLogger(__name__)

class GradingAgent:
    """Specialized agent for educational assessment and grading."""
    
    def __init__(self):
        """Initialize the grading agent."""
        self.llm = self._create_llm()
        self.agent_type = "grading"
        logger.info("Grading Agent initialized")
    
    def _create_llm(self) -> AzureChatOpenAI:
        """Create Azure OpenAI LLM instance for grading."""
        return AzureChatOpenAI(
            **config.get_azure_openai_kwargs(),
            temperature=1.0,  # Explicitly set to 1.0 as required by gpt-5 model
        )
    
    def process(self, user_input: str) -> str:
        """Process grading and assessment requests."""
        try:
            system_message = """You are grading clinical student patient notes.

The rubric items and their text are derived exactly from the rubric PDF.
Exclusions: "NONE OF THE ABOVE" and "COMMENTS" are not scored or included in totals.

Matching & Scoring Logic:
- Use semantic and simile-aware matching (not just keyword or literal).
- Match phrases even when meaning is equivalent (e.g., "shooting pain" ≈ "pain radiates down leg").
- Count multiple rubric matches from a single phrase when appropriate.
- Use these thresholds:
  * semantic similarity ≥ 0.55
  * token overlap ≥ 0.35
  * combined ≥ 0.50

Safeguards:
- Checked-only safeguard: Count only rubric items actually marked/checked by the evaluator in the spreadsheet.
- Student-content safeguard: Ignore rubric phrases that are identical or near-identical copies of the official rubric text (≥ 0.80 similarity).

Output per Student:
1. Header table:
   | Section | AI Score | Human Score | Max | Δ |
2. Itemized rubric list with ✓ / ✗ for each rubric line.
3. Ignored or unscored phrases (due to safeguards).
4. Brief narrative explaining differences (AI vs Human) and improvement feedback.

Use templates where appropriate. If a particular line or section does not contain student-level rubric or score data, do not treat it as an error; instead, emit a brief **Notice:** explaining that the content does not contain student data and has been skipped, then continue grading any valid student rows. Only if the entire input cannot be interpreted as rubric/grade data should you return an actual error and clearly state that grading could not be performed.

For general educational tasks:
- Grading assignments, essays, and exams
- Providing detailed feedback on student work
- Creating rubrics and assessment criteria
- Analyzing learning outcomes
- Identifying areas for improvement
- Maintaining consistency in grading standards

Always be fair, objective, and constructive in your assessments. Provide specific examples and actionable feedback."""
            
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            logger.info("Grading agent processed request successfully")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in grading agent: {e}")
            return f"I apologize, but I encountered an error during grading assessment: {str(e)}"
    
    def get_status(self) -> str:
        """Get the status of the grading agent."""
        return "active"
    
    def process_with_history(self, user_input: str, conversation_history: 'ConversationHistory') -> str:
        """Process grading and assessment requests with conversation history context."""
        try:
            system_message = """You are grading clinical student patient notes.

The rubric items and their text are derived exactly from the rubric PDF.
Exclusions: "NONE OF THE ABOVE" and "COMMENTS" are not scored or included in totals.

Matching & Scoring Logic:
- Use semantic and simile-aware matching (not just keyword or literal).
- Match phrases even when meaning is equivalent (e.g., "shooting pain" ≈ "pain radiates down leg").
- Count multiple rubric matches from a single phrase when appropriate.
- Use these thresholds:
  * semantic similarity ≥ 0.55
  * token overlap ≥ 0.35
  * combined ≥ 0.50

Safeguards:
- Checked-only safeguard: Count only rubric items actually marked/checked by the evaluator in the spreadsheet.
- Student-content safeguard: Ignore rubric phrases that are identical or near-identical copies of the official rubric text (≥ 0.80 similarity).

Output per Student:
1. Header table:
   | Section | AI Score | Human Score | Max | Δ |
2. Itemized rubric list with ✓ / ✗ for each rubric line.
3. Ignored or unscored phrases (due to safeguards).
4. Brief narrative explaining differences (AI vs Human) and improvement feedback.

Use templates where appropriate. If the data is not in a rubric or grade format, return an error and announce that it could not be processed.

You have access to the conversation history, so you can reference previous grading sessions, 
maintain consistency across multiple student assessments, and build upon earlier feedback. 
Use this context to provide more coherent and consistent grading across all students.

For general educational tasks:
- Grading assignments, essays, and exams
- Providing detailed feedback on student work
- Creating rubrics and assessment criteria
- Analyzing learning outcomes
- Identifying areas for improvement
- Maintaining consistency in grading standards

Always be fair, objective, and constructive in your assessments. Provide specific examples and actionable feedback."""
            
            # Get conversation history messages
            history_messages = conversation_history.get_langchain_messages()
            
            # Create current message set
            current_messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_input)
            ]
            
            # Combine history with current messages
            all_messages = [current_messages[0]] + history_messages + [current_messages[1]]
            
            response = self.llm.invoke(all_messages)
            logger.info("Grading agent processed request with conversation history successfully")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in grading agent with history: {e}")
            return f"I apologize, but I encountered an error during grading assessment: {str(e)}"
    
    async def stream_process(
        self,
        user_input: str,
        conversation_history: Optional['ConversationHistory'] = None
    ) -> AsyncGenerator[str, None]:
        """
        Process grading with streaming output.
        
        Args:
            user_input: Grading request
            conversation_history: Optional conversation history
            
        Yields:
            String chunks of the grading response
        """
        try:
            # Use the same system message (PRESERVED from process_with_history)
            system_message = """You are grading clinical student patient notes.

The rubric items and their text are derived exactly from the rubric PDF.
Exclusions: "NONE OF THE ABOVE" and "COMMENTS" are not scored or included in totals.

Matching & Scoring Logic:
- Use semantic and simile-aware matching (not just keyword or literal).
- Match phrases even when meaning is equivalent (e.g., "shooting pain" ≈ "pain radiates down leg").
- Count multiple rubric matches from a single phrase when appropriate.
- Use these thresholds:
  * semantic similarity ≥ 0.55
  * token overlap ≥ 0.35
  * combined ≥ 0.50

Safeguards:
- Checked-only safeguard: Count only rubric items actually marked/checked by the evaluator in the spreadsheet.
- Student-content safeguard: Ignore rubric phrases that are identical or near-identical copies of the official rubric text (≥ 0.80 similarity).

Output per Student:
1. Header table:
   | Section | AI Score | Human Score | Max | Δ |
2. Itemized rubric list with ✓ / ✗ for each rubric line.
3. Ignored or unscored phrases (due to safeguards).
4. Brief narrative explaining differences (AI vs Human) and improvement feedback.

Use templates where appropriate. If the data is not in a rubric or grade format, return an error and announce that it could not be processed.

You have access to the conversation history, so you can reference previous grading sessions,
maintain consistency across multiple student assessments, and build upon earlier feedback.
Use this context to provide more coherent and consistent grading across all students.

For general educational tasks:
- Grading assignments, essays, and exams
- Providing detailed feedback on student work
- Creating rubrics and assessment criteria
- Analyzing learning outcomes
- Identifying areas for improvement
- Maintaining consistency in grading standards

Always be fair, objective, and constructive in your assessments. Provide specific examples and actionable feedback."""
            
            if conversation_history:
                history_messages = conversation_history.get_langchain_messages()
                all_messages = [
                    SystemMessage(content=system_message)
                ] + history_messages + [
                    HumanMessage(content=user_input)
                ]
            else:
                all_messages = [
                    SystemMessage(content=system_message),
                    HumanMessage(content=user_input)
                ]
            
            # Stream response
            async for chunk in self.llm.astream(all_messages):
                if chunk.content:
                    yield chunk.content
            
            logger.info("Grading agent completed streaming")
            
        except Exception as e:
            logger.error(f"Error in grading agent streaming: {e}")
            yield f"I apologize, but I encountered an error during grading: {str(e)}"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the grading agent."""
        return {
            "agent_type": self.agent_type,
            "capabilities": [
                "Clinical student patient note grading",
                "Semantic and simile-aware scoring (similarity ≥ 0.55, token overlap ≥ 0.35)",
                "Rubric-based assessment with safeguards",
                "AI vs Human score comparison and analysis",
                "Checked-only safeguard enforcement",
                "Student-content safeguard (anti-template copying)",
                "Itemized rubric scoring with ✓/✗ indicators",
                "Discrepancy analysis and improvement feedback",
                "Assignment and essay grading",
                "Detailed feedback generation",
                "Rubric creation and application",
                "Learning outcome analysis",
                "Educational assessment design",
                "Conversation history awareness for consistent grading"
            ],
            "specialization": "Clinical student note grading with semantic matching and educational assessment",
            "temperature": 1.0,
            "scoring_thresholds": {
                "semantic_similarity": 0.55,
                "token_overlap": 0.35,
                "combined_minimum": 0.50,
                "template_clone_threshold": 0.80
            }
        }
