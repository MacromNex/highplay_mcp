# HighPlay MCP

> MCP tools for cyclic peptide computational analysis using MCTS reinforcement learning

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

HighPlay MCP provides comprehensive computational tools for cyclic peptide design and analysis through Monte Carlo Tree Search (MCTS) reinforcement learning. This MCP server enables design of novel cyclic peptides that bind to specific target proteins, analysis of existing peptide-protein interactions, and training of neural networks for peptide optimization.

### Features
- **Cyclic Peptide Design**: MCTS-based optimization for target-specific peptide design
- **Molecular Property Analysis**: Calculate binding scores, physicochemical properties, and drug-likeness
- **Structure-Activity Relationships**: Mutation suggestions for improved binding
- **Neural Network Training**: Policy-value networks for reinforcement learning
- **Batch Processing**: High-throughput screening and analysis capabilities

### Directory Structure
```
./
├── README.md               # This file
├── env/                    # Conda environment (Python 3.10, MCP)
├── env_py39/              # Legacy environment (Python 3.9, HighPlay)
├── src/
│   ├── server.py           # MCP server
│   └── jobs/               # Job management system
├── scripts/
│   ├── analyze_peptide.py  # Peptide-protein interaction analysis
│   ├── train_mcts.py       # MCTS policy-value network training
│   ├── design_peptide.py   # MCTS-based peptide design
│   └── lib/                # Shared utilities
├── examples/
│   └── data/               # Demo data
│       └── sequences/      # Sample peptide-protein complexes
├── configs/                # Configuration files
│   ├── analyze_peptide_config.json
│   ├── train_mcts_config.json
│   ├── design_peptide_config.json
│   └── default_config.json
└── repo/                   # Original HighPlay repository
```

---

## Installation

### Quick Setup

Run the automated setup script:

```bash
./quick_setup.sh
```

This will create both environments (main MCP and legacy Python 3.9) and install all dependencies automatically.

### Manual Setup (Advanced)

For manual installation or customization, follow these steps.

#### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+
- 4GB+ RAM (8GB+ recommended for design optimization)
- RDKit (installed automatically)

#### Create Environment

Please follow the dual environment setup from `reports/step3_environment.md`. The complete workflow is:

```bash
# Navigate to the MCP directory
cd /home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/highplay_mcp

# Determine package manager (prefer mamba over conda)
if command -v mamba &> /dev/null; then
    PKG_MGR="mamba"
else
    PKG_MGR="conda"
fi
echo "Using package manager: $PKG_MGR"

# Create main MCP environment
$PKG_MGR create -p ./env python=3.10 pip -y

# Create legacy environment for advanced features (optional)
$PKG_MGR create -p ./env_py39 python=3.9 pip -y

# Activate main environment
$PKG_MGR activate ./env

# Install MCP dependencies
pip install loguru click pandas numpy tqdm
pip install --force-reinstall --no-cache-dir fastmcp

# Install core scientific packages
pip install biopython scipy matplotlib PyYAML requests

# Install RDKit (recommended for molecular property calculations)
$PKG_MGR install -c conda-forge rdkit -y

# Optional: Install legacy environment dependencies
$PKG_MGR activate ./env_py39
pip install numpy==1.23.5 pandas==1.5.3 biopython==1.79 scipy==1.10.1 matplotlib==3.7.1 PyYAML==6.0 tqdm==4.65.0 requests==2.28.2
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Example |
|--------|-------------|---------|
| `scripts/analyze_peptide.py` | Analyze cyclic peptide-protein interactions with binding metrics and mutation suggestions | See below |
| `scripts/train_mcts.py` | Train and evaluate MCTS policy-value networks for peptide optimization | See below |
| `scripts/design_peptide.py` | Design cyclic peptides using MCTS reinforcement learning optimization | See below |

### Script Examples

#### Analyze Peptide-Protein Interactions

```bash
# Activate environment
mamba activate ./env

# Analyze specific PDB complex from demo data
python scripts/analyze_peptide.py \
  --input examples/data/sequences/target.csv \
  --pdb-id 6seo \
  --output results/6seo_analysis.csv \
  --suggest-mutations

# Analyze custom peptide-protein pair
python scripts/analyze_peptide.py \
  --peptide-seq "XVPLRARNLPPSFFTEPX" \
  --receptor-seq "GPRSVASSKLWMLEFSAFLEQQQDPDTYNKHLFVHIGQSSPSYSDPYLEAVDIRQIYDKFPEKKGGLKDLFERGPSNAFFLVKFWADLNTNIEDEGSSFYGVSSQYESPENMIITCSTKVCSFGKQVVEXVETEYARYENGHYSYRIHRSPLCEYMINFIHKLKHLPEKYMMNSVLENFTILQVVTNRDTQETLLCIAYVFEVSASEHGAQHHIYRLVKE" \
  --output results/custom_analysis.csv
