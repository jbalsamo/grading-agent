# Clinical Student Grading Guide

This guide explains how to use the Grading Agent for clinical student patient note assessment.

## Overview

The Grading Agent is specifically designed to grade clinical student patient notes using semantic and simile-aware matching with built-in safeguards to ensure fair and accurate scoring.

## System Capabilities

### Scoring Algorithm
- **Semantic Matching**: Understands meaning, not just keywords
- **Simile-Aware**: Recognizes equivalent phrases (e.g., "shooting pain" ≈ "pain radiates down leg")
- **Multi-Match**: Can count multiple rubric items from a single phrase when appropriate

### Scoring Thresholds
- Semantic similarity: **≥ 0.55**
- Token overlap: **≥ 0.35**
- Combined minimum: **≥ 0.50**
- Template clone threshold: **≥ 0.80** (for filtering)

### Safeguards

1. **Checked-Only Safeguard**
   - Counts only rubric items actually marked/checked by the evaluator
   - Prevents scoring unchecked items

2. **Student-Content Safeguard**
   - Ignores phrases that are near-identical copies of rubric text
   - Prevents students from scoring points by copying the rubric template
   - Threshold: ≥ 0.80 similarity to rubric text

## Required Files

To grade clinical students, you need:

1. **Rubric PDF**: Contains the official grading rubric
   - Example: `Patient Jack-Jackie Kimble Scoring Rubric 2025.pdf`

2. **Student Scores Excel**: Contains student submissions and human grader scores
   - Example: `Jack-Jackie Kimble Student Patient Note Scores PCC Block 1.xlsx`

## How to Use

### Via StreamLit Web Interface

1. **Upload Documents**
   ```
   - Upload the rubric PDF
   - Upload the student scores Excel file
   ```

2. **Use the Grading Prompt Template**
   ```
   Grade all students in the provided Excel spreadsheets using the rubric from [RUBRIC_FILENAME].
   Use the semantic/simile-aware scoring with both safeguards enabled:

   1. Count only checked items
   2. Ignore rubric clones (template text)

   Compare the AI-calculated scores to the Human scores from the file [SCORES_FILENAME].

   For each student:
   - Display a table: AI vs Human scores (PS, DX, PL, Total, Δ)
   - List ignored items filtered by safeguards
   - Provide a short paragraph summarizing discrepancies and possible reasons

   After scoring all, generate a single report summarizing every student.
   ```

3. **Review Results**
   - The agent will generate a report for each student
   - Compare AI scores vs Human scores
   - Review discrepancies and feedback

### Via CLI

1. **Start the CLI**
   ```bash
   python main.py
   ```

2. **Paste the Grading Prompt**
   - Replace `[RUBRIC_FILENAME]` and `[SCORES_FILENAME]` with your actual filenames
   - The documents must be uploaded first via the web interface or referenced in accessible locations

### Programmatic Usage

```python
from modules.agents.grading_prompts import get_grading_prompt
from modules.master_agent import MasterAgent

# Initialize agent
agent = MasterAgent()

# Generate prompt
prompt = get_grading_prompt(
    rubric_filename="Patient Jack-Jackie Kimble Scoring Rubric 2025.pdf",
    scores_filename="Jack-Jackie Kimble Student Patient Note Scores PCC Block 1.xlsx"
)

# Get grading results
response = agent.chat(prompt)
print(response)
```

## Output Format

For each student, the agent provides:

### 1. Score Comparison Table
```
| Section | AI Score | Human Score | Max | Δ   |
|---------|----------|-------------|-----|-----|
| PS      | 8        | 7           | 10  | +1  |
| DX      | 12       | 13          | 15  | -1  |
| PL      | 9        | 9           | 12  | 0   |
| Total   | 29       | 29          | 37  | 0   |
```

### 2. Itemized Rubric List
```
✓ Patient presents with chest pain
✓ Pain radiates to left arm
✗ Shortness of breath noted
✓ History of hypertension
```

### 3. Ignored Items
```
Ignored due to safeguards:
- "The patient's chief complaint" (template clone, similarity: 0.85)
- "History of present illness" (not checked in evaluator spreadsheet)
```

### 4. Narrative Summary
```
The AI score matches the human score (29/37). The +1 in PS was due to 
semantic matching of "severe chest discomfort" with "chest pain" in the 
rubric. The -1 in DX occurred because the human grader counted "possible 
MI" while the AI required more specific diagnostic terminology. Overall, 
the student demonstrated strong documentation skills with minor gaps in 
diagnostic precision.
```

## Error Handling

If the uploaded files are not in the correct format:

```
❌ Error: The provided data is not in a valid rubric or grading format.
Please upload:
1. A rubric PDF with grading criteria
2. An Excel file with student scores and submissions
```

## Sections Explanation

- **PS (Problem Statement)**: Patient presentation and chief complaint
- **DX (Diagnosis)**: Diagnostic reasoning and differential diagnosis
- **PL (Plan)**: Treatment plan and follow-up care
- **Total**: Sum of all section scores
- **Δ (Delta)**: Difference between AI and Human scores

## Best Practices

1. **Upload Clear Documents**: Ensure PDFs are readable and Excel files are properly formatted
2. **Review Discrepancies**: Always review cases where AI and Human scores differ significantly
3. **Provide Context**: Include all relevant rubric items and grading criteria
4. **Batch Processing**: Grade multiple students in one session for consistency
5. **Export Results**: Use the export feature to save grading reports for record-keeping

## Troubleshooting

### Issue: Agent not finding rubric items
**Solution**: Ensure the rubric PDF is clearly formatted and uploaded correctly

### Issue: All scores are 0
**Solution**: Check that the Excel file has checked items marked properly

### Issue: Too many template clones flagged
**Solution**: Verify the template clone threshold (0.80) is appropriate for your use case

### Issue: Semantic matches seem incorrect
**Solution**: Review the similarity thresholds and adjust if needed (requires code modification)

## Support

For issues or questions about the grading agent:
1. Check this guide
2. Review the agent capabilities with the `status` command
3. Enable debug mode (`-D` flag) to see detailed matching information
4. Consult the main README.md for general troubleshooting

## Advanced Configuration

### Adjusting Thresholds

To modify scoring thresholds, edit `modules/agents/grading_agent.py`:

```python
# Current thresholds in system prompt
semantic_similarity ≥ 0.55
token_overlap ≥ 0.35
combined ≥ 0.50
template_clone ≥ 0.80
```

### Custom Prompts

Use `modules/agents/grading_prompts.py` to create custom prompt templates:

```python
from modules.agents.grading_prompts import get_grading_prompt

custom_prompt = get_grading_prompt(
    rubric_filename="My_Custom_Rubric.pdf",
    scores_filename="My_Student_Scores.xlsx"
)
```

## Version History

- **v1.0**: Initial clinical grading implementation with semantic matching and safeguards
