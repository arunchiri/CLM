# Claims Denial Prediction with Hierarchical Reasoning Model (HRM)

A deep learning model for predicting insurance claims denial status and denial codes using a novel Hierarchical Reasoning Machine architecture optimized for tabular data.

## Overview

This project implements a sophisticated neural network architecture designed specifically for insurance claims processing. The model performs two primary tasks:

1. **Binary Classification**: Predicts whether a claim will be denied or approved
2. **Multi-class Classification**: For denied claims, predicts the specific denial code/reason

The architecture uses a Hierarchical Reasoning Machine (HRM) with dual-level reasoning cycles, inspired by cognitive processing models, to handle complex tabular relationships in claims data.

## Features

- **Hierarchical Reasoning**: Two-level reasoning architecture (H-level and L-level) with configurable cycles
- **Multi-task Learning**: Simultaneous prediction of denial status and denial codes
- **Robust Data Processing**: Handles mixed data types (numeric, binary, categorical) with comprehensive preprocessing
- **Environment-aware Training**: Incorporates payer-specific weighting for domain adaptation
- **Causal Feature Engineering**: Derives causally-relevant features to avoid data leakage
- **Mixed Precision Training**: Supports AMP for faster training on modern GPUs

## Architecture

The HRM model consists of:

- **Input Layer**: Handles numeric, binary, and categorical features with learned embeddings
- **Hierarchical Reasoning Module**: 
  - H-level: High-level abstract reasoning
  - L-level: Low-level detail processing
  - Configurable cycles between levels mimicking cognitive processing
- **Output Heads**: Task-specific heads for denial prediction and code classification

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/claims-denial-prediction.git
cd claims-denial-prediction

# Install dependencies
pip install torch torchvision numpy pandas scikit-learn tqdm
```

### Requirements

- Python 3.8+
- PyTorch 1.9+
- NumPy
- Pandas
- Scikit-learn
- tqdm

## Data Format

The model expects a CSV file with the following columns:

### Required Columns
- `ClaimAmount`: Numeric claim amount
- `Reimbursement`: Reimbursement amount
- `DenialStatus`: Target binary label (0=approved, 1=denied)
- `Denial_Code`: Target denial reason code
- `PayerID`: Insurance payer identifier

### Optional Columns
- `ProviderID`: Healthcare provider ID
- `ICD10_Code`: ICD-10 diagnosis code
- `CPT_Code`: CPT procedure code
- `HCPCS_Code`: HCPCS code
- `Modifier`: Procedure modifier
- `DRG_Code`: Diagnosis Related Group code
- `Plan_Type`: Insurance plan type
- `PriorAuth_Obtained`: Prior authorization status
- `Referral_Required`: Referral requirement status
- Date columns: `ServiceDate`, `SubmissionDate`, `ProcessedDate`, etc.

## Quick Start

### Basic Training

```bash
python train_clm.py --csv data/claims_data.csv --epochs 25 --batch_size 256
```

### Advanced Configuration

```bash
python train_clm.py \
    --csv data/claims_data.csv \
    --hidden_size 256 \
    --H_layers 3 \
    --L_layers 3 \
    --H_cycles 3 \
    --L_cycles 2 \
    --epochs 50 \
    --batch_size 512 \
    --lr 1e-3 \
    --amp \
    --time_split \
    --guard_leakage
