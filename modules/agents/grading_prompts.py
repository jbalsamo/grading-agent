"""
Grading Agent Prompt Templates

This module contains prompt templates for the clinical student grading agent.
"""

# User Prompt Template for Clinical Student Grading
CLINICAL_GRADING_TEMPLATE = """Grade all students in the provided Excel spreadsheets using the rubric from {rubric_filename}.
Use the semantic/simile-aware scoring with both safeguards enabled:

1. Count only checked items
2. Ignore rubric clones (template text)

Compare the AI-calculated scores to the Human scores from the file {scores_filename}.

For each student:
- Display a table: AI vs Human scores (PS, DX, PL, Total, Δ)
- List ignored items filtered by safeguards
- Provide a short paragraph summarizing discrepancies and possible reasons (e.g., missed context, phrasing differences)

After scoring all, generate a single report (on-screen or PDF) summarizing every student."""


# Example usage prompt
EXAMPLE_USAGE = """Example Usage:

Grade all students in the provided Excel spreadsheets using the rubric from Patient Jack-Jackie Kimble Scoring Rubric 2025.pdf.
Use the semantic/simile-aware scoring with both safeguards enabled:

1. Count only checked items
2. Ignore rubric clones (template text)

Compare the AI-calculated scores to the Human scores from the file Jack-Jackie Kimble Student Patient Note Scores PCC Block 1.xlsx.

For each student:
- Display a table: AI vs Human scores (PS, DX, PL, Total, Δ)
- List ignored items filtered by safeguards
- Provide a short paragraph summarizing discrepancies and possible reasons (e.g., missed context, phrasing differences)

After scoring all, generate a single report (on-screen or PDF) summarizing every student."""


def get_grading_prompt(rubric_filename: str, scores_filename: str) -> str:
    """
    Generate a grading prompt with specific filenames.
    
    Args:
        rubric_filename: Name of the rubric PDF file
        scores_filename: Name of the student scores Excel file
        
    Returns:
        Formatted grading prompt
    """
    return CLINICAL_GRADING_TEMPLATE.format(
        rubric_filename=rubric_filename,
        scores_filename=scores_filename
    )


# System prompt (for reference - this is already in grading_agent.py)
SYSTEM_PROMPT = """You are grading clinical student patient notes.

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

Use templates where appropriate. If the data is not in a rubric or grade format, return an error and announce that it could not be processed."""
