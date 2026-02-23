# HighPlay MCP Examples

This directory contains example scripts demonstrating the main use cases of HighPlay for cyclic peptide design and analysis.

## Overview

HighPlay is a computational tool for designing cyclic peptides that bind to target proteins using Monte Carlo Tree Search (MCTS) reinforcement learning combined with AlphaFold structure prediction.

## Available Examples

### 1. Peptide Design (`use_case_1_peptide_design.py`)

**Purpose**: Design new cyclic peptides that bind to target proteins

**Input**: Target protein sequence, binding pocket residues, desired peptide length
**Output**: Optimized cyclic peptide sequences with predicted binding properties

**Example Usage**:
```bash
# Design peptide for 6seo receptor using demo data
mamba activate ./env_py39
python examples/use_case_1_peptide_design.py --target 6seo --peptide-length 16

# Custom target with specific parameters
python examples/use_case_1_peptide_design.py --receptor-seq "GPRSVASS..." --interface-residues "40,41,42,43,46" --peptide-length 12 --iterations 200
```

### 2. Peptide Analysis (`use_case_2_peptide_analysis.py`)

**Purpose**: Analyze existing cyclic peptide-protein interactions

**Input**: Peptide sequence, target protein sequence, known binding data
**Output**: Structural analysis, binding predictions, optimization suggestions

**Example Usage**:
```bash
# Analyze a specific peptide from demo data
python examples/use_case_2_peptide_analysis.py --pdb-id 6seo

# Analyze custom peptide-protein pair
python examples/use_case_2_peptide_analysis.py --peptide "XVPLRARNLPPSFFTEPX" --receptor-seq "GPRSVASS..." --suggest-mutations
```

### 3. MCTS Training (`use_case_3_mcts_training.py`)

**Purpose**: Train and fine-tune the MCTS policy-value network

**Input**: Training data from peptide optimization runs
**Output**: Trained MCTS policy-value network models

**Example Usage**:
```bash
# Train model with default parameters
python examples/use_case_3_mcts_training.py --train --peptide-length 16 --epochs 100

# Generate training data only
python examples/use_case_3_mcts_training.py --generate-data --num-samples 5000 --output training_data.pkl
```

## Demo Data

### sequences/target.csv

Contains sample peptide-protein complex data with the following columns:
- `pdb_id`: PDB structure identifier
- `receptor_chain`: Receptor protein chain
- `peptide_chain`: Peptide chain identifier
- `receptor_sequence`: Target protein amino acid sequence
- `peptide_sequence`: Cyclic peptide amino acid sequence
- `peptide_length`: Number of amino acids in peptide

Available targets:
- **1ssc**: 11-residue peptide (PYVPVHFDASV)
- **3r7g**: 22-residue peptide (KSLYKIKPRHDSGIKAKISMKT)
- **6seo**: 18-residue peptide (XVPLRARNLPPSFFTEPX)

## Environment Setup

All examples require the HighPlay legacy Python 3.9 environment:

```bash
# Activate the environment
mamba activate ./env_py39

# Verify installation
python -c "import numpy, pandas, biopython; print('Environment ready')"
```

## Quick Start Guide

1. **Set up the environment**:
   ```bash
   cd /path/to/highplay_mcp
   mamba activate ./env_py39
   ```

2. **Run a simple peptide design**:
   ```bash
   python examples/use_case_1_peptide_design.py --target 6seo --peptide-length 16 --iterations 50
   ```

3. **Analyze the results**:
   ```bash
   python examples/use_case_2_peptide_analysis.py --pdb-id 6seo --suggest-mutations
   ```

## Expected Output Files

### Peptide Design Output
- `peptides.csv`: Optimized sequences with scores
- `structures/`: Predicted 3D structures (PDB files)
- `optimization.log`: Training progress and convergence
- `mcts_tree.pkl`: Saved MCTS search tree

### Analysis Output
- `analysis_{pdb_id}.csv`: Structural analysis metrics
- `mutations_{pdb_id}.csv`: Suggested sequence improvements
- `visualization_{pdb_id}.txt`: 3D visualization info

### Training Output
- `policy_value_net.pkl`: Trained neural network model
- `training_data.pkl`: Generated training samples
- `validation_results.csv`: Model performance metrics

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure the HighPlay environment is activated
   ```bash
   mamba activate ./env_py39
   ```

2. **CUDA errors**: HighPlay requires GPU support for structure prediction
   ```bash
   # Check GPU availability
   nvidia-smi
   ```

3. **AlphaFold dependencies**: Some features require AlphaFold parameters
   ```bash
   # Download AlphaFold params (large download)
   bash repo/HighPlay/download_alphafold_params.sh ./
   ```

### Performance Notes

- **Peptide Design**: 300 iterations typically take 2-6 hours depending on peptide length and GPU
- **Analysis**: Structure prediction for single peptides takes 5-15 minutes
- **Training**: Training with 1000 samples takes 30-60 minutes

## Advanced Usage

### Custom Scoring Functions

Modify the scoring functions in the HighPlay modules:
- `mutate.py`: Peptide mutation and scoring logic
- `pre.py`: Structure prediction and evaluation
- `policyvaluenet.py`: Neural network architecture

### Batch Processing

Process multiple targets using shell scripts:
```bash
# Design peptides for all targets in CSV
for target in 1ssc 3r7g 6seo; do
    python examples/use_case_1_peptide_design.py --target $target --peptide-length 16
done
```

## References

- HighPlay Paper: "Cyclic Peptide Sequence Design Based on Reinforcement Learning and Protein Structure Prediction"
- AlphaFold: https://alphafold.ebi.ac.uk/
- ColabFold: https://colab.research.google.com/github/deepmind/alphafold