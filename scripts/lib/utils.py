"""
General utility functions for cyclic peptide MCP scripts.

These functions provide common utilities like logging, progress tracking, and error handling.
"""

import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def setup_logging(log_file: Optional[Union[str, Path]] = None,
                 level: int = logging.INFO) -> logging.Logger:
    """
    Setup logging for MCP scripts.

    Args:
        log_file: Optional log file path
        level: Logging level

    Returns:
        Configured logger
    """
    logger = logging.getLogger('cyclic_peptide_mcp')
    logger.setLevel(level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def filter_dict(before_dict: Dict[str, Any], filtered_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter dictionary to keep only specified keys.

    Extracted from repo/HighPlay/train.py lines 16-20.

    Args:
        before_dict: Original dictionary
        filtered_dict: Dictionary defining keys to keep

    Returns:
        Filtered dictionary
    """
    return {key: before_dict[key] for key in filtered_dict if key in before_dict}


def progress_callback(current: int, total: int, prefix: str = "Progress") -> None:
    """
    Simple progress callback for long-running operations.

    Args:
        current: Current progress
        total: Total items
        prefix: Progress message prefix
    """
    percent = (current / total) * 100 if total > 0 else 0
    print(f"\r{prefix}: {current}/{total} ({percent:.1f}%)", end='', flush=True)

    if current >= total:
        print()  # New line when complete


class Timer:
    """Simple timer context manager for measuring execution time."""

    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        duration = end_time - self.start_time
        print(f"{self.name} completed in {duration:.2f} seconds")


def format_results(results: Dict[str, Any], precision: int = 4) -> Dict[str, Any]:
    """
    Format numerical results for display.

    Args:
        results: Results dictionary
        precision: Decimal precision for floats

    Returns:
        Formatted results dictionary
    """
    formatted = {}

    for key, value in results.items():
        if isinstance(value, float):
            formatted[key] = round(value, precision)
        elif isinstance(value, dict):
            formatted[key] = format_results(value, precision)
        else:
            formatted[key] = value

    return formatted


def merge_configs(default_config: Dict[str, Any],
                 user_config: Optional[Dict[str, Any]] = None,
                 **kwargs) -> Dict[str, Any]:
    """
    Merge configuration dictionaries with precedence.

    Args:
        default_config: Default configuration
        user_config: User-provided configuration (optional)
        **kwargs: Additional keyword arguments (highest precedence)

    Returns:
        Merged configuration dictionary
    """
    config = default_config.copy()

    if user_config:
        config.update(user_config)

    if kwargs:
        config.update(kwargs)

    return config


def safe_execute(func, *args, default_return=None, **kwargs):
    """
    Safely execute function with error handling.

    Args:
        func: Function to execute
        *args: Positional arguments
        default_return: Value to return on error
        **kwargs: Keyword arguments

    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger = logging.getLogger('cyclic_peptide_mcp')
        logger.warning(f"Error executing {func.__name__}: {e}")
        return default_return


def create_output_metadata(input_params: Dict[str, Any],
                          execution_time: float,
                          script_name: str) -> Dict[str, Any]:
    """
    Create standardized output metadata.

    Args:
        input_params: Input parameters used
        execution_time: Execution time in seconds
        script_name: Name of the script

    Returns:
        Metadata dictionary
    """
    return {
        "script": script_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "execution_time_seconds": round(execution_time, 2),
        "input_parameters": input_params,
        "success": True
    }


def handle_mcp_error(error: Exception, operation: str) -> Dict[str, Any]:
    """
    Standardized error handling for MCP tools.

    Args:
        error: Exception that occurred
        operation: Name of operation that failed

    Returns:
        Error result dictionary
    """
    error_result = {
        "success": False,
        "error": str(error),
        "operation": operation,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    logger = logging.getLogger('cyclic_peptide_mcp')
    logger.error(f"Error in {operation}: {error}")

    return error_result