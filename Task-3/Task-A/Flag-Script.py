import os
import requests

# Set headers to mimic a browser
headers = {"User-Agent": "Mozilla/5.0"}

# API URL for the "svg" folder of the repository on the main branch
api_url = "https://api.github.com/repos/hampusborgos/country-flags/contents/svg?ref=main"

response = requests.get(api_url, headers=headers)
if response.status_code != 200:
    raise Exception(f"Failed to fetch file list: {response.status_code}")

files = response.json()

# Sort files by name for a consistent order
files_sorted = sorted(files, key=lambda x: x['name'])

# Create an output directory for the flags
output_dir = "flags"
os.makedirs(output_dir, exist_ok=True)

# Download every flag (SVG format)
for file_info in files_sorted:
    download_url = file_info["download_url"]
    file_name = file_info["name"]  # e.g., "ad.svg"
    r = requests.get(download_url, headers=headers)
    if r.status_code == 200:
        with open(os.path.join(output_dir, file_name), "wb") as f:
            f.write(r.content)
        print(f"Downloaded {file_name}")
    else:
        print(f"Failed to download {file_name} (status code: {r.status_code})")
