# Step 3: Use Cases Report

## Scan Information
- **Scan Date**: 2024-12-31
- **Filter Applied**: cyclic peptide sequence design using HighPlay MCTS reinforcement learning, target protein binding
- **Python Version**: 3.9 (legacy environment), 3.10 (MCP environment)
- **Environment Strategy**: dual environment setup
- **Repository Analyzed**: HighPlay

## Use Cases

### UC-001: Cyclic Peptide Design using MCTS Reinforcement Learning
- **Description**: Design new cyclic peptides that bind to target proteins using Monte Carlo Tree Search reinforcement learning combined with AlphaFold structure prediction
- **Script Path**: `examples/use_case_1_peptide_design.py`
- **Complexity**: complex
- **Priority**: high
- **Environment**: `./env_py39` (requires HighPlay dependencies)
- **Source**: `repo/HighPlay/design.py`, `repo/HighPlay/design.sh`, README.md

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| target_id | string | PDB ID from demo data | --target |
| receptor_seq | string | Target protein amino acid sequence | --receptor-seq |
| interface_residues | string | Comma-separated binding pocket residue indices | --interface-residues, --pocket |
| peptide_length | integer | Desired cyclic peptide length (8-25 residues) | --peptide-length, -l |
| iterations | integer | Number of MCTS optimization iterations | --iterations, -n |
| input_file | file | CSV file with target protein data | --input, -i |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| optimized_sequences | file | CSV with optimized peptide sequences and scores |
| structures | directory | Predicted 3D structures (PDB files) |
| optimization_log | file | Training progress and convergence metrics |
| mcts_tree | file | Saved MCTS search tree (pickle format) |

**Example Usage:**
```bash
# Environment activation required
mamba activate ./env_py39

# Design peptide for demo target
python examples/use_case_1_peptide_design.py --target 6seo --peptide-length 16

# Custom target design
python examples/use_case_1_peptide_design.py --receptor-seq "GPRSVASS..." --interface-residues "40,41,42,43,46" --peptide-length 12 --iterations 200
```

**Example Data**: `examples/data/sequences/target.csv`

---

### UC-002: Cyclic Peptide-Protein Interaction Analysis
- **Description**: Analyze existing cyclic peptide-protein interactions including structure prediction, binding affinity estimation, and sequence optimization suggestions
- **Script Path**: `examples/use_case_2_peptide_analysis.py`
- **Complexity**: medium
- **Priority**: high
- **Environment**: `./env_py39` (for structure prediction) or `./env` (for basic analysis)
- **Source**: Derived from `repo/HighPlay/mutate.py`, `repo/HighPlay/pre.py`

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| pdb_id | string | PDB ID from demo data | --pdb-id |
| peptide_seq | string | Cyclic peptide amino acid sequence | --peptide |
| receptor_seq | string | Target protein amino acid sequence | --receptor-seq |
| input_file | file | CSV file with peptide-protein data | --input, -i |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| analysis_results | file | CSV with structural analysis metrics |
| mutation_suggestions | file | CSV with beneficial sequence modifications |
| visualization_info | file | 3D structure visualization information |

**Example Usage:**
```bash
# Analyze demo peptide-protein pair
python examples/use_case_2_peptide_analysis.py --pdb-id 6seo

# Custom analysis with mutation suggestions
python examples/use_case_2_peptide_analysis.py --peptide "XVPLRARNLPPSFFTEPX" --receptor-seq "GPRSVASS..." --suggest-mutations
```

**Example Data**: `examples/data/sequences/target.csv`

---

