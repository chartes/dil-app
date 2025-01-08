import pandas as pd
import os
import shutil
import numpy as np




# Define paths for source, destination, and log file
source_dir = "/Users/lucaterre/Documents/pro/Travail_courant/DEV/PROJETS/MPN_ELEC_Applications/DIL/on_github/dil-app/data/images"
destination_dir = "/Users/lucaterre/Documents/pro/Travail_courant/DEV/PROJETS/MPN_ELEC_Applications/DIL/on_github/dil-app/data/images_prepared"
log_file = "copy_images_log.txt"

# Create destination directory if it doesn't exist
os.makedirs(destination_dir, exist_ok=True)

# Load the CSV data
csv_file_path = "table_image_prepared.csv"  # Chemin vers votre fichier CSV
data = pd.read_csv(csv_file_path, sep='\t')

# Prepare lists to track success and failure
copied_files = []
not_found_files = []
errors = []

# Iterate through the rows of the DataFrame
for _, row in data.iterrows():
    source_file = row.get('filesys_path')
    new_file_name = row.get('new_filename')

    # Skip rows with invalid or missing filenames
    if not isinstance(source_file, str) or not isinstance(new_file_name, str):
        if source_file != np.nan:
            errors.append(f"Invalid data: filename={source_file}, new_filename={new_file_name}")
            continue
        else:
            continue

    source_path = os.path.join(source_dir, source_file)
    destination_path = os.path.join(destination_dir, new_file_name)

    try:
        # Check if the source file exists
        if os.path.exists(source_path):
            # Copy and rename the file
            shutil.copy(source_path, destination_path)
            copied_files.append(source_file)
            # remove the source file
            os.remove(source_path)
        else:
            not_found_files.append(source_file)
    except Exception as e:
        # Log any errors during the process
        errors.append(f"Error copying {source_file} to {new_file_name}: {str(e)}")

# Generate a log report
with open(log_file, "w") as log:
    log.write("Copy Images Log\n")
    log.write("================\n\n")
    log.write("Successfully copied files:\n")
    log.write("\n".join(copied_files) + "\n\n")
    log.write("Files not found:\n")
    log.write("\n".join(not_found_files) + "\n\n")
    log.write("Errors:\n")
    log.write("\n".join(errors) + "\n")

print(f"Processing complete. Log file saved to {log_file}.")