import roboflow
import os

# 1. Initialize Roboflow
rf = roboflow.Roboflow()
project = rf.workspace("mafs").project("mafs")

# 2. Open and read the failed images list
txt_file = "failed_images.txt"

if os.path.exists(txt_file):
    with open(txt_file, "r") as f:
        # Read lines, strip whitespace, and ignore empty lines
        failed_list = [line.strip() for line in f if line.strip()]
    print(f"Loaded {len(failed_list)} images for retry.")
else:
    print(f"ERROR: {txt_file} not found in the current directory.")
    exit()

# 3. Define the SSDD search paths
base = "Training and Validation/data/sar/raw/Official-SSDD-OPEN/Official-SSDD-OPEN/BBox_SSDD/coco_style"
search_paths = [
    {"imgs": f"{base}/images/train", "ann": f"{base}/annotations/train.json", "batch": "Retry_Train"},
    {"imgs": f"{base}/images/test_inshore", "ann": f"{base}/annotations/test_inshore.json", "batch": "Retry_Inshore"},
    {"imgs": f"{base}/images/test_offshore", "ann": f"{base}/annotations/test_offshore.json", "batch": "Retry_Offshore"}
]

# 4. Execution Loop
print("--- Starting Targeted Re-upload ---")
for filename in failed_list:
    found = False
    
    # Search each potential SSDD folder for the file
    for area in search_paths:
        img_path = os.path.join(area["imgs"], filename)
        
        if os.path.exists(img_path):
            try:
                # Use single_upload for the best chance of matching
                project.single_upload(
                    image_path=img_path,
                    annotation_path=area["ann"],
                    batch_name=area["batch"],
                    overwrite=True
                )
                print(f"SUCCESS: Retried {filename} in {area['batch']}")
                found = True
                break # Move to next image in failed_list
            except Exception as e:
                print(f"STILL FAILING: {filename} | Error: {e}")
                found = True # File exists, but API rejected it
                break
    
    if not found:
        print(f"NOT FOUND: Could not find {filename} in any SSDD images folder.")

print("\nRetry process finished. Check the Roboflow 'Annotate' tab for the new Retry batches.")