```

### Command Line Arguments

#### Data Arguments
- `--csv`: Path to CSV file (required)
- `--val_split`: Validation split ratio (default: 0.2)
- `--time_split`: Use time-based validation split
- `--min_freq`: Minimum frequency for categorical vocabulary (default: 1)
- `--guard_leakage`: Remove potentially leaking features

#### Model Architecture
- `--hidden_size`: Hidden dimension size (default: 128)
- `--H_layers`: Number of H-level reasoning layers (default: 2)
- `--L_layers`: Number of L-level reasoning layers (default: 2)
- `--H_cycles`: Number of H-level reasoning cycles (default: 2)
- `--L_cycles`: Number of L-level reasoning cycles (default: 2)
- `--dropout`: Dropout rate (default: 0.05)
- `--expansion`: MLP expansion factor (default: 2.0)

#### Training Configuration
- `--epochs`: Number of training epochs (default: 25)
- `--batch_size`: Batch size (default: 256)
- `--lr`: Learning rate (default: 3e-4)
- `--weight_decay`: Weight decay (default: 1e-4)
- `--denial_w`: Weight for denial status loss (default: 1.0)
- `--code_w`: Weight for denial code loss (default: 0.8)

#### System Arguments
- `--amp`: Enable mixed precision training
- `--prefer_bf16`: Prefer bfloat16 over float16 for AMP
- `--num_workers`: DataLoader workers (default: 0)
- `--seed`: Random seed (default: 42)

## Model Architecture Details

### Hierarchical Reasoning Machine

The HRM architecture implements a two-level reasoning system:

1. **L-Level (Low-Level)**: Processes detailed, specific patterns in the data
2. **H-Level (High-Level)**: Integrates information for abstract reasoning

The model alternates between these levels in configurable cycles, allowing for sophisticated reasoning patterns that can capture both fine-grained details and high-level relationships.

### SwiGLU Activation

Uses SwiGLU (Swish-Gated Linear Unit) activation functions with gating mechanisms for improved learning dynamics.

## Feature Engineering

The model automatically engineers causal features to improve prediction accuracy:

- **Timely Filing Lateness**: Days late after contracted submission deadline
- **Over Benefit Amount**: Amount exceeding benefit limits
- **Coverage Gap**: Days between coverage end and service date
- **High Edits Indicator**: Binary flag for high clearinghouse edit counts
- **Processing Lag**: Time between submission and processing (optional)

## Training Process

1. **Data Loading**: Parses CSV and handles mixed data types
2. **Feature Engineering**: Derives causal features automatically
3. **Preprocessing**: Normalizes numeric features, builds categorical vocabularies
4. **Model Training**: Multi-task learning with environment weighting
5. **Evaluation**: Comprehensive metrics including AUC, PR-AUC, F1, Brier score
6. **Checkpointing**: Saves best model with full configuration

## Evaluation Metrics

### Denial Status (Binary Classification)
- ROC-AUC
- PR-AUC (Average Precision)
- F1 Score
- Brier Score

### Denial Codes (Multi-class Classification)
- Accuracy (on denied claims only)
- Top-5 Accuracy
- Macro F1 Score

## Output

The model saves:
- **Model checkpoint**: Complete model state with configuration
- **Preprocessing artifacts**: Scalers, vocabularies, feature mappings
- **Training configuration**: All hyperparameters and settings
- **Performance metrics**: Validation scores and training history

## Advanced Usage

### Custom Model Configuration

```python
from hrm_model import TabularHRMConfig, ClaimsSpecificHRM

config = TabularHRMConfig(
    numeric_dim=10,
    binary_dim=5,
    cat_vocab_sizes=[100, 50, 200],
    cat_emb_dims=[16, 8, 32],
    hidden_size=256,
    H_layers=4,
    L_layers=3,
    H_cycles=3,
    L_cycles=2
)

model = ClaimsSpecificHRM(config, num_denial_classes=50)
```

### Feature Extraction

```python
# Extract learned representations
embeddings = model.get_embeddings(batch)
```

## Best Practices

1. **Data Quality**: Ensure consistent date formats and handle missing values appropriately
2. **Leakage Prevention**: Use `--guard_leakage` for pre-submission predictions
3. **Time Splitting**: Use `--time_split` for realistic temporal evaluation
4. **Hyperparameter Tuning**: Start with default parameters and adjust based on dataset size
5. **Mixed Precision**: Enable `--amp` for faster training on compatible GPUs

## Troubleshooting

### Common Issues

**Memory Issues**: Reduce `batch_size` or `hidden_size`
```bash
python train_clm.py --csv data.csv --batch_size 128 --hidden_size 64
```

**Convergence Problems**: Adjust learning rate or add regularization
```bash
python train_clm.py --csv data.csv --lr 1e-4 --weight_decay 1e-3
```

**Class Imbalance**: The model automatically handles class imbalance with computed positive weights

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this code in your research, please cite:

```bibtex
@misc{hrm_claims_prediction,
  title={Hierarchical Reasoning Machine for Insurance Claims Denial Prediction},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/claims-denial-prediction}
}
```

## Acknowledgments

- Inspired by cognitive processing models and hierarchical reasoning systems
- Built with PyTorch and modern deep learning best practices
- Designed for real-world insurance claims processing workflows
