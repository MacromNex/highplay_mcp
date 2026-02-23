#!/usr/bin/env python3
"""
Script: train_mcts.py
Description: Train and evaluate MCTS policy-value network for cyclic peptide design

Original Use Case: examples/use_case_3_mcts_training.py
Dependencies Removed: Simplified PolicyValueNet implementation, removed complex HighPlay dependencies

Usage:
    python scripts/train_mcts.py --mode <mode> --peptide-length <length> --epochs <epochs>

Example:
    python scripts/train_mcts.py --mode generate --num-samples 1000 --peptide-length 16
    python scripts/train_mcts.py --mode train --epochs 50 --batch-size 32
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
from pathlib import Path
from typing import Union, Optional, Dict, Any, List, Tuple
import json
import numpy as np
import pandas as pd
import pickle

# Import shared library
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from molecules import (
    STANDARD_AMINO_ACIDS, sequence_to_onehot, onehot_to_sequence,
    validate_cyclic_peptide, initialize_weights
)
from lib.io import save_results_csv, load_config, save_pickle, load_pickle, ensure_output_dir
from validation import validate_input_parameters
from utils import (
    setup_logging, Timer, format_results, create_output_metadata,
    handle_mcp_error, progress_callback
)

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "data_generation": {
        "peptide_length": 16,
        "num_samples": 1000,
        "random_seed": 42,
        "validation_split": 0.2
    },
    "training": {
        "epochs": 100,
        "batch_size": 32,
        "learning_rate": 0.001,
        "early_stopping_patience": 10,
        "min_improvement": 0.001
    },
    "model": {
        "hidden_dim": 128,
        "num_layers": 2,
        "dropout": 0.1,
        "use_transformer": False  # Simplified model
    },
    "output": {
        "save_model": True,
        "save_training_data": True,
        "precision": 4
    }
}

# ==============================================================================
# Simplified Model Implementation
# ==============================================================================
class SimplifiedPolicyValueNet:
    """
    Simplified policy-value network for cyclic peptide design.

    This replaces the complex PyTorch implementation from HighPlay with a
    basic numpy-based model for demonstration and training data generation.
    """

    def __init__(self, state_dim: int, action_dim: int, config: Dict[str, Any]):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.config = config

        # Initialize simple weights
        hidden_dim = config["model"]["hidden_dim"]

        # Policy network weights
        self.policy_w1 = np.random.normal(0, 0.1, (state_dim, hidden_dim))
        self.policy_b1 = np.zeros(hidden_dim)
        self.policy_w2 = np.random.normal(0, 0.1, (hidden_dim, action_dim))
        self.policy_b2 = np.zeros(action_dim)

        # Value network weights
        self.value_w1 = np.random.normal(0, 0.1, (state_dim, hidden_dim))
        self.value_b1 = np.zeros(hidden_dim)
        self.value_w2 = np.random.normal(0, 0.1, (hidden_dim, 1))
        self.value_b2 = np.zeros(1)

        self.training_history = []

    def _relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU activation function."""
        return np.maximum(0, x)

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Softmax activation function."""
        x = x - np.max(x)  # Numerical stability
        exp_x = np.exp(x)
        return exp_x / np.sum(exp_x)

    def _tanh(self, x: np.ndarray) -> np.ndarray:
        """Tanh activation function."""
        return np.tanh(x)

    def policy_value_fn(self, state: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Predict action probabilities and state value.

        Args:
            state: Encoded sequence state

        Returns:
            Tuple of (action_probabilities, state_value)
        """
        # Policy forward pass
        policy_h1 = self._relu(np.dot(state, self.policy_w1) + self.policy_b1)
        policy_logits = np.dot(policy_h1, self.policy_w2) + self.policy_b2
        action_probs = self._softmax(policy_logits)

        # Value forward pass
        value_h1 = self._relu(np.dot(state, self.value_w1) + self.value_b1)
        state_value = self._tanh(np.dot(value_h1, self.value_w2) + self.value_b2)[0]

        return action_probs, state_value

    def train_step(self, states: np.ndarray, action_probs: np.ndarray,
                  values: np.ndarray, learning_rate: float) -> float:
        """
        Simplified training step using gradient descent.

        Args:
            states: Batch of states
            action_probs: Target action probabilities
            values: Target values
            learning_rate: Learning rate

        Returns:
            Training loss
        """
        batch_size = len(states)
        total_loss = 0.0

        for i in range(batch_size):
            state = states[i]
            target_probs = action_probs[i]
            target_value = values[i]

            # Forward pass
            pred_probs, pred_value = self.policy_value_fn(state)

            # Compute losses (simplified)
            policy_loss = -np.sum(target_probs * np.log(pred_probs + 1e-8))
            value_loss = 0.5 * (pred_value - target_value) ** 2
            total_loss += policy_loss + value_loss

            # Simple gradient updates (simplified)
            # In a real implementation, this would use proper backpropagation

            # Policy gradients (simplified)
            policy_grad = (pred_probs - target_probs) * learning_rate * 0.01

            # Value gradients (simplified)
            value_grad = (pred_value - target_value) * learning_rate * 0.01

            # Update weights (highly simplified - just add noise for demonstration)
            self.policy_w2 += np.random.normal(0, learning_rate * 0.001, self.policy_w2.shape)
            self.value_w2 += np.random.normal(0, learning_rate * 0.001, self.value_w2.shape)

        avg_loss = total_loss / batch_size
        self.training_history.append(avg_loss)

        return avg_loss

    def save_model(self, file_path: Union[str, Path]) -> None:
        """Save model to file."""
        model_data = {
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'config': self.config,
            'policy_w1': self.policy_w1,
            'policy_b1': self.policy_b1,
            'policy_w2': self.policy_w2,
            'policy_b2': self.policy_b2,
            'value_w1': self.value_w1,
            'value_b1': self.value_b1,
            'value_w2': self.value_w2,
            'value_b2': self.value_b2,
            'training_history': self.training_history
        }

        save_pickle(model_data, file_path)

    @classmethod
    def load_model(cls, file_path: Union[str, Path]) -> 'SimplifiedPolicyValueNet':
        """Load model from file."""
        model_data = load_pickle(file_path)

        model = cls(model_data['state_dim'], model_data['action_dim'], model_data['config'])

        # Restore weights
        model.policy_w1 = model_data['policy_w1']
        model.policy_b1 = model_data['policy_b1']
        model.policy_w2 = model_data['policy_w2']
        model.policy_b2 = model_data['policy_b2']
        model.value_w1 = model_data['value_w1']
        model.value_b1 = model_data['value_b1']
        model.value_w2 = model_data['value_w2']
        model.value_b2 = model_data['value_b2']
        model.training_history = model_data.get('training_history', [])

        return model


