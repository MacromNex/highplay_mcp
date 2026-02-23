#!/usr/bin/env python3
"""
MCP Server for Cyclic Peptide Tools

Provides both synchronous and asynchronous (submit) APIs for cyclic peptide analysis,
MCTS training, and peptide design.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List, Dict, Any
import sys
import os

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"

# Add paths to Python path
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from jobs.manager import job_manager
from loguru import logger

# Create MCP server
mcp = FastMCP("cycpep-tools")

logger.info(f"CycPep MCP Server initialized")
logger.info(f"Scripts directory: {SCRIPTS_DIR}")
logger.info(f"Jobs directory: {job_manager.jobs_dir}")

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted cyclic peptide computation job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    logger.info(f"Checking status for job {job_id}")
    return job_manager.get_job_status(job_id)


@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed cyclic peptide computation job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    logger.info(f"Getting results for job {job_id}")
    return job_manager.get_job_result(job_id)


@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    logger.info(f"Getting log for job {job_id}, tail={tail}")
    return job_manager.get_job_log(job_id, tail)


@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running cyclic peptide computation job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    logger.info(f"Cancelling job {job_id}")
    return job_manager.cancel_job(job_id)


@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted cyclic peptide computation jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    logger.info(f"Listing jobs with status filter: {status}")
    return job_manager.list_jobs(status)


# ==============================================================================
# Synchronous Tools (for fast operations < 10 min)
# ==============================================================================

@mcp.tool()
def analyze_cyclic_peptide(
    input_file: Optional[str] = None,
    pdb_id: Optional[str] = None,
    peptide_seq: Optional[str] = None,
    receptor_seq: Optional[str] = None,
    suggest_mutations: bool = False,
    output_file: Optional[str] = None
) -> dict:
    """
    Analyze cyclic peptide-protein interactions with binding metrics and mutation suggestions.

    Fast operation - returns results immediately (typically <10 seconds).

    Args:
        input_file: CSV file with peptide-protein data
        pdb_id: PDB ID to analyze (if using input_file)
        peptide_seq: Direct peptide sequence input
        receptor_seq: Direct receptor sequence input
        suggest_mutations: Whether to suggest mutations for improved binding
        output_file: Optional path to save analysis results

    Returns:
        Dictionary with analysis results including binding metrics and mutations
    """
    logger.info(f"Starting peptide analysis - pdb_id: {pdb_id}, suggest_mutations: {suggest_mutations}")

    try:
        from analyze_peptide import run_analyze_peptide

        result = run_analyze_peptide(
            input_file=input_file,
            pdb_id=pdb_id,
            peptide_seq=peptide_seq,
            receptor_seq=receptor_seq,
            suggest_mutations=suggest_mutations,
            output_file=output_file
        )
        logger.info(f"Peptide analysis completed successfully")
        return {"status": "success", **result}

    except FileNotFoundError as e:
        error_msg = f"File not found: {e}"
        logger.error(error_msg)
        return {"status": "error", "error": error_msg}
    except ValueError as e:
        error_msg = f"Invalid input: {e}"
        logger.error(error_msg)
        return {"status": "error", "error": error_msg}
    except Exception as e:
        error_msg = f"Analysis failed: {e}"
        logger.error(error_msg)
        return {"status": "error", "error": error_msg}


@mcp.tool()
def train_mcts_generate_data(
    peptide_length: int = 16,
    num_samples: int = 1000,
    output_dir: Optional[str] = None
) -> dict:
    """
    Generate training data for MCTS policy-value network.

    Fast operation - generates synthetic peptide training data.

    Args:
        peptide_length: Length of peptides to generate (default: 16)
        num_samples: Number of training samples to generate (default: 1000)
        output_dir: Directory to save training data

    Returns:
        Dictionary with generation results and data file paths
    """
    logger.info(f"Generating MCTS training data - length: {peptide_length}, samples: {num_samples}")

    try:
        from train_mcts import run_train_mcts

        result = run_train_mcts(
            mode="generate",
            peptide_length=peptide_length,
            num_samples=num_samples,
            output_dir=output_dir
        )
        logger.info(f"Training data generation completed")
        return {"status": "success", **result}

    except Exception as e:
        error_msg = f"Data generation failed: {e}"
        logger.error(error_msg)
        return {"status": "error", "error": error_msg}


@mcp.tool()
def train_mcts_evaluate_model(
    model_file: str,
    training_data_file: Optional[str] = None,
    output_dir: Optional[str] = None
) -> dict:
    """
    Evaluate a trained MCTS policy-value model.

    Fast operation - evaluates model performance on test data.

    Args:
        model_file: Path to trained model file
        training_data_file: Path to training data for evaluation
        output_dir: Directory to save evaluation results

    Returns:
        Dictionary with evaluation metrics and results
    """
    logger.info(f"Evaluating MCTS model: {model_file}")

    try:
        from train_mcts import run_train_mcts

        result = run_train_mcts(
            mode="evaluate",
            model_file=model_file,
            training_data_file=training_data_file,
            output_dir=output_dir
        )
        logger.info(f"Model evaluation completed")
        return {"status": "success", **result}

    except Exception as e:
        error_msg = f"Model evaluation failed: {e}"
        logger.error(error_msg)
        return {"status": "error", "error": error_msg}


# ==============================================================================
# Submit Tools (for long-running operations > 10 min)
# ==============================================================================

@mcp.tool()
def submit_mcts_training(
    peptide_length: int = 16,
    epochs: int = 100,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    training_data_file: Optional[str] = None,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit MCTS policy-value network training job.

    This task may take more than 10 minutes depending on epochs and data size.
    Use get_job_status() to monitor progress and get_job_result() to retrieve results.

    Args:
        peptide_length: Length of peptides for training (default: 16)
        epochs: Number of training epochs (default: 100)
        batch_size: Training batch size (default: 32)
        learning_rate: Learning rate for training (default: 0.001)
        training_data_file: Path to training data file (optional)
        output_dir: Directory for training outputs
        job_name: Optional name for the job (for easier tracking)

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs
    """
    logger.info(f"Submitting MCTS training job - epochs: {epochs}, batch_size: {batch_size}")

    script_path = str(SCRIPTS_DIR / "train_mcts.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "mode": "train",
            "peptide_length": peptide_length,
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "training_data_file": training_data_file
        },
        job_name=job_name or f"mcts_training_{epochs}epochs"
    )


