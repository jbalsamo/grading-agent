# Examples

This directory contains example scripts demonstrating different use cases of the grading agent system.

## 🆕 Streaming Examples

### 1. Streaming Demo (`streaming_demo.py`) ⭐ NEW
Comprehensive demonstration of real-time streaming capabilities:
- Basic streaming with visual feedback
- Streaming with progress tracking
- Streaming cancellation
- Blocking vs streaming comparison

```bash
python examples/streaming_demo.py
```

### 2. Grading Workflow Demo (`grading_workflow_demo.py`) ⭐ NEW
Multi-agent grading pipeline demonstration:
- Automatic grading workflow (Grading → Formatting → Chat)
- Visual progress tracking
- Agent-by-agent comparison
- FormattingAgent showcase with table generation

```bash
python examples/grading_workflow_demo.py
```

## Original Examples

### 3. Agent Comparison (`agent_comparison.py`)
Demonstrates the differences between specialized agents (Chat, Grading, Analysis) by showing how each agent responds to the same query differently.

**Features:**
- Side-by-side agent comparison
- Response analysis (length, processing time, focus)
- Capability comparison
- Performance metrics

**Usage:**
```bash
python examples/agent_comparison.py
```

## Running Examples

1. **Prerequisites:**
   - Ensure the Master Agent System is properly configured
   - Run `python validate_config.py` to verify setup
   - Make sure all dependencies are installed

2. **Execute Examples:**
   ```bash
   # From the project root directory
   python examples/batch_processing.py
   python examples/agent_comparison.py
   ```

3. **Expected Output:**
   - Each example will display progress and results in the terminal
   - Some examples may generate output files (JSON reports, etc.)

## Example Scenarios

### Batch Processing Use Cases
- **Content Generation**: Process multiple content requests
- **Data Analysis**: Analyze multiple datasets
- **Educational Assessment**: Grade multiple assignments
- **System Testing**: Validate system performance

### Agent Comparison Use Cases
- **Response Quality**: Compare agent response quality
- **Specialization Testing**: Verify agent specialization
- **Performance Benchmarking**: Measure processing times
- **Capability Analysis**: Understand agent strengths

## Customization

You can modify these examples to:
- Add your own test queries
- Test specific agent combinations
- Implement custom analysis metrics
- Export results in different formats

## Integration

These examples can serve as templates for:
- Building automated testing suites
- Creating performance monitoring tools
- Developing custom agent workflows
- Implementing batch processing systems

## Troubleshooting

If examples fail to run:
1. Check that you're running from the project root directory
2. Verify your `.env` configuration with `python validate_config.py`
3. Ensure all Python dependencies are installed
4. Check the console output for specific error messages