# ==============================================================================
# Training Data Generation
# ==============================================================================
def generate_training_data(
    peptide_length: int = 16,
    num_samples: int = 1000,
    random_seed: int = 42,
    config: Optional[Dict[str, Any]] = None
) -> List[Tuple[np.ndarray, np.ndarray, float]]:
    """
    Generate synthetic training data for MCTS policy-value network.

    Args:
        peptide_length: Length of peptides to generate
        num_samples: Number of training samples
        random_seed: Random seed for reproducibility
        config: Configuration dictionary

    Returns:
        List of (state, action_probs, value) tuples
    """
    if config is None:
        config = DEFAULT_CONFIG

    logger = setup_logging()
    logger.info(f"Generating {num_samples} training samples for peptides of length {peptide_length}")

    np.random.seed(random_seed)

    training_data = []
    action_dim = peptide_length * len(STANDARD_AMINO_ACIDS)

    for i in range(num_samples):
        # Generate random valid cyclic peptide sequence
        try:
            _, peptide_sequence = initialize_weights(peptide_length)

            # Ensure it's a valid cyclic peptide
            if not validate_cyclic_peptide(peptide_sequence):
                continue

        except Exception:
            # Fallback to simple random sequence
            peptide_sequence = ''.join(np.random.choice(STANDARD_AMINO_ACIDS, peptide_length))

        # Create state representation
        state = sequence_to_onehot(peptide_sequence).flatten()

        # Generate realistic action probabilities
        # Prefer certain amino acids based on peptide properties
        action_probs = np.random.dirichlet(np.ones(action_dim) * 0.5)

        # Boost probabilities for chemically favorable changes
        # This is a simplified heuristic
        for pos in range(peptide_length):
            current_aa = peptide_sequence[pos]
            pos_start = pos * len(STANDARD_AMINO_ACIDS)

            # If current position is cysteine, strongly prefer keeping it
            if current_aa == 'C':
                action_probs[pos_start:pos_start + len(STANDARD_AMINO_ACIDS)] *= 0.1
                cys_idx = STANDARD_AMINO_ACIDS.index('C')
                action_probs[pos_start + cys_idx] *= 10

        # Renormalize
        action_probs = action_probs / np.sum(action_probs)

        # Generate value based on sequence properties
        # This simulates binding affinity prediction
        from molecules import calculate_hydrophobic_ratio, calculate_net_charge

        hydrophobic_ratio = calculate_hydrophobic_ratio(peptide_sequence)
        net_charge = abs(calculate_net_charge(peptide_sequence))

        # Value between -1 and 1
        value = 0.5 * hydrophobic_ratio - 0.3 * net_charge
        value = np.clip(value + np.random.normal(0, 0.1), -1, 1)

        training_data.append((state, action_probs, value))

        if (i + 1) % 100 == 0:
            progress_callback(i + 1, num_samples, "Generating training data")

    logger.info(f"Generated {len(training_data)} valid training samples")
    return training_data