```

**Parameters:**
- `--input, -i`: CSV file with peptide-protein data (optional)
- `--pdb-id`: PDB ID from input file to analyze
- `--peptide-seq`: Direct peptide sequence input
- `--receptor-seq`: Direct receptor sequence input
- `--suggest-mutations`: Generate mutation suggestions for improved binding
- `--output, -o`: Output file path (default: results/)

#### Train MCTS Policy-Value Networks

```bash
# Generate training data
python scripts/train_mcts.py \
  --mode generate \
  --peptide-length 16 \
  --num-samples 1000 \
  --output training_data/

# Train neural network
python scripts/train_mcts.py \
  --mode train \
  --peptide-length 16 \
  --epochs 100 \
  --batch-size 32 \
  --learning-rate 0.001 \
  --output models/

# Evaluate trained model
python scripts/train_mcts.py \
  --mode evaluate \
  --model-file models/policy_value_net.pkl \
  --output evaluation/
```

#### Design Cyclic Peptides

```bash
# Design peptide for target protein from demo data
python scripts/design_peptide.py \
  --input examples/data/sequences/target.csv \
  --target 6seo \
  --peptide-length 16 \
  --iterations 300 \
  --output results/design_6seo/

# Design with custom target
python scripts/design_peptide.py \
  --receptor-seq "GPRSVASS..." \
  --interface-residues "40,41,42,43,46" \
  --peptide-length 12 \
  --iterations 200 \
  --output results/custom_design/
```

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Install MCP server for Claude Code
fastmcp install src/server.py --name cycpep-tools
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add cycpep-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "cycpep-tools": {
      "command": "/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/highplay_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/highplay_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from cycpep-tools?
```

#### Property Analysis (Fast)
```
Analyze the cyclic peptide XVPLRARNLPPSFFTEPX binding to protein 6seo with mutation suggestions
```

#### Structure Prediction (Submit API)
```
Design a 16-residue cyclic peptide that binds to protein 6seo using 300 MCTS optimization iterations
```

#### Check Job Status
```
Check the status of job abc12345 and show me the logs if it failed
```

