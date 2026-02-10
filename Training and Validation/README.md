# Training and Validation

## Partition datasets (70/20/10)

**What it means:** Split your labeled dataset into three non-overlapping sets:

| Split   | Fraction | Purpose |
|--------|----------|--------|
| **Train** | 70% | Fit the model (weights and biases). |
| **Val**   | 20% | Tune hyperparameters, early stopping, and model selection. Not used for training. |
| **Test**  | 10% | Final evaluation only. Use once at the end to report metrics; never use for training or tuning. |

**Why:** Using separate val and test sets avoids overfitting to your evaluation data and gives trustworthy performance estimates.

**How to complete:** Run the `partition_dataset.py` script from the root directory.

### Usage

```bash
# Basic usage (defaults to 70/20/10)
python "Training and Validation/partition_dataset.py" --images data/sar --annotations data/annotations --output data/partitioned

# Custom split with seed for reproducibility
python "Training and Validation/partition_dataset.py" --images data/sar --annotations data/annotations --output data/partitioned --seed 42 --train 0.8 --val 0.1 --test 0.1
```

### Script Output
The script creates a YOLO-compatible directory structure:
- `output/train/images`, `output/train/labels`
- `output/val/images`,   `output/val/labels`
- `output/test/images`,  `output/test/labels`
- `output/dataset.yaml` (Configuration file for YOLO training)
