# CycPep MCP Server

A Model Context Protocol (MCP) server for cyclic peptide computational tools, providing both synchronous and asynchronous APIs for peptide analysis, MCTS training, and peptide design.

## Quick Start

### Start the Server
```bash
# Development mode
mamba run --prefix ./env fastmcp dev src/server.py

# Production mode
mamba run --prefix ./env python src/server.py
```

### Server Information
- **Name**: `cycpep-tools`
- **Version**: 1.0.0
- **Transport**: STDIO
- **Framework**: FastMCP 2.14.1

## Available Tools

### 🚀 Sync Tools (Fast Operations)
- `analyze_cyclic_peptide` - Analyze peptide-protein interactions (~1-10 sec)
- `train_mcts_generate_data` - Generate training data (~1-30 sec)
- `train_mcts_evaluate_model` - Evaluate trained models (~10-60 sec)
- `get_server_info` - Get server and tools information

### ⏱️ Submit Tools (Long Operations)
- `submit_mcts_training` - Train MCTS models (>10 min)
- `submit_peptide_design` - Design peptides with MCTS (>10 min)
- `submit_batch_peptide_analysis` - Batch analysis (>10 min)

### 📊 Job Management
- `get_job_status` - Check job progress
- `get_job_result` - Get completed results
- `get_job_log` - View execution logs
- `cancel_job` - Cancel running jobs
- `list_jobs` - List all jobs

## Example Usage

### Quick Analysis
```python
# Immediate results for fast operations
result = analyze_cyclic_peptide(
    input_file="examples/data/sequences/target.csv",
    pdb_id="6seo",
    suggest_mutations=True
)
```

### Long-Running Design
```python
# Submit background job
job = submit_peptide_design(
    target_id="6seo",
    peptide_length=16,
    iterations=300,
    job_name="design_6seo"
)

# Monitor progress
while get_job_status(job["job_id"])["status"] != "completed":
    time.sleep(30)

# Get results
result = get_job_result(job["job_id"])
```

## Architecture

```
src/
├── server.py              # Main MCP server
├── jobs/
│   ├── manager.py         # Job execution
│   └── store.py           # Job persistence
└── tools/                 # Tool definitions

scripts/                   # Source algorithms
├── analyze_peptide.py     # Peptide analysis
├── train_mcts.py         # MCTS training
├── design_peptide.py     # Peptide design
└── lib/                  # Shared utilities

jobs/                     # Job outputs
└── {job_id}/
    ├── metadata.json     # Job info
    ├── job.log          # Execution log
    └── outputs/         # Result files
```

## Key Features

- **🔄 Dual API Design**: Sync for fast ops, Submit for long jobs
- **📝 Job Persistence**: Jobs survive server restarts
- **🔍 Comprehensive Logging**: Full execution tracking
- **⚡ Thread-Based Execution**: Concurrent job processing
- **🛡️ Error Recovery**: Structured error responses
- **🎯 LLM-Optimized**: Clear tool descriptions and workflows

## Documentation

- **Complete Guide**: `reports/step6_mcp_tools.md`
- **Script Documentation**: `scripts/README.md`
- **Testing**: `test_tools_direct.py`, `test_mcp_server.py`

## Dependencies

- **FastMCP** 2.14.1 - MCP server framework
- **Loguru** - Logging
- **NumPy/Pandas** - Data processing
- **Python 3.10+** - Runtime environment

## Tested & Verified

✅ Server starts without errors
✅ All sync tools work correctly
✅ Submit tools execute successfully
✅ Job management fully functional
✅ Error handling provides useful feedback
✅ Documentation comprehensive

Ready for production use with Claude and other MCP clients!