#!/usr/bin/env python3
"""
Script: analyze_peptide.py
Description: Analyze cyclic peptide-protein interactions with binding metrics and mutation suggestions

Original Use Case: examples/use_case_2_peptide_analysis.py
Dependencies Removed: HighPlay modules inlined, simplified structure prediction simulation

Usage:
    python scripts/analyze_peptide.py --input <input_file> --output <output_file>

Example:
    python scripts/analyze_peptide.py --input examples/data/sequences/target.csv --pdb-id 6seo --output results/analysis.csv
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

# Import shared library
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from molecules import (
    calculate_hydrophobic_ratio, calculate_net_charge, calculate_molecular_weight,
    validate_cyclic_peptide, STANDARD_AMINO_ACIDS
)
from lib.io import load_peptide_csv, save_results_csv, load_config, ensure_output_dir
from validation import validate_input_parameters
from utils import setup_logging, Timer, format_results, create_output_metadata, handle_mcp_error

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "analysis": {
        "simulate_binding_scores": True,
        "score_range": {"min": 0.3, "max": 0.9},
        "plddt_range": {"min": 60, "max": 90},
        "confidence_range": {"min": 0.5, "max": 0.95}
    },
    "mutations": {
        "max_suggestions": 10,
        "min_improvement": 0.01,
        "position_scan": True
    },
    "output": {
        "include_metadata": True,
        "precision": 4
    }
}

# ==============================================================================
# Core Analysis Functions
# ==============================================================================
def simulate_binding_scores(peptide_seq: str, receptor_seq: str, config: Dict[str, Any]) -> Dict[str, float]:
    """
    Simulate binding scores for demo purposes.

    In the original HighPlay code, this would call predict_cycle() and sequence_scores,
    but those require ColabFold/AlphaFold setup. For MCP use, we simulate reasonable scores
    based on sequence properties.

    Args:
        peptide_seq: Peptide amino acid sequence
        receptor_seq: Receptor protein sequence
        config: Configuration dictionary

    Returns:
        Dictionary with binding scores
    """
    # Use sequence properties to generate realistic scores
    np.random.seed(hash(peptide_seq + receptor_seq) % 2**32)  # Reproducible per pair

    # Base scores on sequence properties
    hydrophobic_ratio = calculate_hydrophobic_ratio(peptide_seq)
    charge = abs(calculate_net_charge(peptide_seq))
    length_factor = len(peptide_seq) / 16.0  # Normalize to typical length

    # Adjust score ranges based on properties
    score_config = config["analysis"]
    base_binding = np.random.uniform(score_config["score_range"]["min"],
                                   score_config["score_range"]["max"])

    # Adjust based on properties
    binding_score = base_binding
    binding_score += 0.1 * hydrophobic_ratio  # More hydrophobic = better binding
    binding_score -= 0.05 * charge  # Less charged = better binding
    binding_score = np.clip(binding_score, 0.1, 1.0)

    # PlDDT score (structure confidence)
    base_plddt = np.random.uniform(score_config["plddt_range"]["min"],
                                 score_config["plddt_range"]["max"])
    plddt_score = base_plddt + 10 * (1 - length_factor * 0.5)  # Shorter = higher confidence
    plddt_score = np.clip(plddt_score, 40, 95)

    # Overall confidence
    confidence = (binding_score * 0.6 + (plddt_score / 100) * 0.4)
    confidence = np.clip(confidence, 0.1, 1.0)

    return {
        'binding_score': binding_score,
        'plddt_score': plddt_score,
        'confidence': confidence
    }


def analyze_peptide_structure(
    peptide_seq: str,
    receptor_seq: str,
    pdb_id: str = "unknown",
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze peptide-protein interaction structure and binding.

    Args:
        peptide_seq: Cyclic peptide amino acid sequence
        receptor_seq: Target protein amino acid sequence
        pdb_id: PDB identifier for reference
        config: Configuration dictionary

    Returns:
        Dictionary containing analysis results
    """
    if config is None:
        config = DEFAULT_CONFIG

    logger = setup_logging()
    logger.info(f"Analyzing peptide-protein interaction: {pdb_id}")

    # Basic sequence information
    results = {
        'pdb_id': pdb_id,
        'peptide_sequence': peptide_seq,
        'peptide_length': len(peptide_seq),
        'receptor_length': len(receptor_seq),
        'is_valid_cyclic_peptide': validate_cyclic_peptide(peptide_seq)
    }

    try:
        # Calculate binding scores (simulated)
        scores = simulate_binding_scores(peptide_seq, receptor_seq, config)
        results.update(scores)

        # Analyze amino acid composition
        aa_counts = {}
        for aa in peptide_seq:
            aa_counts[aa] = aa_counts.get(aa, 0) + 1
        results['aa_composition'] = aa_counts

        # Calculate peptide properties
        results['hydrophobic_ratio'] = calculate_hydrophobic_ratio(peptide_seq)
        results['net_charge'] = calculate_net_charge(peptide_seq)
        results['molecular_weight'] = calculate_molecular_weight(peptide_seq)

        # Cysteine analysis for cyclization
        cys_count = peptide_seq.count('C')
        results['cysteine_count'] = cys_count

        if cys_count >= 2:
            cys_positions = [i for i, aa in enumerate(peptide_seq) if aa == 'C']
            results['cysteine_positions'] = cys_positions
            if len(cys_positions) >= 2:
                results['cysteine_distance'] = cys_positions[-1] - cys_positions[0]

        logger.info(f"Analysis completed for {pdb_id}")
        logger.info(f"  Binding score: {results['binding_score']:.3f}")
        logger.info(f"  plDDT score: {results['plddt_score']:.1f}")
        logger.info(f"  Confidence: {results['confidence']:.3f}")

        return results

    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        results['error'] = str(e)
        return results