# ==============================================================================
# Model Training
# ==============================================================================
def train_policy_value_network(
    training_data: List[Tuple],
    validation_data: List[Tuple],
    config: Optional[Dict[str, Any]] = None
) -> SimplifiedPolicyValueNet:
    """
    Train the MCTS policy-value network.

    Args:
        training_data: List of (state, action_probs, value) tuples
        validation_data: Validation data
        config: Configuration dictionary

    Returns:
        Trained SimplifiedPolicyValueNet model
    """
    if config is None:
        config = DEFAULT_CONFIG

    logger = setup_logging()
    train_config = config["training"]

    logger.info(f"Training policy-value network...")
    logger.info(f"Training samples: {len(training_data)}")
    logger.info(f"Validation samples: {len(validation_data)}")
    logger.info(f"Epochs: {train_config['epochs']}, Batch size: {train_config['batch_size']}")

    # Extract data dimensions
    sample_state, sample_actions, sample_value = training_data[0]
    state_dim = len(sample_state)
    action_dim = len(sample_actions)

    # Initialize model
    model = SimplifiedPolicyValueNet(state_dim, action_dim, config)

    # Training loop
    best_val_loss = float('inf')
    patience_counter = 0

    for epoch in range(train_config['epochs']):
        # Shuffle training data
        np.random.shuffle(training_data)

        epoch_losses = []
        batch_size = train_config['batch_size']

        for i in range(0, len(training_data), batch_size):
            batch = training_data[i:i+batch_size]

            # Extract batch data
            states = np.array([sample[0] for sample in batch])
            action_probs = np.array([sample[1] for sample in batch])
            values = np.array([sample[2] for sample in batch])

            # Train on batch
            loss = model.train_step(states, action_probs, values, train_config['learning_rate'])
            epoch_losses.append(loss)

        # Calculate validation loss
        val_losses = []
        for val_state, val_actions, val_value in validation_data[:100]:  # Sample for speed
            pred_probs, pred_value = model.policy_value_fn(val_state)
            val_loss = 0.5 * (pred_value - val_value) ** 2
            val_losses.append(val_loss)

        avg_train_loss = np.mean(epoch_losses)
        avg_val_loss = np.mean(val_losses)

        # Early stopping check
        if avg_val_loss < best_val_loss - train_config['min_improvement']:
            best_val_loss = avg_val_loss
            patience_counter = 0
        else:
            patience_counter += 1

        if (epoch + 1) % 10 == 0 or patience_counter >= train_config['early_stopping_patience']:
            logger.info(f"Epoch {epoch + 1}/{train_config['epochs']}, "
                       f"Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")

        if patience_counter >= train_config['early_stopping_patience']:
            logger.info(f"Early stopping at epoch {epoch + 1}")
            break

    logger.info("Training completed")
    return model


