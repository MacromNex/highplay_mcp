# MCP Scripts

Clean, self-contained scripts extracted from use cases for MCP tool wrapping.

## Design Principles

1. **Minimal Dependencies**: Only essential packages imported (numpy, pandas)
2. **Self-Contained**: Functions inlined where possible, HighPlay dependencies simplified
3. **Configurable**: Parameters in config files, not hardcoded
4. **MCP-Ready**: Each script has a main function ready for MCP wrapping

## Scripts Overview

| Script | Description | Repo Dependent | Config | Verified |
|--------|-------------|----------------|--------|----------|
| `analyze_peptide.py` | Analyze cyclic peptide-protein interactions | No | `configs/analyze_peptide_config.json` | ✅ |
| `train_mcts.py` | Train MCTS policy-value network | No | `configs/train_mcts_config.json` | ✅ |
| `design_peptide.py` | Design cyclic peptides using MCTS | No | `configs/design_peptide_config.json` | ✅ |

## Requirements

```bash
# Required packages
pip install numpy pandas

# Optional for enhanced functionality
pip install torch  # For real neural networks (train_mcts.py uses simplified model by default)
```

## Usage Examples

### 1. Peptide Analysis

```bash
# Analyze peptide from demo data
python scripts/analyze_peptide.py --input examples/data/sequences/target.csv --pdb-id 6seo --output results/analysis.csv

# Direct peptide analysis with mutations
python scripts/analyze_peptide.py \
  --peptide "XVPLRARNLPPSFFTEPX" \
  --receptor-seq "GPRSVASS..." \
  --suggest-mutations \
  --output results/custom_analysis.csv

# With custom config
python scripts/analyze_peptide.py \
  --input examples/data/sequences/target.csv \
  --pdb-id 6seo \
  --config configs/analyze_peptide_config.json \
  --output results/analysis.csv
```

### 2. MCTS Training

```bash
# Generate training data
python scripts/train_mcts.py \
  --mode generate \
  --num-samples 5000 \
  --peptide-length 16 \
  --output models/

# Train model
python scripts/train_mcts.py \
  --mode train \
  --epochs 100 \
  --batch-size 32 \
  --learning-rate 0.001 \
  --output models/

# Evaluate model
python scripts/train_mcts.py \
  --mode evaluate \
  --model models/policy_value_net.pkl \
  --training-data models/training_data.pkl \
  --output models/
```

### 3. Peptide Design

```bash
# Design peptide for demo target
python scripts/design_peptide.py \
  --input examples/data/sequences/target.csv \
  --target 6seo \
  --peptide-length 16 \
  --iterations 300 \
  --output results/design_6seo

# Custom target design
python scripts/design_peptide.py \
  --receptor-seq "GPRSVASS..." \
  --interface-residues "40,41,42,43,46" \
  --peptide-length 12 \
  --iterations 200 \
  --output results/custom_design
```

## Shared Library

Common functions are in `scripts/lib/`:
- `molecules.py`: RDKit-like molecular utilities (no external dependencies)
- `io.py`: File loading/saving
- `validation.py`: Input validation
- `utils.py`: General utilities (logging, timing, error handling)

## Configuration

Each script can use JSON configuration files to override defaults:

```json
{
  "analysis": {
    "simulate_binding_scores": true,
    "score_range": {"min": 0.3, "max": 0.9}
  },
  "output": {
    "precision": 4,
    "include_metadata": true
  }
}
```

## For MCP Wrapping (Step 6)

Each script exports a main function that can be wrapped:

```python
# For analyze_peptide.py
from scripts.analyze_peptide import run_analyze_peptide

@mcp.tool()
def analyze_cyclic_peptide(input_file: str, pdb_id: str, output_file: str = None):
    return run_analyze_peptide(input_file, pdb_id=pdb_id, output_file=output_file)

# For train_mcts.py
from scripts.train_mcts import run_train_mcts

@mcp.tool()
def train_peptide_model(mode: str, peptide_length: int = 16, epochs: int = 100):
    return run_train_mcts(mode, peptide_length=peptide_length, epochs=epochs)

# For design_peptide.py
from scripts.design_peptide import run_design_peptide

@mcp.tool()
def design_cyclic_peptide(target_id: str, peptide_length: int = 16, iterations: int = 300):
    return run_design_peptide(target_id=target_id, peptide_length=peptide_length, iterations=iterations)
```

## Function Signatures

### analyze_peptide.py
```python
def run_analyze_peptide(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    pdb_id: Optional[str] = None,
    peptide_seq: Optional[str] = None,
    receptor_seq: Optional[str] = None,
    suggest_mutations: bool = False,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
```

### train_mcts.py
```python
def run_train_mcts(
    mode: str,  # 'generate', 'train', 'evaluate'
    peptide_length: int = 16,
    num_samples: int = 1000,
    epochs: int = 100,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    training_data_file: Optional[Union[str, Path]] = None,
    model_file: Optional[Union[str, Path]] = None,
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
```

### design_peptide.py
```python
def run_design_peptide(
    input_file: Optional[Union[str, Path]] = None,
    target_id: Optional[str] = None,
    receptor_seq: Optional[str] = None,
    interface_residues: Optional[str] = None,
    peptide_length: int = 16,
    iterations: int = 300,
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
```

## Testing

All scripts have been verified to work independently:

```bash
# Test all scripts
python scripts/analyze_peptide.py --input examples/data/sequences/target.csv --pdb-id 6seo --output test_analysis.csv
python scripts/train_mcts.py --mode generate --num-samples 100 --peptide-length 12
python scripts/design_peptide.py --input examples/data/sequences/target.csv --target 6seo --peptide-length 12 --iterations 20
```

## Key Simplifications

1. **Structure Prediction**: Simulated using sequence properties instead of ColabFold/AlphaFold
2. **Neural Networks**: Simplified numpy implementation instead of PyTorch (can be upgraded)
3. **MCTS**: Basic implementation without complex tree structures
4. **Dependencies**: Only numpy/pandas required, no external APIs

## Upgrade Path

To restore full functionality:
1. Install ColabFold: `pip install colabfold`
2. Set `use_structure_prediction: true` in configs
3. Replace simplified models with PyTorch implementations
4. Add GPU support configuration

The scripts are designed to gracefully degrade when advanced features are unavailable.