#!/usr/bin/env python3
"""
Script: design_peptide.py
Description: Design cyclic peptides using MCTS reinforcement learning

Original Use Case: examples/use_case_1_peptide_design.py
Dependencies Removed: Simplified for demo mode, HighPlay components extracted

Usage:
    python scripts/design_peptide.py --target <target_id> --peptide-length <length>

Example:
    python scripts/design_peptide.py --target 6seo --peptide-length 16 --iterations 50
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
from pathlib import Path
from typing import Union, Optional, Dict, Any, List
import json
import numpy as np
import pandas as pd
import random
from collections import deque

# Import shared library
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from molecules import (
    STANDARD_AMINO_ACIDS, initialize_weights, CC_index, CC_distance,
    validate_cyclic_peptide, calculate_hydrophobic_ratio, calculate_net_charge
)
from lib.io import load_peptide_csv, save_results_csv, load_config, ensure_output_dir, save_pickle
from validation import validate_input_parameters
from utils import (
    setup_logging, Timer, format_results, create_output_metadata,
    handle_mcp_error, progress_callback
)

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "design": {
        "peptide_length": 16,
        "iterations": 300,
        "jumpout_num": 30,
        "use_structure_prediction": False,  # Set to True if HighPlay/ColabFold available
        "simulation_mode": True  # Simplified scoring for demo
    },
    "scoring": {
        "plddt_only": True,
        "binding_weight": 0.6,
        "plddt_weight": 0.4,
        "cyclization_penalty": 0.2
    },
    "mcts": {
        "c_puct": 5.0,
        "n_playout": 100,
        "temperature": 1.0,
        "dirichlet_alpha": 0.3
    },
    "optimization": {
        "max_sequence_length": 50,
        "min_sequence_length": 8,
        "cysteine_distance_min": 3,
        "cysteine_distance_max": 20
    },
    "output": {
        "save_intermediate": True,
        "save_optimization_log": True,
        "precision": 4
    }
}

# ==============================================================================
# Simplified Peptide Design Environment
# ==============================================================================
class SimplifiedPeptideEnvironment:
    """
    Simplified peptide design environment that replaces HighPlay's Seqenv.

    This provides basic peptide generation and mutation functionality
    without requiring the complex ColabFold/AlphaFold dependencies.
    """

    def __init__(self, peptide_length: int, receptor_seq: str, config: Dict[str, Any]):
        self.peptide_length = peptide_length
        self.receptor_seq = receptor_seq
        self.config = config
        self.current_peptide = None
        self.iteration = 0
        self.best_score = -float('inf')
        self.best_peptide = None
        self.optimization_history = []

    def initialize_peptide(self) -> str:
        """Initialize a random cyclic peptide."""
        try:
            _, peptide = initialize_weights(self.peptide_length)
            if not validate_cyclic_peptide(peptide):
                # Fallback to simple valid peptide
                peptide = self._create_simple_cyclic_peptide()
        except Exception:
            peptide = self._create_simple_cyclic_peptide()

        self.current_peptide = peptide
        return peptide

    def _create_simple_cyclic_peptide(self) -> str:
        """Create a simple valid cyclic peptide."""
        # Start with random sequence
        peptide = ''.join(random.choices(STANDARD_AMINO_ACIDS, k=self.peptide_length))

        # Ensure cysteines at reasonable positions
        c1_pos = random.randint(1, min(4, self.peptide_length // 3))
        c2_pos = random.randint(
            c1_pos + 3,
            min(self.peptide_length - 1, c1_pos + 15)
        )

        peptide_list = list(peptide)
        peptide_list[c1_pos] = 'C'
        peptide_list[c2_pos] = 'C'

        return ''.join(peptide_list)

    def calculate_score(self, peptide: str) -> float:
        """
        Calculate peptide score.

        In the full HighPlay implementation, this would use predict_cycle()
        and ColabFold structure prediction. Here we simulate reasonable scores.
        """
        if not validate_cyclic_peptide(peptide):
            return -1.0

        # Simulate binding affinity based on sequence properties
        hydrophobic_ratio = calculate_hydrophobic_ratio(peptide)
        net_charge = abs(calculate_net_charge(peptide))

        # Base score
        score = 0.5

        # Hydrophobic patches often improve binding
        score += 0.3 * hydrophobic_ratio

        # Too much charge can hurt binding
        score -= 0.1 * net_charge

        # Favor moderate lengths
        length_penalty = abs(len(peptide) - 16) * 0.02
        score -= length_penalty

        # Cyclization constraint
        try:
            cc_dist = CC_distance(peptide)
            if 3 <= cc_dist <= 20:
                score += 0.1  # Good cyclization
            else:
                score -= 0.2  # Poor cyclization
        except:
            score -= 0.3  # Invalid cyclization

        # Add some randomness to simulate experimental variation
        score += random.gauss(0, 0.05)

        # Ensure score is in reasonable range
        score = max(0.0, min(1.0, score))

        return score

    def mutate_peptide(self, peptide: str, position: int, new_aa: str) -> str:
        """
        Create mutant peptide.

        Args:
            peptide: Original peptide sequence
            position: Position to mutate (0-based)
            new_aa: New amino acid

        Returns:
            Mutated peptide sequence
        """
        if position < 0 or position >= len(peptide):
            return peptide

        mutant = peptide[:position] + new_aa + peptide[position + 1:]

        # Validate the mutation doesn't break cyclization
        if not validate_cyclic_peptide(mutant):
            return peptide

        return mutant

    def get_available_moves(self, peptide: str) -> List[tuple]:
        """
        Get list of available mutations.

        Returns:
            List of (position, new_aa) tuples
        """
        moves = []

        for pos in range(len(peptide)):
            current_aa = peptide[pos]

            for new_aa in STANDARD_AMINO_ACIDS:
                if new_aa != current_aa:
                    # Check if mutation would maintain valid cyclization
                    mutant = self.mutate_peptide(peptide, pos, new_aa)
                    if mutant != peptide and validate_cyclic_peptide(mutant):
                        moves.append((pos, new_aa))

        return moves

    def optimize_step(self, peptide: str) -> tuple[str, float]:
        """
        Perform one optimization step.

        Returns:
            Tuple of (best_mutant, best_score)
        """
        current_score = self.calculate_score(peptide)
        best_mutant = peptide
        best_score = current_score

        # Get available mutations
        available_moves = self.get_available_moves(peptide)

        if not available_moves:
            return best_mutant, best_score

        # Try random subset of moves (simulating MCTS sampling)
        num_tries = min(len(available_moves), 20)
        sampled_moves = random.sample(available_moves, num_tries)

        for pos, new_aa in sampled_moves:
            mutant = self.mutate_peptide(peptide, pos, new_aa)
            score = self.calculate_score(mutant)

            if score > best_score:
                best_mutant = mutant
                best_score = score

        return best_mutant, best_score


# ==============================================================================
# Simplified MCTS Implementation
# ==============================================================================
class SimplifiedMCTS:
    """
    Simplified MCTS for peptide optimization.

    This replaces the complex HighPlay MCTS implementation with a basic
    version suitable for demonstration.
    """

    def __init__(self, env: SimplifiedPeptideEnvironment, config: Dict[str, Any]):
        self.env = env
        self.config = config
        self.c_puct = config["mcts"]["c_puct"]
        self.n_playout = config["mcts"]["n_playout"]

    def select_move(self, peptide: str) -> tuple[str, float]:
        """
        Select next move using simplified MCTS.

        Args:
            peptide: Current peptide sequence

        Returns:
            Tuple of (new_peptide, score)
        """
        best_peptide = peptide
        best_score = self.env.calculate_score(peptide)

        # Simplified MCTS: try multiple random rollouts
        for _ in range(self.n_playout):
            candidate_peptide, candidate_score = self.env.optimize_step(peptide)

            if candidate_score > best_score:
                best_peptide = candidate_peptide
                best_score = candidate_score

        return best_peptide, best_score


# ==============================================================================
# Design Pipeline
# ==============================================================================
def design_cyclic_peptide(
    receptor_seq: str,
    interface_residues: str,
    peptide_length: int,
    iterations: int = 300,
    receptor_name: str = "target",
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Design a cyclic peptide using simplified MCTS algorithm.

    Args:
        receptor_seq: Target protein amino acid sequence
        interface_residues: Comma-separated interface residue indices
        peptide_length: Desired peptide length
        iterations: Number of optimization iterations
        receptor_name: Name identifier for the receptor
        config: Configuration dictionary

    Returns:
        Dictionary containing optimization results
    """
    if config is None:
        config = DEFAULT_CONFIG

    logger = setup_logging()
    logger.info(f"Designing cyclic peptide for receptor: {receptor_name}")
    logger.info(f"Receptor sequence length: {len(receptor_seq)}")
    logger.info(f"Interface residues: {interface_residues}")
    logger.info(f"Target peptide length: {peptide_length}")
    logger.info(f"Optimization iterations: {iterations}")

    # Initialize environment and MCTS
    env = SimplifiedPeptideEnvironment(peptide_length, receptor_seq, config)
    mcts = SimplifiedMCTS(env, config)

    # Initialize peptide
    current_peptide = env.initialize_peptide()
    current_score = env.calculate_score(current_peptide)

    # Track optimization history
    optimization_log = []
    best_peptide = current_peptide
    best_score = current_score

    logger.info(f"Initial peptide: {current_peptide}")
    logger.info(f"Initial score: {current_score:.4f}")

    # Optimization loop
    jumpout_interval = max(1, iterations // config["design"]["jumpout_num"])

    for i in range(iterations):
        # MCTS optimization step
        new_peptide, new_score = mcts.select_move(current_peptide)

        # Update current peptide
        current_peptide = new_peptide
        current_score = new_score

        # Track best peptide
        if current_score > best_score:
            best_peptide = current_peptide
            best_score = current_score

        # Log progress
        log_entry = {
            'iteration': i + 1,
            'peptide_sequence': current_peptide,
            'score': current_score,
            'is_best': current_score == best_score
        }
        optimization_log.append(log_entry)

        # Random jumpout to avoid local minima
        if (i + 1) % jumpout_interval == 0:
            current_peptide = env.initialize_peptide()
            current_score = env.calculate_score(current_peptide)
            logger.info(f"Jumpout at iteration {i + 1}")

        # Progress reporting
        if (i + 1) % 50 == 0:
            progress_callback(i + 1, iterations, "Optimization")
            logger.info(f"Iteration {i + 1}: best score = {best_score:.4f}, current = {current_score:.4f}")

    logger.info(f"Optimization completed")
    logger.info(f"Best peptide: {best_peptide}")
    logger.info(f"Best score: {best_score:.4f}")

    # Prepare results
    results = {
        'receptor_name': receptor_name,
        'receptor_sequence': receptor_seq,
        'interface_residues': interface_residues,
        'peptide_length': peptide_length,
        'iterations': iterations,
        'best_peptide': best_peptide,
        'best_score': best_score,
        'final_peptide': current_peptide,
        'final_score': current_score,
        'optimization_log': optimization_log,
        'total_iterations': len(optimization_log)
    }

    # Calculate additional metrics
    if best_peptide:
        results.update({
            'best_hydrophobic_ratio': calculate_hydrophobic_ratio(best_peptide),
            'best_net_charge': calculate_net_charge(best_peptide),
            'best_cysteine_count': best_peptide.count('C'),
            'best_is_valid': validate_cyclic_peptide(best_peptide)
        })

        try:
            results['best_cysteine_distance'] = CC_distance(best_peptide)
        except:
            results['best_cysteine_distance'] = None

    return results


# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
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
    """
    Main function for cyclic peptide design.

    Args:
        input_file: Path to input CSV file
        target_id: PDB ID to design for
        receptor_seq: Direct receptor sequence input
        interface_residues: Interface residue indices
        peptide_length: Desired peptide length
        iterations: Optimization iterations
        output_dir: Output directory
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Design results
            - output_files: List of generated files
            - metadata: Execution metadata
    """
    # Setup
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    # Override config with explicit parameters
    config["design"].update({
        "peptide_length": peptide_length,
        "iterations": iterations
    })

    logger = setup_logging()

    with Timer("Peptide Design"):
        try:
            # Determine input source
            if target_id and input_file:
                # Load from CSV file
                input_path = Path(input_file)
                if not input_path.exists():
                    raise FileNotFoundError(f"Input file not found: {input_path}")

                df = load_peptide_csv(input_path)
                target_row = df[df['pdb_id'] == target_id]

                if target_row.empty:
                    available = ', '.join(df['pdb_id'].tolist())
                    raise ValueError(f"Target ID '{target_id}' not found. Available: {available}")

                row = target_row.iloc[0]
                receptor_sequence = row['receptor_sequence']
                receptor_name = row['pdb_id']

                # Use provided interface residues or defaults
                if interface_residues is None:
                    if target_id == '6seo':
                        interface_residues = '40,41,42,43,46,47,74,76,162,185,187,189,190,191,196,197,198,200'
                    else:
                        interface_residues = '1,2,3,4,5'  # Placeholder

            elif receptor_seq and interface_residues:
                # Direct sequence input
                receptor_sequence = receptor_seq
                interface_residues = interface_residues
                receptor_name = 'custom'

            else:
                raise ValueError("Must specify either: (input_file + target_id) or (receptor_seq + interface_residues)")

            # Validate parameters
            validation_params = {
                'peptide_length': peptide_length,
                'interface_residues': interface_residues,
                'iterations': iterations
            }
            errors = validate_input_parameters(validation_params)
            if errors:
                raise ValueError(f"Validation errors: {'; '.join(errors)}")

            # Set output directory
            if output_dir is None:
                output_dir = Path(f"./results/{receptor_name}_{peptide_length}")
            else:
                output_dir = Path(output_dir)

            output_dir.mkdir(parents=True, exist_ok=True)

            # Perform peptide design
            design_results = design_cyclic_peptide(
                receptor_seq=receptor_sequence,
                interface_residues=interface_residues,
                peptide_length=peptide_length,
                iterations=iterations,
                receptor_name=receptor_name,
                config=config
            )

            # Format results
            formatted_results = format_results(design_results, config["output"]["precision"])

            # Save output files
            output_files = []

            # Save main results
            results_file = output_dir / f"peptide_design_{receptor_name}.csv"
            main_result = {key: val for key, val in formatted_results.items()
                          if key != 'optimization_log'}
            save_results_csv(main_result, results_file)
            output_files.append(str(results_file))

            # Save optimization log
            if config["output"]["save_optimization_log"] and 'optimization_log' in design_results:
                log_file = output_dir / f"optimization_log_{receptor_name}.csv"
                save_results_csv(design_results['optimization_log'], log_file)
                output_files.append(str(log_file))

            # Save best peptide sequence
            if 'best_peptide' in design_results:
                seq_file = output_dir / f"best_peptide_{receptor_name}.txt"
                with open(seq_file, 'w') as f:
                    f.write(f"Best Peptide for {receptor_name}\n")
                    f.write(f"Sequence: {design_results['best_peptide']}\n")
                    f.write(f"Score: {design_results['best_score']:.4f}\n")
                    f.write(f"Length: {len(design_results['best_peptide'])}\n")
                output_files.append(str(seq_file))

            # Save configuration
            config_file = output_dir / "design_config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            output_files.append(str(config_file))

            result = {
                "result": formatted_results,
                "output_files": output_files,
                "metadata": create_output_metadata(
                    input_params=validation_params,
                    execution_time=1.0,  # Timer will show actual time
                    script_name="design_peptide"
                )
            }

            logger.info("✓ Peptide design completed successfully!")
            logger.info(f"Results saved to: {output_dir}")

            return result

        except Exception as e:
            return handle_mcp_error(e, "peptide_design")


# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Input options
    parser.add_argument('--input', '-i', help='CSV file with target protein data')
    parser.add_argument('--target', '--target-id', help='PDB ID from input CSV (e.g., 6seo)')
    parser.add_argument('--receptor-seq', help='Target protein sequence (alternative to CSV)')
    parser.add_argument('--interface-residues', '--pocket',
                       help='Comma-separated interface residue indices')

    # Peptide parameters
    parser.add_argument('--peptide-length', '-l', type=int, default=16,
                       help='Desired peptide length (default: 16)')

    # Optimization parameters
    parser.add_argument('--iterations', '-n', type=int, default=300,
                       help='Number of optimization iterations (default: 300)')

    # Output parameters
    parser.add_argument('--output', '-o', help='Output directory')
    parser.add_argument('--config', '-c', help='Config file (JSON)')

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        config = load_config(args.config)

    # Run design
    result = run_design_peptide(
        input_file=args.input,
        target_id=args.target,
        receptor_seq=args.receptor_seq,
        interface_residues=args.interface_residues,
        peptide_length=args.peptide_length,
        iterations=args.iterations,
        output_dir=args.output,
        config=config
    )

    if result.get('metadata', {}).get('success', False):
        print(f"Success: Design completed")
        for file_path in result.get('output_files', []):
            print(f"  Generated: {file_path}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())