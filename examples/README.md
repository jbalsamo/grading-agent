# Master Agent System Examples

This directory contains example scripts demonstrating various features and capabilities of the Master Agent System.

## Available Examples

### 1. `batch_processing.py`
Demonstrates how to process multiple requests programmatically using the Master Agent System.

**Features:**
- Batch processing of different request types
- Performance timing and monitoring
- Results export to JSON
- Error handling and reporting

**Usage:**
```bash
python examples/batch_processing.py
```

### 2. `agent_comparison.py`
Compares how different specialized agents respond to the same query.

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