def generate_mutation_suggestions(
    peptide_seq: str,
    receptor_seq: str,
    current_score: float,
    config: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Suggest mutations to improve binding affinity.

    Args:
        peptide_seq: Current peptide sequence
        receptor_seq: Target protein sequence
        current_score: Current binding score
        config: Configuration dictionary

    Returns:
        List of mutation suggestions with predicted improvements
    """
    if config is None:
        config = DEFAULT_CONFIG

    logger = setup_logging()
    logger.info("Generating mutation suggestions...")

    mut_config = config["mutations"]
    suggestions = []

    # Try single-point mutations at each position
    for i, original_aa in enumerate(peptide_seq):
        for new_aa in STANDARD_AMINO_ACIDS:
            if new_aa != original_aa:
                mutant_seq = peptide_seq[:i] + new_aa + peptide_seq[i+1:]

                # Skip if mutation breaks cyclization (removes critical cysteines)
                if not validate_cyclic_peptide(mutant_seq):
                    continue

                # Simulate scoring for mutant
                scores = simulate_binding_scores(mutant_seq, receptor_seq, config)
                predicted_score = scores['binding_score']
                improvement = predicted_score - current_score

                if improvement > mut_config["min_improvement"]:
                    suggestion = {
                        'position': i + 1,  # 1-based indexing
                        'original': original_aa,
                        'mutation': new_aa,
                        'mutant_sequence': mutant_seq,
                        'predicted_score': predicted_score,
                        'improvement': improvement,
                        'mutation_type': f"{original_aa}{i+1}{new_aa}",
                        'predicted_plddt': scores['plddt_score'],
                        'predicted_confidence': scores['confidence']
                    }
                    suggestions.append(suggestion)

    # Sort by predicted improvement
    suggestions.sort(key=lambda x: x['improvement'], reverse=True)

    # Take top suggestions
    suggestions = suggestions[:mut_config["max_suggestions"]]

    logger.info(f"Found {len(suggestions)} beneficial mutation suggestions")
    return suggestions


def generate_analysis_report(results: Dict[str, Any], suggestions: List[Dict[str, Any]]) -> str:
    """
    Generate a text report of the analysis results.

    Args:
        results: Analysis results dictionary
        suggestions: Mutation suggestions list

    Returns:
        Formatted text report
    """
    report = []
    report.append("CYCLIC PEPTIDE ANALYSIS REPORT")
    report.append("=" * 50)
    report.append("")

    # Basic information
    report.append(f"PDB ID: {results.get('pdb_id', 'N/A')}")
    report.append(f"Peptide Sequence: {results.get('peptide_sequence', 'N/A')}")
    report.append(f"Peptide Length: {results.get('peptide_length', 'N/A')}")
    report.append(f"Receptor Length: {results.get('receptor_length', 'N/A')}")
    report.append(f"Valid Cyclic Peptide: {results.get('is_valid_cyclic_peptide', False)}")
    report.append("")

    # Binding metrics
    report.append("BINDING METRICS:")
    report.append(f"  Binding Score: {results.get('binding_score', 0):.4f}")
    report.append(f"  plDDT Score: {results.get('plddt_score', 0):.1f}")
    report.append(f"  Confidence: {results.get('confidence', 0):.4f}")
    report.append("")

    # Physicochemical properties
    report.append("PHYSICOCHEMICAL PROPERTIES:")
    report.append(f"  Hydrophobic Ratio: {results.get('hydrophobic_ratio', 0):.3f}")
    report.append(f"  Net Charge: {results.get('net_charge', 0):.1f}")
    report.append(f"  Molecular Weight: {results.get('molecular_weight', 0):.1f} Da")
    report.append(f"  Cysteine Count: {results.get('cysteine_count', 0)}")
    report.append("")

    # Amino acid composition
    if 'aa_composition' in results:
        report.append("AMINO ACID COMPOSITION:")
        aa_comp = results['aa_composition']
        for aa in sorted(aa_comp.keys()):
            count = aa_comp[aa]
            percentage = (count / results.get('peptide_length', 1)) * 100
            report.append(f"  {aa}: {count} ({percentage:.1f}%)")
        report.append("")

    # Top mutation suggestions
    if suggestions:
        report.append("TOP MUTATION SUGGESTIONS:")
        for i, sug in enumerate(suggestions[:5], 1):
            report.append(f"  {i}. {sug['mutation_type']}: score {sug['predicted_score']:.4f} "
                         f"(+{sug['improvement']:.4f})")
        report.append("")

    return "\n".join(report)


# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
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
    """
    Main function for cyclic peptide analysis.

    Args:
        input_file: Path to input CSV file or None
        output_file: Path to save output (optional)
        pdb_id: PDB ID to analyze from CSV
        peptide_seq: Direct peptide sequence input
        receptor_seq: Direct receptor sequence input
        suggest_mutations: Whether to generate mutation suggestions
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Main analysis results
            - mutations: Mutation suggestions (if requested)
            - output_file: Path to output file (if saved)
            - metadata: Execution metadata
    """
    # Setup
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}
    logger = setup_logging()

    with Timer("Peptide Analysis"):
        try:
            # Determine input source
            if pdb_id and input_file:
                # Load from CSV file
                input_path = Path(input_file)
                if not input_path.exists():
                    raise FileNotFoundError(f"Input file not found: {input_path}")

                df = load_peptide_csv(input_path)
                target_row = df[df['pdb_id'] == pdb_id]

                if target_row.empty:
                    available = ', '.join(df['pdb_id'].tolist())
                    raise ValueError(f"PDB ID '{pdb_id}' not found in {input_file}. Available: {available}")

                row = target_row.iloc[0]
                peptide_sequence = row['peptide_sequence']
                receptor_sequence = row['receptor_sequence']
                target_pdb_id = row['pdb_id']

            elif peptide_seq and receptor_seq:
                # Direct sequence input
                peptide_sequence = peptide_seq
                receptor_sequence = receptor_seq
                target_pdb_id = 'custom'

            else:
                raise ValueError("Must specify either: (input_file + pdb_id) or (peptide_seq + receptor_seq)")

            # Validate parameters
            validation_params = {
                'peptide_sequence': peptide_sequence,
                'pdb_id': target_pdb_id if target_pdb_id != 'custom' else None
            }
            errors = validate_input_parameters(validation_params)
            if errors:
                raise ValueError(f"Validation errors: {'; '.join(errors)}")

            # Perform analysis
            analysis_results = analyze_peptide_structure(
                peptide_seq=peptide_sequence,
                receptor_seq=receptor_sequence,
                pdb_id=target_pdb_id,
                config=config
            )

            # Generate mutation suggestions if requested
            mutation_suggestions = []
            if suggest_mutations and 'binding_score' in analysis_results:
                mutation_suggestions = generate_mutation_suggestions(
                    peptide_seq=peptide_sequence,
                    receptor_seq=receptor_sequence,
                    current_score=analysis_results['binding_score'],
                    config=config
                )

            # Format results
            formatted_results = format_results(analysis_results, config["output"]["precision"])

            # Save output if requested
            output_path = None
            if output_file:
                output_path = ensure_output_dir(Path(output_file))

                # Save main results
                save_results_csv(formatted_results, output_path)

                # Save mutation suggestions
                if mutation_suggestions:
                    suggestions_file = output_path.parent / f"{output_path.stem}_mutations{output_path.suffix}"
                    save_results_csv(mutation_suggestions, suggestions_file)

                # Save text report
                report = generate_analysis_report(formatted_results, mutation_suggestions)
                report_file = output_path.parent / f"{output_path.stem}_report.txt"
                with open(report_file, 'w') as f:
                    f.write(report)

                logger.info(f"Results saved to: {output_path}")
                if mutation_suggestions:
                    logger.info(f"Mutations saved to: {suggestions_file}")
                logger.info(f"Report saved to: {report_file}")

            result = {
                "result": formatted_results,
                "mutations": mutation_suggestions if suggest_mutations else [],
                "output_file": str(output_path) if output_path else None,
                "metadata": create_output_metadata(
                    input_params=validation_params,
                    execution_time=1.0,  # Timer will show actual time
                    script_name="analyze_peptide"
                )
            }

            logger.info("✓ Analysis completed successfully!")
            return result

        except Exception as e:
            return handle_mcp_error(e, "peptide_analysis")


# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Input options
    parser.add_argument('--input', '-i', help='CSV file with peptide-protein data')
    parser.add_argument('--pdb-id', help='PDB ID to analyze from input CSV')
    parser.add_argument('--peptide', help='Peptide sequence (alternative to CSV input)')
    parser.add_argument('--receptor-seq', help='Receptor protein sequence')

    # Analysis options
    parser.add_argument('--suggest-mutations', action='store_true',
                       help='Generate mutation suggestions for improved binding')

    # Output options
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--config', '-c', help='Config file (JSON)')

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        config = load_config(args.config)

    # Run analysis
    result = run_analyze_peptide(
        input_file=args.input,
        output_file=args.output,
        pdb_id=args.pdb_id,
        peptide_seq=args.peptide,
        receptor_seq=args.receptor_seq,
        suggest_mutations=args.suggest_mutations,
        config=config
    )

    if result.get('metadata', {}).get('success', False):
        print(f"Success: {result.get('output_file', 'Analysis completed')}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())