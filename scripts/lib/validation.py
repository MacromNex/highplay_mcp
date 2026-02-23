"""
Input validation utilities for cyclic peptide MCP scripts.

These functions provide validation for peptide sequences, parameters, and file inputs.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def validate_amino_acid_sequence(sequence: str) -> bool:
    """
    Validate amino acid sequence.

    Args:
        sequence: Amino acid sequence string

    Returns:
        True if valid amino acid sequence
    """
    if not sequence:
        return False

    # Check for valid amino acid characters (including X for unknown)
    valid_pattern = re.compile(r'^[ARNDCQEGHILKMFPSTWYVX]+$')
    return bool(valid_pattern.match(sequence.upper()))


def validate_peptide_length(length: int, min_length: int = 8, max_length: int = 50) -> bool:
    """
    Validate peptide length is within reasonable bounds.

    Args:
        length: Peptide length
        min_length: Minimum allowed length
        max_length: Maximum allowed length

    Returns:
        True if length is valid
    """
    return min_length <= length <= max_length


def validate_file_exists(file_path: Union[str, Path]) -> bool:
    """
    Check if file exists and is readable.

    Args:
        file_path: Path to file

    Returns:
        True if file exists and is readable
    """
    try:
        file_path = Path(file_path)
        return file_path.exists() and file_path.is_file()
    except Exception:
        return False


def validate_config_dict(config: Dict[str, Any], required_keys: List[str]) -> bool:
    """
    Validate that configuration dictionary has required keys.

    Args:
        config: Configuration dictionary
        required_keys: List of required key names

    Returns:
        True if all required keys are present
    """
    if not isinstance(config, dict):
        return False

    return all(key in config for key in required_keys)


def validate_pdb_id(pdb_id: str) -> bool:
    """
    Validate PDB ID format.

    Args:
        pdb_id: PDB identifier

    Returns:
        True if valid PDB ID format
    """
    if not isinstance(pdb_id, str):
        return False

    # PDB IDs are 4 characters: 1 digit + 3 alphanumeric
    pdb_pattern = re.compile(r'^[0-9][A-Za-z0-9]{3}$')
    return bool(pdb_pattern.match(pdb_id))


def validate_interface_residues(residues: str) -> bool:
    """
    Validate interface residues string format.

    Args:
        residues: Comma-separated residue indices

    Returns:
        True if valid format
    """
    if not residues:
        return False

    try:
        # Split by comma and check each is a positive integer
        indices = [int(x.strip()) for x in residues.split(',')]
        return all(idx > 0 for idx in indices)
    except (ValueError, AttributeError):
        return False


def validate_numeric_parameter(value: Any, min_value: Optional[float] = None,
                             max_value: Optional[float] = None) -> bool:
    """
    Validate numeric parameter is within bounds.

    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        True if value is valid
    """
    try:
        num_value = float(value)

        if min_value is not None and num_value < min_value:
            return False

        if max_value is not None and num_value > max_value:
            return False

        return True
    except (ValueError, TypeError):
        return False


def validate_input_parameters(params: Dict[str, Any]) -> List[str]:
    """
    Comprehensive validation of input parameters.

    Args:
        params: Dictionary of parameters to validate

    Returns:
        List of validation error messages (empty if all valid)
    """
    errors = []

    # Validate peptide sequence if provided
    if 'peptide_sequence' in params:
        seq = params['peptide_sequence']
        if not validate_amino_acid_sequence(seq):
            errors.append(f"Invalid amino acid sequence: {seq}")

    # Validate peptide length if provided
    if 'peptide_length' in params:
        length = params['peptide_length']
        if not validate_numeric_parameter(length, min_value=8, max_value=50):
            errors.append(f"Invalid peptide length: {length} (must be 8-50)")

    # Validate PDB ID if provided
    if 'pdb_id' in params:
        pdb_id = params['pdb_id']
        if not validate_pdb_id(pdb_id):
            errors.append(f"Invalid PDB ID format: {pdb_id}")

    # Validate interface residues if provided
    if 'interface_residues' in params:
        residues = params['interface_residues']
        if not validate_interface_residues(residues):
            errors.append(f"Invalid interface residues format: {residues}")

    # Validate file paths if provided
    for file_param in ['input_file', 'config_file', 'training_data']:
        if file_param in params and params[file_param]:
            file_path = params[file_param]
            if not validate_file_exists(file_path):
                errors.append(f"File not found: {file_path}")

    # Validate numeric parameters with bounds
    numeric_params = {
        'iterations': (1, 10000),
        'epochs': (1, 1000),
        'batch_size': (1, 1024),
        'learning_rate': (1e-6, 1.0),
        'num_samples': (1, 1000000)
    }

    for param_name, (min_val, max_val) in numeric_params.items():
        if param_name in params:
            value = params[param_name]
            if not validate_numeric_parameter(value, min_val, max_val):
                errors.append(f"Invalid {param_name}: {value} (must be {min_val}-{max_val})")

    return errors


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')

    # Ensure not empty
    if not sanitized:
        sanitized = "output"

    return sanitized


def validate_directory_writable(dir_path: Union[str, Path]) -> bool:
    """
    Check if directory is writable.

    Args:
        dir_path: Directory path

    Returns:
        True if directory is writable
    """
    try:
        dir_path = Path(dir_path)

        # Create directory if it doesn't exist
        dir_path.mkdir(parents=True, exist_ok=True)

        # Try to create a test file
        test_file = dir_path / '.test_write'
        test_file.touch()
        test_file.unlink()

        return True
    except Exception:
        return False