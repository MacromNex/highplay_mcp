# CycPep MCP Server Installation Guide

## Quick Start

### Prerequisites
```bash
# Ensure you have Claude CLI installed
which claude

# Ensure you have Python environment with required dependencies
python -c "import fastmcp, loguru; print('Dependencies OK')"
```

### 1. Register MCP Server
```bash
# Navigate to project directory
cd /path/to/highplay_mcp

# Register with Claude Code (use absolute paths)
claude mcp add cycpep-tools -- $(which python) $(pwd)/src/server.py
```

### 2. Verify Installation
```bash
# Check server is registered and connected
claude mcp list

# Should show:
# cycpep-tools: /path/to/python /path/to/src/server.py - ✓ Connected
```

### 3. Test Basic Functionality
Start Claude Code and test:
```
What tools are available from cycpep-tools?
```

You should see 12 tools categorized as:
- Job Management Tools (5)
- Synchronous Tools (3)
- Asynchronous Submit Tools (3)
- Information Tools (1)

## Available Tools

### Quick Reference
| Tool | Type | Description |
|------|------|-------------|
| `get_server_info` | Info | Server information and usage examples |
| `analyze_cyclic_peptide` | Sync | Fast peptide-protein interaction analysis |
| `train_mcts_generate_data` | Sync | Generate training data for MCTS |
| `train_mcts_evaluate_model` | Sync | Evaluate MCTS model performance |
| `submit_mcts_training` | Async | Submit MCTS training job |
| `submit_peptide_design` | Async | Submit peptide design job |
| `submit_batch_peptide_analysis` | Async | Submit batch analysis job |
| `get_job_status` | Job Mgmt | Check job status |
| `get_job_result` | Job Mgmt | Get job results |
| `get_job_log` | Job Mgmt | View job logs |
| `cancel_job` | Job Mgmt | Cancel running job |
| `list_jobs` | Job Mgmt | List all jobs |

## Example Workflows

### Basic Analysis
```
Get server information to understand available tools.
Then analyze this cyclic peptide: sequence "GRGDSP" with receptor sequence "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR"
```

### Training Data Generation
```
Generate training data for MCTS with peptide length 12 and 100 samples.
```

### Model Training (Async)
```
Submit an MCTS training job with 10 epochs and batch size 32.
Monitor the job progress and show me the results when complete.
```

### Design Optimization
```
Submit a peptide design job for optimization with 200 iterations.
Use job management tools to track progress and retrieve results.
```

## Troubleshooting

### Server Not Connecting
```bash
# Check server can start manually
python src/server.py

# Check dependencies
python -c "from src.server import mcp; print('Server imports OK')"

# Re-register if needed
claude mcp remove cycpep-tools
claude mcp add cycpep-tools -- $(which python) $(pwd)/src/server.py
```

### Tool Not Found
```bash
# Verify all tools are registered
python -c "
import sys; sys.path.insert(0, '.')
from src.server import mcp
import asyncio
async def show_tools():
    tools = await mcp.get_tools()
    print(f'Found {len(tools)} tools:', tools)
asyncio.run(show_tools())
"
```

### Job Issues
- Jobs are stored in `jobs/` directory
- Check logs: `tail -f jobs/*/job.log`
- Use job management tools to monitor status

## System Requirements

### Environment
- Python 3.9+
- conda/mamba environment recommended
- Required packages: fastmcp, loguru, rdkit

### Resources
- Sync tools: Minimal resources, < 1GB RAM
- Async jobs: Depends on job size, 2-8GB RAM recommended
- Storage: ~100MB per job for outputs

## Support

For issues or questions:
1. Check the `reports/` directory for test results and examples
2. Review `tests/test_prompts.md` for usage examples
3. Use `get_server_info` tool to see available workflows
4. Check job logs for detailed error information

## Advanced Configuration

### Custom Paths
```bash
# Use custom Python environment
claude mcp add cycpep-tools -- /custom/path/to/python /path/to/src/server.py

# Set custom environment variables (if needed)
# Edit ~/.claude.json to add "env" section
```

### Job Management
```bash
# Monitor all jobs
python -c "
from src.jobs.manager import job_manager
print(job_manager.list_jobs())
"

# Clean old jobs (if needed)
rm -rf jobs/old_job_id
```

## Production Deployment

For production use:
1. Ensure stable Python environment
2. Monitor job queue depth
3. Implement regular cleanup of old jobs
4. Consider setting resource limits for concurrent jobs
5. Monitor disk space in jobs directory

---

**Installation Status**: ✅ Fully Tested and Ready
**Last Updated**: December 31, 2025
**Compatibility**: Claude Code CLI with MCP support