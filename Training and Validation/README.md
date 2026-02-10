# Training and Validation

## SAR Ship Detection Benchmark Datasets

| Dataset Name | Images | Resolution / Satellite | Image Shape | Instances | Related Paper |
| --- | --- | --- | --- | --- | --- |
| **SSDD** | 1,160 | 1–15m (S1, RS2, TSX) |  | 2,358 | [IEEE Xplore](https://ieeexplore.ieee.org/document/8124934) |
| **OpenSARShip 1.0** | 11,346 | 2–22m (Sentinel-1) |  to  | 67,489 | [IEEE Xplore](https://ieeexplore.ieee.org/document/8067489) |
| **OpenSARShip 2.0** | 34,528 | 2–22m (Sentinel-1) |  to  | — | [IEEE Xplore](https://ieeexplore.ieee.org/document/8124929) |
| **SAR-Ship-Dataset** | 43,819 | 3–25m (S1, Gaofen-3) |  | 59,535 | [MDPI Paper](https://www.mdpi.com/2072-4292/11/7/765) |
| **HRSID** | 5,604 | 0.5–3m (S1B, TSX, TDX) |  | 16,951 | [IEEE Xplore](https://ieeexplore.ieee.org/document/9127939) |
| **LS-SSDD-v1.0** | 9,000 | Sentinel-1 |  | 6,015 | [MDPI Paper](https://www.mdpi.com/2072-4292/12/18/2997) |
| **DSSDD** | 1,236 | Sentinel-1 |  | 3,540 | [MDPI Paper](https://www.mdpi.com/1424-8220/21/24/8478) |
| **SRSDD-v1.0** | 666 | Gaofen-3 |  | 2,884 | [MDPI Paper](https://www.mdpi.com/2072-4292/13/24/5104) |
| **xView3-SAR** | 991 | 20m (Sentinel-1) |  | — | [arXiv Paper](https://arxiv.org/abs/2206.00897) |
| **AIR-SARShip-1.0** | 1,116 | 1–3m (Gaofen-3) |  | — | [Journal of Radars](https://radars.ac.cn/en/article/doi/10.12000/JR19097) |

---

### Dataset Details

* **Multi-Modal Support:** Datasets like **xView3-SAR** and **HRSID** are designed specifically for large-scale characterization and instance segmentation.
* **Satellite Sources:** Most datasets utilize **Sentinel-1** data, though several incorporate high-resolution **Gaofen-3** or **TerraSAR-X** imagery.


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