#### Batch Processing
```
Train an MCTS policy-value network for 16-residue peptides with 100 epochs and batch size 32
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/sequences/target.csv` | Reference the demo peptide data |
| `@configs/analyze_peptide_config.json` | Reference analysis configuration |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "cycpep-tools": {
      "command": "/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/highplay_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/highplay_mcp/src/server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same as Claude Code)
> What cyclic peptide design tools are available?
> Analyze peptide KSLYKIKPRHDSGIKAKISMKT for binding properties
```

---

## Available Tools

### Quick Operations (Sync API)

These tools return results immediately (< 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `analyze_cyclic_peptide` | Analyze peptide-protein interactions | `input_file`, `pdb_id`, `peptide_seq`, `receptor_seq`, `suggest_mutations` |
| `train_mcts_generate_data` | Generate MCTS training data | `peptide_length`, `num_samples`, `output_dir` |
| `train_mcts_evaluate_model` | Evaluate trained MCTS model | `model_file`, `training_data_file`, `output_dir` |

### Long-Running Tasks (Submit API)

These tools return a job_id for tracking (> 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_mcts_training` | Train MCTS policy-value network | `peptide_length`, `epochs`, `batch_size`, `learning_rate`, `job_name` |
| `submit_peptide_design` | Design peptides with MCTS optimization | `input_file`, `target_id`, `receptor_seq`, `peptide_length`, `iterations` |
| `submit_batch_peptide_analysis` | Batch analyze multiple peptides | `input_file`, `suggest_mutations`, `job_name` |

### Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress |
| `get_job_result` | Get results when completed |
| `get_job_log` | View execution logs |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs |

---

## Examples

### Example 1: Quick Property Analysis

**Goal:** Analyze binding properties of a known cyclic peptide

**Using Script:**
```bash
python scripts/analyze_peptide.py \
  --input examples/data/sequences/target.csv \
  --pdb-id 6seo \
  --suggest-mutations \
  --output results/6seo_analysis.csv
```

**Using MCP (in Claude Code):**
```
Analyze the cyclic peptide from PDB entry 6seo in the demo data. Include mutation suggestions for improved binding.
```

**Expected Output:**
- Binding score: 0.493
- plDDT confidence: 79.0
- Overall confidence: 0.612
- 10 mutation suggestions
- Physicochemical properties

### Example 2: MCTS Peptide Design

**Goal:** Design a novel cyclic peptide targeting protein 6seo

**Using Script:**
```bash
python scripts/design_peptide.py \
  --input examples/data/sequences/target.csv \
  --target 6seo \
  --peptide-length 16 \
  --iterations 300 \
  --output results/design_6seo/
```

**Using MCP (in Claude Code):**
```
Design a 16-residue cyclic peptide that binds to protein 6seo using MCTS optimization with 300 iterations.
Monitor the job progress and show me the final optimized peptide sequence when complete.
```

### Example 3: Neural Network Training Pipeline

**Goal:** Train a policy-value network for peptide optimization

**Using MCP (in Claude Code):**
```
I want to train an MCTS policy-value network for cyclic peptide design:

1. First generate 5000 training samples for 16-residue peptides
2. Train the network with 100 epochs and batch size 32
3. Evaluate the trained model and show me the performance metrics

Start with the training data generation.
```

### Example 4: Virtual Screening Pipeline

**Goal:** Screen multiple peptides for drug-likeness and binding

**Using MCP (in Claude Code):**
```
I have these three cyclic peptides I want to analyze for drug potential:
1. PYVPVHFDASV (from 1ssc)
2. KSLYKIKPRHDSGIKAKISMKT (from 3r7g)
3. XVPLRARNLPPSFFTEPX (from 6seo)

Analyze each one using the demo data and tell me which has the best binding properties and molecular characteristics.
```

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Use With |
|------|-------------|----------|
| `sequences/target.csv` | Sample peptide-protein complexes | All analysis and design tools |

### Target Data Contents
- **1ssc**: 11-residue cyclic peptide (PYVPVHFDASV) binding to receptor
- **3r7g**: 22-residue cyclic peptide (KSLYKIKPRHDSGIKAKISMKT) binding to receptor
- **6seo**: 18-residue cyclic peptide (XVPLRARNLPPSFFTEPX) binding to receptor

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Parameters |
|--------|-------------|------------|
| `analyze_peptide_config.json` | Peptide analysis config | scoring weights, mutation settings |
| `train_mcts_config.json` | MCTS training config | network architecture, hyperparameters |
| `design_peptide_config.json` | Peptide design config | MCTS settings, optimization parameters |
| `default_config.json` | Shared default settings | validation rules, constraints |

### Config Example

```json
{
  "analysis": {
    "simulate_binding_scores": true,
    "score_range": {"min": 0.3, "max": 0.9}
  },
  "mutations": {
    "max_suggestions": 10,
    "min_improvement": 0.01
  },
  "validation": {
    "min_length": 8,
    "max_length": 50
  }
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate environment
mamba create -p ./env python=3.10 pip -y
mamba activate ./env
pip install loguru click pandas numpy tqdm fastmcp
mamba install -c conda-forge rdkit -y
```

**Problem:** RDKit import errors
```bash
# Install RDKit from conda-forge
mamba install -c conda-forge rdkit -y
```

**Problem:** FastMCP import errors
```bash
# Reinstall FastMCP
pip install --force-reinstall --no-cache-dir fastmcp
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove cycpep-tools
claude mcp add cycpep-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

**Problem:** Invalid peptide sequence error
```
Ensure your peptide sequence uses standard amino acid codes (A-Z).
For cyclic peptides, use the format like "XVPLRARNLPPSFFTEPX" where X represents cyclization points.
```

**Problem:** Tools not working
```bash
# Test server directly
python -c "
from src.server import mcp
print(list(mcp.list_tools().keys()))
"
```

### Job Issues

**Problem:** Job stuck in pending
```bash
# Check job directory
ls -la jobs/

# View job log
cat jobs/<job_id>/job.log
```

**Problem:** Job failed
```
Use get_job_log with job_id "<job_id>" and tail 100 to see error details
```

**Problem:** Out of memory during training
```bash
# Reduce batch size and number of samples
python scripts/train_mcts.py --mode train --batch-size 16 --num-samples 500
```

---

## Development

### Running Tests

```bash
# Activate environment
mamba activate ./env

# Run integration tests
python tests/integration_test.py

# Test specific script
python scripts/analyze_peptide.py --help
python scripts/design_peptide.py --input examples/data/sequences/target.csv --target 6seo --iterations 5
```

### Starting Dev Server

```bash
# Run MCP server in dev mode
fastmcp dev src/server.py
```

### Performance Tuning

For better performance with large-scale design:

1. **Use GPU acceleration** (requires PyTorch + CUDA in env_py39)
2. **Increase iteration counts** for better optimization (500-1000 iterations)
3. **Enable structure prediction** for more accurate scoring
4. **Parallel job execution** for batch processing

---

## Algorithm Overview

### MCTS Reinforcement Learning
1. **Monte Carlo Tree Search**: Explores peptide sequence space using tree search
2. **Policy-Value Network**: Neural network guides search towards optimal sequences
3. **Rollouts**: Simulated optimization paths evaluate sequence quality
4. **Backpropagation**: Results update search tree for improved exploration

### Cyclic Peptide Constraints
- **Cyclization**: Enforces proper ring closure (typically disulfide bonds)
- **Length Constraints**: Supports 8-50 residue peptides
- **Amino Acid Diversity**: Uses all 20 standard amino acids
- **Physicochemical Properties**: Balances hydrophobicity, charge, and size

### Scoring Functions
- **Binding Affinity**: Simulated protein-peptide interaction strength
- **Structural Confidence**: plDDT-like scores for structure quality
- **Drug-likeness**: Molecular properties for oral bioavailability
- **Manufacturability**: Sequence complexity and stability

---

## License

This project builds upon the HighPlay repository for cyclic peptide design using MCTS reinforcement learning.

## Credits

Based on [HighPlay](https://github.com/HighPlay/repo) - MCTS Reinforcement Learning for Cyclic Peptide Design