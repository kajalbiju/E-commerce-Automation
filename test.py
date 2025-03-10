import os
import re
import glob

# Define the base path where directories are located
base_path = 'InstaLoginWeb'  # Adjust to the actual parent directory path if needed

# Use a regular expression to find the directory starting with "instagram_content"
matching_dirs = [d for d in glob.glob(os.path.join(base_path, "instagram_content*")) if re.match(r"^instagram_content_\d+_\d+$", os.path.basename(d))]

if matching_dirs:
    base_dir = matching_dirs[0]  # Use the first match, or modify as needed
else:
    raise FileNotFoundError("No directory matching the pattern 'instagram_content_*_*' was found.")

print("Base directory selected:", base_dir)
