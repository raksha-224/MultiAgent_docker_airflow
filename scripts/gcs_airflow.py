# File: /app/scripts/gcs_airflow.py

import subprocess
import os
from github import Github
from datetime import date, timedelta
from tqdm import tqdm
from google.cloud import storage
import shutil  # Import shutil for removing directories

# Single GCS Bucket name
GCS_BUCKET = "data298a-data"
GITHUB_ACCESS = ""

# Function to handle GCS client
def get_gcs_client():
    """Initialize and return a Google Cloud Storage client."""
    try:
        client = storage.Client()
        return client
    except Exception as e:
        print(f"Error initializing GCS client: {e}")
        return None

def save_file_to_gcs(file_path, target_dir):
    """Upload a file to a specific GCS subfolder (target_dir) within a single GCS bucket."""
    client = get_gcs_client()
    if not client:
        return

    try:
        bucket = client.get_bucket(GCS_BUCKET)
        file_name = os.path.basename(file_path)
        target_blob_name = os.path.join(target_dir, file_name)  # Use subfolder structure

        # Create a blob (equivalent to a file in GCS)
        blob = bucket.blob(target_blob_name)
        blob.upload_from_filename(file_path)

        print(f"Uploaded {file_path} to gs://{GCS_BUCKET}/{target_blob_name}")
    except Exception as e:
        print(f"Error uploading file {file_path} to GCS: {e}")

# GitHub Authentication and Data Loading
def data_loading():
    """Main function to load data from GitHub repositories and upload to GCS."""
    print("Starting data_loading...", flush=True)
    
    try:
        auth = Github(GITHUB_ACCESS)
        rate_limit = auth.get_rate_limit()
        print(f"GIT API rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
    except Exception as e:
        print(f"ERROR: GitHub authentication failed: {e}", flush=True)
        return

    # Date range for repo search
    end_time = date.today()
    start_time = end_time - timedelta(days=10)
    languages = ["python", "javascript", "html", "css", "java"]
    language_query = " ".join([f"language:{lang}" for lang in languages])
    query = f"({language_query}) created:{start_time}..{end_time}"

    try:
        result = auth.search_repositories(query)
        repos_list = list(result)
        if not repos_list:
            print("WARNING: No repositories returned in search results", flush=True)
            return
    except Exception as e:
        print(f"Error searching repositories: {e}", flush=True)
        return

    # Process repositories
    for repo in repos_list[:20]:  # Limiting to 20 repos for now
        clone_url = repo.clone_url
        repo_name = repo.name
        repo_path = f"/tmp/{repo_name}"

        if os.path.exists(repo_path):
            print(f"Repository {repo_name} already cloned. Skipping.")
            continue

        try:
            subprocess.run(f"git clone {clone_url} {repo_path}", shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error cloning {repo_name}: {e}", flush=True)
            continue

        # Walk through repo files and upload to GCS
        for dirpath, _, filenames in tqdm(os.walk(repo_path), desc=f"Processing {repo_name}"):
            for f in filenames:
                full_path = os.path.join(dirpath, f)
                # Classify files based on extensions and upload to respective subfolders
                if f.endswith(".py"):
                    save_file_to_gcs(full_path, "python_files")
                elif f.endswith(".html"):
                    save_file_to_gcs(full_path, "html_files")
                elif f.endswith(".css"):
                    save_file_to_gcs(full_path, "css_files")
                elif f.endswith(".java"):
                    save_file_to_gcs(full_path, "java_files")
                else:
                    try:
                        os.remove(full_path)
                        print(f"Deleted unneeded file: {full_path}")
                    except Exception as e:
                        print(f"Error deleting {full_path}: {e}")

        # Clear the temporary repo folder
        try:
            shutil.rmtree(repo_path)
            print(f"Deleted temporary folder: {repo_path}")
        except Exception as e:
            print(f"Error deleting repo folder {repo_path}: {e}")

    print("Data loading completed.")

if __name__ == "__main__":
    print("Calling data_loading function", flush=True)
    data_loading()
