import os
import subprocess
import glob

# --- CONFIGURATION ---
# Update this if your SNAP is installed in a different location
GPT_PATH = r"C:\Program Files\esa-snap\bin\gpt.exe"

# This finds the directory where THIS script is saved
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GRAPH_XML = os.path.join(BASE_DIR, "mafs_preproc.xml")
INPUT_DIR = os.path.join(BASE_DIR, "corpenicus_raw")
OUTPUT_DIR = os.path.join(BASE_DIR, "corpenicus_output")

def process_sentinel_images():
    # 1. Check if directories exist
    if not os.path.exists(INPUT_DIR):
        print(f"ERROR: Could not find input folder at: {INPUT_DIR}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 2. Search for ZIP files (handles .SAFE.zip and .zip)
    # We use recursive=False to stay in the main folder
    raw_files = glob.glob(os.path.join(INPUT_DIR, "*.zip"))

    print(f"Scanning folder: {INPUT_DIR}")
    if not raw_files:
        print("No .zip files found. Contents of folder:")
        print(os.listdir(INPUT_DIR))
        return

    print(f"Found {len(raw_files)} files to process.")

    for input_file in raw_files:
        base_name = os.path.basename(input_file)
        # Keeps the original long name but changes extension to .tif
        output_name = base_name.replace(".zip", ".tif")
        output_file = os.path.join(OUTPUT_DIR, output_name)

        print(f"\n--- Processing: {base_name} ---")

        command = [
            GPT_PATH,
            GRAPH_XML,
            f"-Pinput={input_file}",
            f"-Poutput={output_file}"
        ]

        try:
            # Run the SNAP engine
            subprocess.run(command, check=True)
            print(f"SUCCESS: Created {output_name}")
        except subprocess.CalledProcessError as e:
            print(f"FAILED: Error in SNAP processing for {base_name}")
        except Exception as e:
            print(f"CRITICAL ERROR: {str(e)}")

if __name__ == "__main__":
    process_sentinel_images()