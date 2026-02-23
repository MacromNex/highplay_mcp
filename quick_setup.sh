#!/bin/bash
# Quick Setup Script for HighPlay MCP
# HighPlay: Cyclic Peptide Sequence Design Based on Reinforcement Learning
# Uses MCTS and protein structure prediction for cyclic peptide design
# Source: https://github.com/hongliangduan/HighPlay

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Setting up HighPlay MCP ==="

# Step 1: Create Python environment
echo "[1/5] Creating Python 3.10 environment..."
(command -v mamba >/dev/null 2>&1 && mamba create -p ./env python=3.10 pip -y) || \
(command -v conda >/dev/null 2>&1 && conda create -p ./env python=3.10 pip -y) || \
(echo "Warning: Neither mamba nor conda found, creating venv instead" && python3 -m venv ./env)

# Step 2: Install core dependencies
echo "[2/5] Installing core dependencies..."
./env/bin/pip install loguru click pandas numpy tqdm

# Step 3: Install fastmcp
echo "[3/5] Installing fastmcp..."
./env/bin/pip install --force-reinstall --no-cache-dir fastmcp

# Step 4: Install additional scientific packages
echo "[4/5] Installing scientific packages..."
./env/bin/pip install biopython scipy matplotlib PyYAML requests

# Step 5: Install RDKit
echo "[5/5] Installing RDKit..."
(command -v mamba >/dev/null 2>&1 && mamba install -p ./env -c conda-forge rdkit -y) || \
(command -v conda >/dev/null 2>&1 && conda install -p ./env -c conda-forge rdkit -y) || \
./env/bin/pip install rdkit

echo ""
echo "=== HighPlay MCP Setup Complete ==="
echo "Note: For full functionality, download AlphaFold parameters:"
echo "See: https://github.com/deepmind/alphafold/blob/main/scripts/download_alphafold_params.sh"
echo "To run the MCP server: ./env/bin/python src/server.py"
