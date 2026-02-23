#!/usr/bin/env python3
"""
HighPlay Cyclic Peptide Design Use Case 1: MCTS-based Peptide Sequence Design

This script demonstrates how to use HighPlay for designing cyclic peptides that bind to target proteins
using Monte Carlo Tree Search (MCTS) reinforcement learning combined with AlphaFold structure prediction.

The main workflow:
1. Initialize random peptide sequence of specified length
2. Use MCTS to explore sequence space guided by predicted binding affinity
3. Use AlphaFold/ColabFold to predict 3D structures and evaluate binding
4. Iteratively improve peptide sequence through reinforcement learning

Input: Target protein sequence, binding pocket residues, desired peptide length
Output: Optimized cyclic peptide sequence with predicted binding properties
"""

import os
import sys
import argparse
import pandas as pd
from typing import Optional, List, Tuple

# Add repo path to import HighPlay modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'repo', 'HighPlay'))

try:
    from train import TrainPipeline
    from pre import initialize_weights, CC_index
except ImportError as e:
    print(f"Error importing HighPlay modules: {e}")
    print("Please ensure the HighPlay environment is activated: mamba activate ./env_py39")
    sys.exit(1)


def load_target_data(data_file: str) -> pd.DataFrame:
    """Load target protein data from CSV file."""
    try:
        df = pd.read_csv(data_file)
        print(f"Loaded {len(df)} target proteins from {data_file}")
        return df
    except FileNotFoundError:
        print(f"Error: Data file not found: {data_file}")
        return pd.DataFrame()