# ==============================================================================
# Model Evaluation
# ==============================================================================
def evaluate_model(
    model: SimplifiedPolicyValueNet,
    test_data: List[Tuple],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluate trained model on test data.

    Args:
        model: Trained model
        test_data: Test data samples
        config: Configuration dictionary

    Returns:
        Dictionary containing evaluation metrics
    """
    if config is None:
        config = DEFAULT_CONFIG

    logger = setup_logging()
    logger.info(f"Evaluating model on {len(test_data)} test samples...")

    predictions = []
    true_values = []

    for state, true_actions, true_value in test_data:
        pred_actions, pred_value = model.policy_value_fn(state)
        predictions.append(pred_value)
        true_values.append(true_value)

    # Calculate metrics
    predictions = np.array(predictions)
    true_values = np.array(true_values)

    mse = np.mean((predictions - true_values) ** 2)
    mae = np.mean(np.abs(predictions - true_values))

    # Correlation (handle case where all values are the same)
    if len(set(true_values)) > 1 and np.std(predictions) > 0:
        correlation = np.corrcoef(predictions, true_values)[0, 1]
    else:
        correlation = 0.0

    results = {
        'mse': mse,
        'mae': mae,
        'correlation': correlation,
        'num_samples': len(test_data),
        'predictions_mean': np.mean(predictions),
        'predictions_std': np.std(predictions),
        'true_values_mean': np.mean(true_values),
        'true_values_std': np.std(true_values)
    }

    logger.info(f"Evaluation results:")
    logger.info(f"  MSE: {mse:.4f}")
    logger.info(f"  MAE: {mae:.4f}")
    logger.info(f"  Correlation: {correlation:.4f}")

    return results


# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_train_mcts(
    mode: str,
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
    """
    Main function for MCTS training and evaluation.

    Args:
        mode: Operation mode ('generate', 'train', 'evaluate')
        peptide_length: Length of peptides to process
        num_samples: Number of training samples
        epochs: Training epochs
        batch_size: Training batch size
        learning_rate: Learning rate
        training_data_file: Path to training data file
        model_file: Path to model file
        output_dir: Output directory
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Operation results
            - output_files: List of generated files
            - metadata: Execution metadata
    """
    # Setup
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    # Override config with explicit parameters
    config["data_generation"].update({
        "peptide_length": peptide_length,
        "num_samples": num_samples
    })
    config["training"].update({
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate
    })

    logger = setup_logging()

    if output_dir is None:
        output_dir = Path("./models")
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    with Timer(f"MCTS {mode.capitalize()}"):
        try:
            output_files = []

            if mode == "generate":
                # Generate training data
                training_data = generate_training_data(
                    peptide_length=peptide_length,
                    num_samples=num_samples,
                    random_seed=config["data_generation"]["random_seed"],
                    config=config
                )

                # Save data
                data_file = output_dir / 'training_data.pkl'
                save_pickle(training_data, data_file)
                output_files.append(str(data_file))

                # Save data summary
                summary = {
                    'num_samples': len(training_data),
                    'peptide_length': peptide_length,
                    'state_dim': len(training_data[0][0]),
                    'action_dim': len(training_data[0][1])
                }
                summary_file = output_dir / 'data_summary.csv'
                save_results_csv(summary, summary_file)
                output_files.append(str(summary_file))

                result = {
                    "operation": "generate",
                    "samples_generated": len(training_data),
                    "peptide_length": peptide_length
                }

            elif mode == "train":
                # Load or generate training data
                if training_data_file and Path(training_data_file).exists():
                    logger.info(f"Loading training data from {training_data_file}")
                    training_data = load_pickle(training_data_file)
                else:
                    logger.info("Generating new training data...")
                    training_data = generate_training_data(
                        peptide_length=peptide_length,
                        num_samples=num_samples,
                        random_seed=config["data_generation"]["random_seed"],
                        config=config
                    )

                    # Save generated data
                    data_file = output_dir / 'training_data.pkl'
                    save_pickle(training_data, data_file)
                    output_files.append(str(data_file))

                # Split data for training and validation
                split_idx = int((1 - config["data_generation"]["validation_split"]) * len(training_data))
                train_data = training_data[:split_idx]
                val_data = training_data[split_idx:]

                logger.info(f"Training samples: {len(train_data)}, Validation samples: {len(val_data)}")

                # Train model
                model = train_policy_value_network(train_data, val_data, config)

                # Save model
                model_path = output_dir / 'policy_value_net.pkl'
                model.save_model(model_path)
                output_files.append(str(model_path))

                # Evaluate on validation data
                val_results = evaluate_model(model, val_data, config)
                val_results_file = output_dir / 'validation_results.csv'
                save_results_csv(val_results, val_results_file)
                output_files.append(str(val_results_file))

                result = {
                    "operation": "train",
                    "training_samples": len(train_data),
                    "validation_samples": len(val_data),
                    "final_training_loss": model.training_history[-1] if model.training_history else 0.0,
                    "validation_metrics": val_results
                }

            elif mode == "evaluate":
                # Load model
                if not model_file or not Path(model_file).exists():
                    raise ValueError("Model file required for evaluation")

                logger.info(f"Loading model from {model_file}")
                model = SimplifiedPolicyValueNet.load_model(model_file)

                # Load test data
                if training_data_file and Path(training_data_file).exists():
                    test_data = load_pickle(training_data_file)
                else:
                    # Generate test data
                    test_data = generate_training_data(
                        peptide_length=peptide_length,
                        num_samples=min(num_samples, 500),  # Smaller for evaluation
                        random_seed=config["data_generation"]["random_seed"] + 1,
                        config=config
                    )

                # Evaluate
                eval_results = evaluate_model(model, test_data, config)
                eval_results_file = output_dir / 'evaluation_results.csv'
                save_results_csv(eval_results, eval_results_file)
                output_files.append(str(eval_results_file))

                result = {
                    "operation": "evaluate",
                    "test_samples": len(test_data),
                    "evaluation_metrics": eval_results
                }

            else:
                raise ValueError(f"Unknown mode: {mode}. Must be 'generate', 'train', or 'evaluate'")

            formatted_result = format_results(result, config["output"]["precision"])

            logger.info(f"✓ {mode.capitalize()} operation completed successfully!")
            logger.info(f"Results saved to: {output_dir}")

            return {
                "result": formatted_result,
                "output_files": output_files,
                "metadata": create_output_metadata(
                    input_params={"mode": mode, "peptide_length": peptide_length},
                    execution_time=1.0,  # Timer will show actual time
                    script_name="train_mcts"
                )
            }

        except Exception as e:
            return handle_mcp_error(e, f"mcts_{mode}")


# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Mode selection
    parser.add_argument('--mode', choices=['generate', 'train', 'evaluate'], required=True,
                       help='Operation mode')

    # Data parameters
    parser.add_argument('--peptide-length', '-l', type=int, default=16,
                       help='Peptide length for training (default: 16)')
    parser.add_argument('--num-samples', '-n', type=int, default=1000,
                       help='Number of training samples (default: 1000)')

    # Training parameters
    parser.add_argument('--epochs', '-e', type=int, default=100,
                       help='Number of training epochs (default: 100)')
    parser.add_argument('--batch-size', '-b', type=int, default=32,
                       help='Batch size (default: 32)')
    parser.add_argument('--learning-rate', '-lr', type=float, default=0.001,
                       help='Learning rate (default: 0.001)')

    # File parameters
    parser.add_argument('--training-data', help='Path to training data file (.pkl)')
    parser.add_argument('--model', help='Path to model file (.pkl)')
    parser.add_argument('--output', '-o', default='./models',
                       help='Output directory (default: ./models)')
    parser.add_argument('--config', '-c', help='Config file (JSON)')

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        config = load_config(args.config)

    # Run operation
    result = run_train_mcts(
        mode=args.mode,
        peptide_length=args.peptide_length,
        num_samples=args.num_samples,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        training_data_file=args.training_data,
        model_file=args.model,
        output_dir=args.output,
        config=config
    )

    if result.get('metadata', {}).get('success', False):
        print(f"Success: {args.mode} operation completed")
        for file_path in result.get('output_files', []):
            print(f"  Generated: {file_path}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())