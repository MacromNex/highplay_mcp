"""
Input/output utilities for cyclic peptide MCP scripts.

These functions handle file loading and saving with appropriate error handling.
"""

import csv
import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd


def load_peptide_csv(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load peptide data from CSV file with error handling.

    Args:
        file_path: Path to CSV file

    Returns:
        Pandas DataFrame with peptide data

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")

    try:
        df = pd.read_csv(file_path)
        if df.empty:
            raise ValueError(f"CSV file is empty: {file_path}")
        return df
    except Exception as e:
        raise ValueError(f"Error reading CSV file {file_path}: {e}")


def save_results_csv(data: Union[Dict, List[Dict]], file_path: Union[str, Path]) -> None:
    """
    Save results to CSV file.

    Args:
        data: Dictionary or list of dictionaries to save
        file_path: Output file path
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(data, dict):
        data = [data]

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)


def load_config(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        file_path: Path to JSON config file

    Returns:
        Configuration dictionary
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")

    try:
        with open(file_path, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        raise ValueError(f"Error reading config file {file_path}: {e}")


def save_config(config: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """
    Save configuration to JSON file.

    Args:
        config: Configuration dictionary
        file_path: Output file path
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2, default=str)
    except Exception as e:
        raise ValueError(f"Error saving config to {file_path}: {e}")


def save_pickle(data: Any, file_path: Union[str, Path]) -> None:
    """
    Save data to pickle file.

    Args:
        data: Data to pickle
        file_path: Output file path
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        raise ValueError(f"Error saving pickle to {file_path}: {e}")


def load_pickle(file_path: Union[str, Path]) -> Any:
    """
    Load data from pickle file.

    Args:
        file_path: Path to pickle file

    Returns:
        Unpickled data
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Pickle file not found: {file_path}")

    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        return data
    except Exception as e:
        raise ValueError(f"Error loading pickle from {file_path}: {e}")


def save_sequence_file(sequence: str, file_path: Union[str, Path], format: str = "fasta") -> None:
    """
    Save peptide sequence to file.

    Args:
        sequence: Amino acid sequence
        file_path: Output file path
        format: Output format ("fasta", "txt")
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(file_path, 'w') as f:
            if format.lower() == "fasta":
                f.write(f">peptide\n{sequence}\n")
            else:
                f.write(sequence)
    except Exception as e:
        raise ValueError(f"Error saving sequence to {file_path}: {e}")


def load_sequence_file(file_path: Union[str, Path]) -> str:
    """
    Load peptide sequence from file.

    Args:
        file_path: Input file path

    Returns:
        Amino acid sequence
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Sequence file not found: {file_path}")

    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()

        # Handle FASTA format
        if content.startswith('>'):
            lines = content.split('\n')
            sequence = ''.join(lines[1:])
        else:
            sequence = content

        return sequence.replace(' ', '').replace('\n', '').upper()

    except Exception as e:
        raise ValueError(f"Error loading sequence from {file_path}: {e}")


def ensure_output_dir(file_path: Union[str, Path]) -> Path:
    """
    Ensure output directory exists.

    Args:
        file_path: File path (directory will be created)

    Returns:
        Path object
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    return file_path