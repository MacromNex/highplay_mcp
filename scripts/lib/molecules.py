"""
Molecular manipulation functions for cyclic peptide MCP scripts.

These functions are extracted and simplified from the HighPlay repository
(repo/HighPlay/pre.py) to provide self-contained molecular utilities.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict


# Standard 20 amino acids
STANDARD_AMINO_ACIDS = ['A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I',
                       'L', 'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V']


def CC_index(peptide: str) -> Tuple[int, int]:
    """
    Find cysteine positions in peptide sequence for cyclization.

    Extracted from repo/HighPlay/pre.py lines 16-26.

    Args:
        peptide: Amino acid sequence string

    Returns:
        Tuple of (C2_index, C1_index) where C2 > C1
    """
    cysteine_positions = [i for i, aa in enumerate(peptide) if aa == 'C']

    if len(cysteine_positions) < 2:
        raise ValueError(f"Cyclic peptide requires at least 2 cysteines, found {len(cysteine_positions)}")

    # Return first and last cysteine positions
    C1 = cysteine_positions[0]
    C2 = cysteine_positions[-1]

    return C2, C1


def CC_distance(peptide: str) -> int:
    """
    Calculate distance between first and last cysteine residues.

    Extracted from repo/HighPlay/pre.py lines 28-30.

    Args:
        peptide: Amino acid sequence string

    Returns:
        Distance between first and last cysteine
    """
    C2, C1 = CC_index(peptide)
    return C2 - C1


def sequence_to_onehot(sequence: str, aatypes: Optional[List[str]] = None) -> np.ndarray:
    """
    Convert amino acid sequence to one-hot encoding.

    Extracted from repo/HighPlay/pre.py lines 233-240.

    Args:
        sequence: Amino acid sequence string
        aatypes: List of amino acid types (default: standard 20 AAs)

    Returns:
        One-hot encoded array of shape (len(sequence), len(aatypes))
    """
    if aatypes is None:
        aatypes = STANDARD_AMINO_ACIDS

    aa_to_index = {aa: i for i, aa in enumerate(aatypes)}

    onehot = np.zeros((len(sequence), len(aatypes)))
    for i, aa in enumerate(sequence):
        if aa in aa_to_index:
            onehot[i, aa_to_index[aa]] = 1

    return onehot


def onehot_to_sequence(onehot: np.ndarray, aatypes: Optional[List[str]] = None) -> str:
    """
    Convert one-hot encoding back to amino acid sequence.

    Extracted from repo/HighPlay/pre.py lines 243-249.

    Args:
        onehot: One-hot encoded array
        aatypes: List of amino acid types (default: standard 20 AAs)

    Returns:
        Amino acid sequence string
    """
    if aatypes is None:
        aatypes = STANDARD_AMINO_ACIDS

    sequence = ""
    for position in onehot:
        aa_index = np.argmax(position)
        if aa_index < len(aatypes):
            sequence += aatypes[aa_index]
        else:
            sequence += 'X'  # Unknown amino acid

    return sequence


def softmax(x: np.ndarray) -> np.ndarray:
    """
    Compute softmax activation.

    Extracted from repo/HighPlay/mcts.py lines 4-7.

    Args:
        x: Input array

    Returns:
        Softmax normalized array
    """
    x = x - np.max(x)  # Numerical stability
    exp_x = np.exp(x)
    return exp_x / np.sum(exp_x)


def initialize_weights(peptide_length: int, max_attempts: int = 1000) -> Tuple[np.ndarray, str]:
    """
    Initialize random peptide weights with cyclization constraints.

    Simplified from repo/HighPlay/pre.py lines 138-159.
    Ensures exactly 2 cysteines with proper distance constraints.

    Args:
        peptide_length: Desired length of peptide
        max_attempts: Maximum attempts to find valid sequence

    Returns:
        Tuple of (weights, peptide_sequence)
    """
    for attempt in range(max_attempts):
        # Generate random Gumbel weights for each position
        weights = np.random.gumbel(0, 1, (peptide_length, len(STANDARD_AMINO_ACIDS)))

        # Convert to sequence
        sequence = ""
        for position_weights in weights:
            aa_index = np.argmax(position_weights)
            sequence += STANDARD_AMINO_ACIDS[aa_index]

        # Check cysteine constraints
        cysteine_count = sequence.count('C')

        if cysteine_count == 2:
            try:
                C2, C1 = CC_index(sequence)
                cc_distance = CC_distance(sequence)

                # Validate distance constraints (typical range 3-20)
                if 3 <= cc_distance <= min(20, peptide_length - 3):
                    return weights, sequence
            except ValueError:
                continue

        elif cysteine_count < 2:
            # Force exactly 2 cysteines in reasonable positions
            # Place first cysteine early
            C1_pos = np.random.randint(1, min(5, peptide_length // 3))
            # Place second cysteine with good spacing
            min_C2_pos = C1_pos + 3
            max_C2_pos = min(peptide_length - 1, C1_pos + 20)

            if min_C2_pos < max_C2_pos:
                C2_pos = np.random.randint(min_C2_pos, max_C2_pos)

                # Set cysteine weights
                cys_index = STANDARD_AMINO_ACIDS.index('C')
                weights[C1_pos, :] = -10  # Set all others low
                weights[C1_pos, cys_index] = 10  # Set cysteine high
                weights[C2_pos, :] = -10
                weights[C2_pos, cys_index] = 10

                # Regenerate sequence
                sequence = ""
                for i, position_weights in enumerate(weights):
                    aa_index = np.argmax(position_weights)
                    sequence += STANDARD_AMINO_ACIDS[aa_index]

                return weights, sequence

    # Fallback: simple sequence with cysteines at positions 1 and -2
    weights = np.random.gumbel(0, 1, (peptide_length, len(STANDARD_AMINO_ACIDS)))
    cys_index = STANDARD_AMINO_ACIDS.index('C')

    weights[1, :] = -10
    weights[1, cys_index] = 10
    weights[-2, :] = -10
    weights[-2, cys_index] = 10

    sequence = ""
    for position_weights in weights:
        aa_index = np.argmax(position_weights)
        sequence += STANDARD_AMINO_ACIDS[aa_index]

    return weights, sequence


def validate_cyclic_peptide(sequence: str) -> bool:
    """
    Validate that a sequence represents a valid cyclic peptide.

    Args:
        sequence: Amino acid sequence

    Returns:
        True if valid cyclic peptide
    """
    try:
        # Check length
        if not (8 <= len(sequence) <= 50):
            return False

        # Check for cysteines
        cys_count = sequence.count('C')
        if cys_count < 2:
            return False

        # Check cysteine distance
        C2, C1 = CC_index(sequence)
        distance = CC_distance(sequence)

        if distance < 3 or distance > min(20, len(sequence) - 3):
            return False

        # Check for valid amino acids
        valid_aas = set(STANDARD_AMINO_ACIDS + ['X'])  # X for unknown
        if not all(aa in valid_aas for aa in sequence):
            return False

        return True

    except (ValueError, IndexError):
        return False


def calculate_hydrophobic_ratio(sequence: str) -> float:
    """
    Calculate the ratio of hydrophobic amino acids in the sequence.

    From examples/use_case_2_peptide_analysis.py lines 125-129.
    """
    hydrophobic = set(['A', 'V', 'I', 'L', 'M', 'F', 'Y', 'W'])
    hydrophobic_count = sum(1 for aa in sequence if aa in hydrophobic)
    return hydrophobic_count / len(sequence) if sequence else 0.0


def calculate_net_charge(sequence: str, pH: float = 7.0) -> float:
    """
    Calculate net charge of the peptide at given pH.

    From examples/use_case_2_peptide_analysis.py lines 132-140.
    Simplified charge calculation.
    """
    positive = {'R': 1, 'K': 1, 'H': 0.1}  # Simplified
    negative = {'D': -1, 'E': -1}

    charge = 0.0
    for aa in sequence:
        charge += positive.get(aa, 0) + negative.get(aa, 0)
    return charge


def calculate_molecular_weight(sequence: str) -> float:
    """
    Calculate approximate molecular weight of the peptide.

    From examples/use_case_2_peptide_analysis.py lines 143-156.
    """
    # Simplified amino acid weights (Da)
    aa_weights = {
        'A': 71.04, 'R': 156.10, 'N': 114.04, 'D': 115.03, 'C': 103.01,
        'Q': 128.06, 'E': 129.04, 'G': 57.02, 'H': 137.06, 'I': 113.08,
        'L': 113.08, 'K': 128.09, 'M': 131.04, 'F': 147.07, 'P': 97.05,
        'S': 87.03, 'T': 101.05, 'W': 186.08, 'Y': 163.06, 'V': 99.07,
        'X': 100.0  # Unknown amino acid
    }

    weight = sum(aa_weights.get(aa, 100) for aa in sequence)
    # Subtract water for peptide bonds
    weight -= (len(sequence) - 1) * 18.015
    return weight