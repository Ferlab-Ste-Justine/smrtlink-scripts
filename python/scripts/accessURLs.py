import requests
import json
import subprocess
import os
import sys
from tqdm import tqdm

# Small script that uses the URL list provided "decodeurURL.json" to download all files for each sample
# It will create a folder for all samples. 
# You can use the md5sum file provided separately to check integrity of the files.
def main():
    if not os.path.exists('decodeurURL.json'):
        print("decodeurURL.json file not found")
        sys.exit(1)

    with open('decodeurURL.json') as json_file:
        url_dict = json.load(json_file)
    # Avoid downloading BAM files if "nobam" argument is provided (useful for testing, BAMs are very large)
    skip_bam = False
    if len(sys.argv) > 1 and sys.argv[1] == "nobam":
        print("Skipping BAM file downloads")
        skip_bam = True
    for decodeur_id, urls in url_dict.items():
        if not os.path.exists(decodeur_id):
            try:
                os.makedirs(decodeur_id, exist_ok=True)
            except OSError as e:
                print(f"Error creating directory '{decodeur_id}': {e}")
                continue

        for url_type, url in urls.items():
            local_filepath = f"{decodeur_id}/{url.split('/')[-1].split('?')[0]}"
            if url_type != "bam_url" or not skip_bam:
            # Check if file already exists to resume download
                if os.path.exists(local_filepath):
                    resume_byte_pos = os.path.getsize(local_filepath)
                    headers = {'Range': f'bytes={resume_byte_pos}-'}
                    mode = 'ab'  # append mode
                else:
                    headers = {}
                    mode = 'wb'
                    resume_byte_pos = 0
                try:
                    with requests.get(url, headers=headers, stream=True) as r:
                        if r.status_code == 416:
                            continue  # File already fully downloaded
                        r.raise_for_status()
                        print(f"Downloading {url_type} for {decodeur_id}")
                        total_size = int(r.headers.get("content-length", 0))
                        chunk_size = 8192
                        effective_total = resume_byte_pos + total_size if total_size else None
                        with tqdm(initial=resume_byte_pos, total=effective_total, unit="B", unit_scale=True) as progress_bar:
                            with open(local_filepath, mode) as f:
                                for chunk in r.iter_content(chunk_size): 
                                    progress_bar.update(len(chunk))
                                    f.write(chunk)

                        # Verify that the final file size matches the expected size (if known)
                        if total_size > 0:
                            expected_total_size = resume_byte_pos + total_size
                            actual_size = os.path.getsize(local_filepath)
                            if actual_size != expected_total_size:
                                print(f"Warning: Downloaded file size for {local_filepath} ({actual_size} bytes) does not match expected size ({expected_total_size} bytes). Skipping md5 generation.")
                                continue
                    with open(f"{local_filepath}.md5", "w") as md5_file:
                        subprocess.run(["md5sum", local_filepath], stdout=md5_file, check=True)
                except requests.RequestException as e:
                    print(f"Error checking {url_type}: {e}")
        print(f"Completed downloads for sample {decodeur_id}\n")
    print("All downloads completed.")

if __name__ == "__main__":
    main()