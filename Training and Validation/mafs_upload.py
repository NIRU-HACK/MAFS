import roboflow
import os
import json
import datetime

# 1. Initialize
# Images in the test subfolder are commented since they are a cumulative of test_inshore and test_offshore
rf = roboflow.Roboflow()
project = rf.workspace("mafs").project("mafs")

base_path = "Training and Validation/data/sar/raw/Official-SSDD-OPEN/Official-SSDD-OPEN/BBox_SSDD/coco_style"
upload_tasks = [
    {"imgs": f"{base_path}/images/train", "ann": f"{base_path}/annotations/train.json", "batch": "SSDD_Train"},
    #{"imgs": f"{base_path}/images/test", "ann": f"{base_path}/annotations/test.json", "batch": "SSDD_Test"},
    {"imgs": f"{base_path}/images/test_inshore", "ann": f"{base_path}/annotations/test_inshore.json", "batch": "SSDD_Inshore"},
    {"imgs": f"{base_path}/images/test_offshore", "ann": f"{base_path}/annotations/test_offshore.json", "batch": "SSDD_Offshore"}
]

# Logging lists
successes = []
failures = []

def log_report():
    with open("upload_report.txt", "w") as f:
        f.write(f"MAFS Upload Report - {datetime.datetime.now()}\n")
        f.write(f"Total Successes: {len(successes)}\n")
        f.write(f"Total Failures: {len(failures)}\n\n")
        f.write("--- FAILED IMAGES ---\n")
        for img, err in failures:
            f.write(f"{img} | Error: {err}\n")
            
    # Create a clean list for easy retrying
    with open("failed_images.txt", "w") as f:
        for img, _ in failures:
            f.write(f"{img}\n")

# 2. Execution
try:
    for task in upload_tasks:
        print(f"\n--- Starting {task['batch']} ---")
        if not os.path.exists(task['imgs']) or not os.path.exists(task['ann']):
            print(f"Skipping: Path not found for {task['batch']}")
            continue

        with open(task['ann'], 'r') as f:
            coco_data = json.load(f)

        for img_entry in coco_data['images']:
            file_name = img_entry['file_name']
            local_image_path = os.path.join(task['imgs'], file_name)

            if os.path.exists(local_image_path):
                try:
                    project.single_upload(
                        image_path=local_image_path,
                        annotation_path=task['ann'],
                        batch_name=task['batch'],
                        overwrite=True
                    )
                    successes.append(file_name)
                    print(f"SUCCESS: {file_name}")
                except Exception as e:
                    failures.append((file_name, str(e)))
                    print(f"FAILED: {file_name} | Error: {e}")
            else:
                failures.append((file_name, "File not found on disk"))
finally:
    log_report()
    print("\nUpload finished. Check 'upload_report.txt' and 'failed_images.txt' for details.")