def design_cyclic_peptide(
    receptor_seq: str,
    receptor_if_residues: str,
    peptide_length: int,
    output_dir: str,
    num_iterations: int = 300,
    plDDT_only: bool = True,
    receptor_name: str = "target",
    jumpout_num: int = 30
) -> str:
    """
    Design a cyclic peptide using HighPlay MCTS algorithm.

    Args:
        receptor_seq: Target protein amino acid sequence
        receptor_if_residues: Comma-separated interface residue indices
        peptide_length: Desired peptide length (typically 8-25 residues)
        output_dir: Directory to save results
        num_iterations: Number of MCTS iterations
        plDDT_only: Whether to use only plDDT score (structure confidence)
        receptor_name: Name identifier for the receptor
        jumpout_num: Number of random jumpouts to avoid local minima

    Returns:
        Path to the output directory containing results
    """
    print(f"Designing cyclic peptide for receptor: {receptor_name}")
    print(f"Receptor sequence length: {len(receptor_seq)}")
    print(f"Interface residues: {receptor_if_residues}")
    print(f"Target peptide length: {peptide_length}")

    # Note: Using CPU for compatibility (CUDA disabled)

    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Initialize random peptide sequence and weights
    weights, peptide_sequence = initialize_weights(peptide_length)
    C2, C1 = CC_index(peptide_sequence)

    print(f"Initial peptide sequence: {peptide_sequence}")
    print(f"Cyclization indices - C1: {C1}, C2: {C2}")

    # Initialize training pipeline
    training_pipeline = TrainPipeline(
        init_seq=peptide_sequence,
        receptor_seq=receptor_seq,
        pocket=receptor_if_residues,
        output_dir=output_dir,
        num_iterations=num_iterations,
        plDDT_only=plDDT_only,
        receptor_name=receptor_name,
        jumpout_num=jumpout_num
    )

    # Run optimization
    print(f"Starting MCTS optimization with {num_iterations} iterations...")
    training_pipeline.run()

    print(f"Optimization completed. Results saved to: {output_dir}")
    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="HighPlay Cyclic Peptide Design using MCTS Reinforcement Learning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Design peptide for 6seo receptor using demo data
    python %(prog)s --target 6seo --peptide-length 16

    # Custom target with specific parameters
    python %(prog)s --receptor-seq "GPRSVASS..." --interface-residues "40,41,42,43,46" --peptide-length 12 --iterations 200

    # Use data from CSV file
    python %(prog)s --input examples/data/sequences/target.csv --target-id 1ssc --peptide-length 11
        """
    )

    # Input options
    parser.add_argument('--input', '-i',
                       default='examples/data/sequences/target.csv',
                       help='CSV file with target protein data')
    parser.add_argument('--target', '--target-id',
                       help='PDB ID from the input CSV file (e.g., 6seo, 1ssc)')
    parser.add_argument('--receptor-seq',
                       help='Target protein sequence (alternative to CSV input)')
    parser.add_argument('--interface-residues', '--pocket',
                       help='Comma-separated interface residue indices')

    # Peptide parameters
    parser.add_argument('--peptide-length', '-l', type=int, default=16,
                       help='Desired peptide length (default: 16)')

    # Optimization parameters
    parser.add_argument('--iterations', '-n', type=int, default=300,
                       help='Number of MCTS iterations (default: 300)')
    parser.add_argument('--jumpout-num', type=int, default=30,
                       help='Number of random jumpouts (default: 30)')
    parser.add_argument('--use-full-scoring', action='store_true',
                       help='Use full scoring (default: plDDT only)')

    # Output parameters
    parser.add_argument('--output', '-o',
                       help='Output directory (default: ./results/TARGET_ID)')
    parser.add_argument('--receptor-name',
                       help='Receptor name for output files')

    args = parser.parse_args()

    # Determine input source
    if args.target and os.path.exists(args.input):
        # Load from CSV file
        df = load_target_data(args.input)
        if df.empty:
            return 1

        target_row = df[df['pdb_id'] == args.target]
        if target_row.empty:
            print(f"Error: Target '{args.target}' not found in {args.input}")
            print(f"Available targets: {', '.join(df['pdb_id'].tolist())}")
            return 1

        row = target_row.iloc[0]
        receptor_seq = row['receptor_sequence']
        receptor_name = args.receptor_name or row['pdb_id']

        # For demo purposes, use a subset of interface residues if not specified
        if args.interface_residues:
            interface_residues = args.interface_residues
        else:
            # Use demo interface residues for 6seo
            if args.target == '6seo':
                interface_residues = '40,41,42,43,46,47,74,76,162,185,187,189,190,191,196,197,198,200'
            else:
                print(f"Warning: No interface residues specified for {args.target}")
                interface_residues = '1,2,3,4,5'  # Placeholder

    elif args.receptor_seq and args.interface_residues:
        # Direct sequence input
        receptor_seq = args.receptor_seq
        interface_residues = args.interface_residues
        receptor_name = args.receptor_name or 'custom'
    else:
        print("Error: Must specify either:")
        print("  1. --target with CSV file, or")
        print("  2. --receptor-seq and --interface-residues")
        return 1

    # Set output directory
    if args.output:
        output_dir = args.output
    else:
        output_dir = f"./results/{receptor_name}_{args.peptide_length}"

    try:
        result_dir = design_cyclic_peptide(
            receptor_seq=receptor_seq,
            receptor_if_residues=interface_residues,
            peptide_length=args.peptide_length,
            output_dir=output_dir,
            num_iterations=args.iterations,
            plDDT_only=not args.use_full_scoring,
            receptor_name=receptor_name,
            jumpout_num=args.jumpout_num
        )

        print(f"\n✓ Peptide design completed successfully!")
        print(f"Results saved to: {result_dir}")
        print(f"\nTo analyze results:")
        print(f"  - Check {result_dir}/peptides.csv for optimized sequences")
        print(f"  - View structure files in {result_dir}/structures/")
        print(f"  - See optimization log in {result_dir}/optimization.log")

        return 0

    except Exception as e:
        print(f"\nError during peptide design: {e}")
        print("Make sure you're using the correct environment: mamba activate ./env_py39")
        return 1


if __name__ == '__main__':
    sys.exit(main())