# Training and Validation
This README provides a comprehensive guide for the **Maritime Anomaly Fusion System (MAFS)** dataset pipeline. It covers the ingestion of multiple SAR (Synthetic Aperture Radar) sources, error recovery, and the standardization process within Roboflow for YOLOv11m training.

---

# MAFS Dataset Integration & Merging Guide

## 🚀 Prerequisites

1. **Roboflow Account:** [Sign up here](https://app.roboflow.com/) and create a project named `mafs`.
2. **Resource Video:** [Uploading Images to Roboflow via CLI](https://docs.roboflow.com/developer/command-line-interface/upload-a-dataset).

## 🛠️ Environment Setup

Open your terminal (PowerShell recommended) and run the following to prepare your environment:

```powershell
# Set execution policy to allow scripts (Windows)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Install the Roboflow SDK
pip install roboflow

# Authenticate with your account
roboflow login

```

## 📥 Data Ingestion

### 1. Importing the YOLO SAR Dataset

For standard YOLO-formatted datasets, use the Roboflow CLI for high-speed upload:

```powershell
roboflow import -w mafs -p mafs "./Training and Validation/data/sar/raw/ship_dataset_v0"

```

### 2. Importing the SSDD Dataset (COCO Format)

Because SSDD uses a complex COCO structure, use the custom manual upload script to ensure 1:1 annotation matching:

```powershell
python "Training and Validation/mafs_upload.py"

```

### 3. Error Recovery (Failed Images)

If the upload log shows failures (e.g., "Unable to match annotation"), ensure those filenames are listed in `failed_images.txt` and run the retry script:

```powershell
python "Training and Validation/mafs_reupload_failed.py"

```

## 🔗 Merging Datasets in Roboflow UI

Follow these steps in the [Roboflow Dashboard](https://app.roboflow.com/) to consolidate your data.

### Step 1: Align Your Classes

SSDD and YOLO datasets often use different labels for the same object.

1. Select the **MAFS** project from your workspace.
2. Click on **Classes** in the left sidebar.
3. If you see multiple names like `0`, `vessel`, or `ship`, click **Modify Classes**.
4. In the **Override** column, type **"ship"** for every entry to merge them into a single class.
5. Click **Apply Changes**.

### Step 2: Generate a Unified Version

1. Go to the **Versions** tab and click **Generate New Version**.
2. **Source Data:** Ensure all batches (SSDD_Train, Inshore, Offshore, YOLO_Batch, etc.) are selected.
3. **Train/Test Split:** For the **MAFS** local partitioning workflow, move the slider to **100% Train**. This allows the local `partition_dataset.py` script to handle the 70/20/10 split with a fixed seed.
4. **Preprocessing (Crucial):**
* **Resize:** Set to **640x640 (Stretch)** to standardize all SAR sources.
* **Auto-Orient:** Enabled (strips EXIF rotation data).


5. **Augmentation:** Leave blank (0%). Augmentations should be handled during training or after partitioning to avoid data leakage.
6. Click **Create**.

## 📦 Export & Training

1. Once the version is generated, click **Export Dataset**.
2. Format: Choose **YOLOv11** (or the specific YOLO version you are using).
3. Download the ZIP or use the `curl` link to pull the data to your training environment.

## 🛰️ Future Data Expansion (Sentinel-1)

When adding new Copernicus Sentinel-1 data (VV/VH polarization):

1. Extract the dual-polarization bands.
2. Label using the **AIS API** logic.
3. Merge the new images/labels into your raw folders.
4. Run `partition_dataset.py --seed 42` to re-distribute the expanded dataset into Train/Val/Test folders.

---

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