@mcp.tool()
def submit_peptide_design(
    input_file: Optional[str] = None,
    target_id: Optional[str] = None,
    receptor_seq: Optional[str] = None,
    interface_residues: Optional[str] = None,
    peptide_length: int = 16,
    iterations: int = 300,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit cyclic peptide design job using MCTS optimization.

    This is a long-running task (typically >10 minutes for 300+ iterations).
    Uses MCTS reinforcement learning to optimize peptide sequences.

    Args:
        input_file: CSV file with target protein data
        target_id: Target protein ID from input file
        receptor_seq: Direct receptor sequence input
        interface_residues: Binding site residues (comma-separated)
        peptide_length: Desired peptide length (default: 16)
        iterations: MCTS optimization iterations (default: 300)
        output_dir: Directory for design outputs
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs
    """
    logger.info(f"Submitting peptide design job - target: {target_id}, iterations: {iterations}")

    script_path = str(SCRIPTS_DIR / "design_peptide.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input": input_file,
            "target": target_id,
            "receptor_seq": receptor_seq,
            "interface_residues": interface_residues,
            "peptide_length": peptide_length,
            "iterations": iterations
        },
        job_name=job_name or f"design_{target_id or 'peptide'}_{iterations}iter"
    )


@mcp.tool()
def submit_batch_peptide_analysis(
    input_file: str,
    suggest_mutations: bool = False,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch analysis job for multiple cyclic peptides.

    Processes multiple peptide-protein pairs from input CSV file.
    Suitable for analyzing large datasets or screening libraries.

    Args:
        input_file: CSV file with multiple peptide-protein pairs
        suggest_mutations: Whether to suggest mutations for each peptide
        output_dir: Directory for batch analysis outputs
        job_name: Optional name for the batch job

    Returns:
        Dictionary with job_id for tracking the batch analysis job
    """
    logger.info(f"Submitting batch analysis job - file: {input_file}")

    script_path = str(SCRIPTS_DIR / "analyze_peptide.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input": input_file,
            "suggest_mutations": suggest_mutations
        },
        job_name=job_name or f"batch_analysis_{Path(input_file).stem}"
    )


# ==============================================================================
# Information and Help Tools
# ==============================================================================

@mcp.tool()
def get_server_info() -> dict:
    """
    Get information about the CycPep MCP server and available tools.

    Returns:
        Dictionary with server information, available tools, and usage examples
    """
    return {
        "server_name": "cycpep-tools",
        "version": "1.0.0",
        "description": "MCP server for cyclic peptide computational tools",
        "scripts_directory": str(SCRIPTS_DIR),
        "jobs_directory": str(job_manager.jobs_dir),
        "sync_tools": [
            "analyze_cyclic_peptide",
            "train_mcts_generate_data",
            "train_mcts_evaluate_model"
        ],
        "submit_tools": [
            "submit_mcts_training",
            "submit_peptide_design",
            "submit_batch_peptide_analysis"
        ],
        "job_management_tools": [
            "get_job_status",
            "get_job_result",
            "get_job_log",
            "cancel_job",
            "list_jobs"
        ],
        "example_workflows": {
            "quick_analysis": "Use analyze_cyclic_peptide with SMILES or sequence",
            "peptide_design": "1) submit_peptide_design, 2) get_job_status, 3) get_job_result",
            "mcts_pipeline": "1) train_mcts_generate_data, 2) submit_mcts_training, 3) train_mcts_evaluate_model"
        }
    }


# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    logger.info("Starting CycPep MCP Server...")
    mcp.run()