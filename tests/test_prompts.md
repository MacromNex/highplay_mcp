# Test Prompts for CycPep MCP Server Integration

This file contains a comprehensive set of test prompts to validate the MCP server integration with Claude Code and other LLM clients.

## Tool Discovery Tests

### Prompt 1: List All Tools
```
What MCP tools are available for cyclic peptides? Give me a brief description of each tool and categorize them by function.
```

**Expected Response:**
- Server should list all 12 tools
- Tools should be categorized into sync, submit, and job management
- Brief descriptions should be provided

### Prompt 2: Tool Details
```
Explain how to use the analyze_cyclic_peptide tool, including all required and optional parameters.
```

**Expected Response:**
- Detailed parameter explanation
- Examples of usage
- Input/output format description

## Sync Tool Tests

### Prompt 3: Server Information
```
Get information about the cyclic peptide MCP server and show me what workflows are available.
```

**Expected Response:**
- Server name, version, description
- Available tool categories
- Example workflows

### Prompt 4: Property Calculation with Sequence
```
Generate training data for MCTS with the following parameters:
- Peptide length: 10
- Number of samples: 50
- Output directory: test_output

Then tell me what was generated.
```

**Expected Response:**
- Successful data generation
- File paths and statistics
- Summary of generated training data

### Prompt 5: Peptide Analysis
```
Analyze a cyclic peptide interaction using these inputs:
- Peptide sequence: "GRGDSP"
- Receptor sequence: "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR"
- Suggest mutations: true

What binding metrics and mutation suggestions do you get?
```

**Expected Response:**
- Analysis results with binding metrics
- Mutation suggestions if available
- Clear status and any limitations

### Prompt 6: Error Handling Test
```
Try to analyze a cyclic peptide without providing any input parameters. What happens?
```

**Expected Response:**
- Graceful error handling
- Clear error message explaining missing inputs
- Suggestions for correct usage

## Submit API Tests

### Prompt 7: Submit MCTS Training Job
```
Submit an MCTS training job with these parameters:
- Peptide length: 12
- Epochs: 5
- Batch size: 16
- Learning rate: 0.01
- Job name: "test_training_run"

Then check the job status immediately.
```

**Expected Response:**
- Job submission confirmation with job ID
- Initial job status (pending or running)
- Instructions for monitoring progress

### Prompt 8: Submit Peptide Design Job
```
Submit a peptide design optimization job:
- Receptor sequence: "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR"
- Peptide length: 8
- Iterations: 100
- Job name: "design_test"

Track this job until completion or give me the job ID to monitor later.
```

**Expected Response:**
- Job submission with job ID
- Job tracking information
- Expected completion time or monitoring instructions

### Prompt 9: Job Management Workflow
```
1. List all currently submitted jobs
2. Show me the status of the most recent job
3. Get the last 20 lines of logs from that job
4. If any job is completed, show me its results
```

**Expected Response:**
- List of jobs with their IDs and status
- Detailed status of specific job
- Log output showing progress
- Results if available

### Prompt 10: Batch Processing
```
Submit a batch analysis for multiple peptide scenarios. Since I don't have a CSV file, can you suggest how to structure the input and what the expected output would be?
```

**Expected Response:**
- Input file format explanation
- Expected batch processing workflow
- Output structure description

## End-to-End Scenarios

### Prompt 11: Complete Drug Discovery Workflow
```
I want to design a cyclic peptide that binds to a specific protein target. Walk me through the complete workflow:

1. Start by generating some training data for MCTS (peptide length 10, 100 samples)
2. Train a model (just 2 epochs for testing)
3. Use the model for peptide design optimization
4. Analyze the results

Guide me through each step and show me what tools to use.
```

**Expected Response:**
- Step-by-step workflow guidance
- Tool usage for each step
- Expected outcomes and next steps
- Clear progression through the pipeline

### Prompt 12: Research Scenario
```
I'm researching cyclic peptide conformational dynamics. I need to:

1. Generate a diverse set of cyclic peptide sequences (length 12-16)
2. Submit structure prediction jobs for the most promising candidates
3. Analyze the binding properties
4. Track all jobs and compile results

Help me set up this research pipeline using the available tools.
```

**Expected Response:**
- Research workflow design
- Multiple job submissions
- Job tracking strategy
- Data compilation approach

