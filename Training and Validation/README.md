# Training and Validation

## Partition datasets (70/20/10)

**What it means:** Split your labeled dataset into three non-overlapping sets:

| Split   | Fraction | Purpose |
|--------|----------|--------|
| **Train** | 70% | Fit the model (weights and biases). |
| **Val**   | 20% | Tune hyperparameters, early stopping, and model selection. Not used for training. |
| **Test**  | 10% | Final evaluation only. Use once at the end to report metrics; never use for training or tuning. |

**Why:** Using separate val and test sets avoids overfitting to your evaluation data and gives trustworthy performance estimates.

**How to complete:** Run the partition script (see below), then point your training config at the new `train`/`val`/`test` folders (e.g. in a YOLO dataset YAML).
