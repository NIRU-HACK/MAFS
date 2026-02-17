## Sentinel-1 VV and VH Extraction Chain

### **Step-by-Step Explanation**

1. **Apply-Orbit-File**
* **What it does:** Updates the satellite’s position and velocity data using "Precise Orbit" files.
* **Why for MAFS:** Standard metadata can be off by several meters. This ensures your ship coordinates are accurate to within centimeters, allowing you to cross-reference detections with AIS (Automatic Identification System) data later.


2. **ThermalNoiseRemoval**
* **What it does:** Subtracts the background "noise floor" (the grainy haze) from the image.
* **Why for MAFS:** Sentinel-1 **VH** bands are very dark over the ocean. Thermal noise can create artifacts that look like ships or clouds. This "cleans" the dark ocean background.


3. **Calibration ()**
* **What it does:** Converts raw pixels (unitless) into **Sigma Naught**, a physical measurement of radar backscatter.
* **Why for MAFS:** Without this, a ship's brightness depends on the sensor's distance. With this, the ship's brightness is constant regardless of when or where the image was taken.


4. **Terrain-Correction (Range-Doppler)**
* **What it does:** Geocodes the image into a map projection (**WGS84**) and corrects for side-looking distortions.
* **Why for MAFS:** Radar data is naturally "tilted." This flattens the image so that a pixel's location matches its real-world Latitude/Longitude.


5. **LinearToFromdB**
* **What it does:** Converts the linear power values into a logarithmic **Decibel (dB)** scale.
* **Why for MAFS:** Ships are thousands of times brighter than water. In linear scale, the water looks black and the ship is a tiny white dot. In dB, the histogram is "stretched," making the ship's shape and its wake visible to the AI.


6. **BandMaths (8-bit Scaling)**
* **What it does:** Normalizes the dB values (which are usually -35 to 0) into the **0 to 255** integer range.
* **Why for MAFS:** Computer vision models like YOLO and platforms like Roboflow cannot read negative decimal numbers. This step makes the data "Roboflow-ready" while keeping the "brightness" of ships consistent across the whole planet.


7. **Write (GeoTIFF)**
* **What it does:** Saves the final processed radar bands into a single file containing both the image pixels and the geographic metadata (Lat/Long).

* **Why for MAFS:** Compatibility: GeoTIFF is the "universal language" of satellite data. It can be opened in SNAP, QGIS, ArcGIS, and Python libraries like Rasterio or OpenCV.

Generalization Testing: Because the file stores the exact location of every pixel, we can prove your AI works in different global regions by overlaying detections on real-world maps.

Important Note: Standard GeoTIFFs are limited to 4 GB. Because we used Band Maths to convert the data to 8-bit (uint8), files will be significantly smaller (roughly 1/4 the size of the original 32-bit data), allowing them to fit comfortably within this 4 GB limit.



---

### How to Use the Script
1. **Raw Data:** Place your downloaded `.zip` Sentinel-1 files into `Preprocessing/corpenicus_raw/`.
2. **Run:** Open your terminal in the `Preprocessing` folder and run:

```bash
# run script
python ./Preprocessing/corpenicus_prepoc.py

```

### What is inside the script?

The script acts as a **"Wrapper"** for the SNAP engine. It doesn't do the heavy math itself; instead, it manages the manual labor:

* **Automation Loop:** It scans `corpenicus_raw` and builds a list of every ZIP file.
* **Path Management:** It automatically creates the `corpenicus_output` folder if it’s missing and generates unique filenames for every output (e.g., `S1_Image_processed.tif`).
* **Subprocess Execution:** It sends a command to your computer's Operating System to start the **SNAP GPT (Graph Processing Tool)** in the background.
* **Error Logging:** If one image is corrupted or fails, the script captures the error message from SNAP, prints it to your screen, and immediately moves to the next file so your processing doesn't stop.

---

### Final Directory Structure

```text
Preprocessing/
│
├── corpenicus_prepoc.py    <-- Run this
├── mafs_preproc.xml        <-- The "Recipe"
│
├── corpenicus_raw/         <-- Put .zip files here
│   └── S1A_IW_GRDH...zip
│
└── corpenicus_output/      <-- GeoTIFFs appear here
    └── S1A_IW_GRDH..._processed.tif

```