### UC-003: MCTS Policy-Value Network Training
- **Description**: Train and fine-tune the Monte Carlo Tree Search policy-value network used for cyclic peptide optimization, enabling improved design performance
- **Script Path**: `examples/use_case_3_mcts_training.py`
- **Complexity**: complex
- **Priority**: medium
- **Environment**: `./env_py39` (requires HighPlay neural network modules)
- **Source**: `repo/HighPlay/policyvaluenet.py`, `repo/HighPlay/mcts.py`, `repo/HighPlay/train.py`

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| training_data | file | Training data from optimization runs (pickle) | --training-data |
| test_data | file | Test data for model evaluation (pickle) | --test-data |
| peptide_length | integer | Peptide length for training samples | --peptide-length, -l |
| num_samples | integer | Number of training samples to generate | --num-samples, -n |
| epochs | integer | Number of training epochs | --epochs, -e |
| batch_size | integer | Training batch size | --batch-size, -b |
| learning_rate | float | Neural network learning rate | --learning-rate, -lr |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| trained_model | file | Trained policy-value network (pickle) |
| training_data | file | Generated training samples (pickle) |
| evaluation_metrics | file | Model performance metrics (CSV) |
| validation_results | file | Validation performance (CSV) |

**Example Usage:**
```bash
# Train model with default parameters
python examples/use_case_3_mcts_training.py --train --peptide-length 16 --epochs 100

# Generate training data only
python examples/use_case_3_mcts_training.py --generate-data --num-samples 5000 --output training_data.pkl

# Evaluate existing model
python examples/use_case_3_mcts_training.py --evaluate --model models/policy_value_net.pkl --test-data test_data.pkl
```

**Example Data**: Synthetic training data generated from peptide optimization runs

---

## Summary

| Metric | Count |
|--------|-------|
| Total Found | 3 |
| Scripts Created | 3 |
| High Priority | 2 |
| Medium Priority | 1 |
| Low Priority | 0 |
| Demo Data Copied | Yes |
| Executable Scripts | Yes |

## Demo Data Index

| Source | Destination | Description |
|--------|-------------|-------------|
| `repo/HighPlay/data/target.csv` | `examples/data/sequences/target.csv` | Sample cyclic peptide-protein complex data with sequences |

### Target Data Contents
- **1ssc**: 11-residue cyclic peptide (PYVPVHFDASV) binding to receptor
- **3r7g**: 22-residue cyclic peptide (KSLYKIKPRHDSGIKAKISMKT) binding to receptor
- **6seo**: 18-residue cyclic peptide (XVPLRARNLPPSFFTEPX) binding to receptor

## Implementation Notes

### Environment Requirements
- **UC-001** and **UC-002**: Require `./env_py39` for AlphaFold/ColabFold structure prediction
- **UC-003**: Requires `./env_py39` for neural network training components
- All scripts include fallback modes for demo purposes when full dependencies unavailable

### Algorithm Overview
1. **MCTS Optimization**: Uses tree search to explore peptide sequence space
2. **Structure Prediction**: AlphaFold/ColabFold for 3D structure and binding evaluation
3. **Reinforcement Learning**: Policy-value network guides search towards optimal sequences
4. **Cyclization**: Specialized handling of cyclic peptide constraints and cyclization indices

### Performance Considerations
- **Peptide Design**: 300 iterations take 2-6 hours depending on length and GPU
- **Analysis**: Single peptide structure prediction takes 5-15 minutes
- **Training**: Neural network training with 1000 samples takes 30-60 minutes
- **Memory**: Peak usage 4-8GB during optimization

### Integration with MCP
Each use case script is designed to be callable from MCP tools with:
- Command-line interface with clear parameter documentation
- JSON-compatible input/output for integration
- Error handling and environment validation
- Progress reporting and logging

## Filter Match Analysis
All identified use cases match the specified filter criteria:
- ✅ **Cyclic peptide sequence design**: All use cases focus on cyclic peptides
- ✅ **HighPlay MCTS reinforcement learning**: Core algorithm in UC-001 and UC-003
- ✅ **Target protein binding**: Primary objective in UC-001 and UC-002

The use cases comprehensively cover the full HighPlay workflow from initial design through analysis and model improvement.