### Prompt 13: High-Throughput Screening
```
I want to screen a library of cyclic peptides for drug-like properties. What's the best way to:

1. Generate a diverse peptide library
2. Calculate properties for each peptide
3. Filter by drug-likeness criteria
4. Optimize the most promising candidates

Show me how to use the MCP tools for this screening pipeline.
```

**Expected Response:**
- Library generation strategy
- Batch processing approach
- Filtering and optimization workflow
- Tool combinations for efficiency

### Prompt 14: Model Development and Validation
```
I need to develop a new MCTS model for peptide design. Help me:

1. Generate appropriate training data
2. Train the model with proper validation
3. Evaluate model performance
4. Use the model for actual peptide design

Walk me through this machine learning pipeline.
```

**Expected Response:**
- ML pipeline design
- Training data requirements
- Model validation approach
- Performance evaluation methods

## Error and Edge Case Tests

### Prompt 15: Invalid Inputs
```
Test the robustness of the system by:

1. Trying to analyze a peptide with invalid characters in the sequence
2. Submitting a training job with impossible parameters (negative epochs)
3. Checking status of a non-existent job ID
4. Canceling a job that doesn't exist

Show me how the system handles these error cases.
```

**Expected Response:**
- Graceful error handling for each case
- Informative error messages
- Suggestions for correct usage
- No system crashes or undefined behavior

### Prompt 16: Resource Management
```
Submit multiple jobs simultaneously to test resource management:

1. Submit 3 MCTS training jobs with different parameters
2. Submit 2 peptide design jobs
3. List all jobs and their status
4. Try to cancel one of the running jobs
5. Monitor resource usage and job queue

How does the system handle concurrent jobs?
```

**Expected Response:**
- Successful multiple job submission
- Queue management demonstration
- Job cancellation functionality
- Resource usage information

## Performance and Scalability Tests

### Prompt 17: Large-Scale Processing
```
Test the system's capacity by:

1. Generating a large training dataset (1000+ samples)
2. Submitting a long-running optimization job (500+ iterations)
3. Processing a batch of 50+ peptides
4. Monitoring system performance during heavy load

What are the practical limits of the system?
```

**Expected Response:**
- Large-scale job handling
- Performance monitoring
- System limits identification
- Optimization suggestions

### Prompt 18: Integration Validation
```
Validate the complete MCP integration by using all major tool categories in sequence:

1. Get server information
2. Generate training data (sync tool)
3. Submit a training job (async tool)
4. Monitor job progress (job management)
5. Analyze results when complete
6. Submit follow-up design job
7. List and manage all jobs

This tests the full integration ecosystem.
```

**Expected Response:**
- Seamless tool integration
- Proper data flow between tools
- Consistent state management
- Complete workflow execution

## Documentation and Help Tests

### Prompt 19: Self-Documentation
```
Help me understand:

1. What file formats does the system accept?
2. What are the computational requirements?
3. How long do different operations typically take?
4. What are the best practices for using these tools?

Provide comprehensive usage guidance.
```

**Expected Response:**
- File format specifications
- Computational requirements
- Expected timing for operations
- Best practices and optimization tips

### Prompt 20: Troubleshooting
```
I'm having issues with the cyclic peptide tools. Help me diagnose:

1. Server connectivity problems
2. Job submission failures
3. Slow performance issues
4. Output interpretation problems

What troubleshooting steps should I follow?
```

**Expected Response:**
- Systematic troubleshooting guide
- Common issues and solutions
- Diagnostic tools and commands
- Contact information for support

## Success Criteria for Each Prompt

For each test prompt, the following criteria should be met:

1. **Responsiveness**: Server responds within reasonable time (<30s for sync, immediate job submission for async)
2. **Accuracy**: Responses contain correct and relevant information
3. **Completeness**: All requested information is provided
4. **Error Handling**: Graceful handling of invalid inputs or error conditions
5. **Consistency**: Similar operations produce consistent results
6. **Documentation**: Clear explanation of what's happening and next steps
7. **Integration**: Seamless integration between different tools and operations

## Notes for Testers

- Test prompts can be run in any order
- Some prompts depend on previous job submissions (use actual job IDs)
- Error cases should not crash the server or client
- Performance tests may take longer to complete
- Document any unexpected behaviors or limitations discovered
- Verify that MCP server remains responsive throughout testing