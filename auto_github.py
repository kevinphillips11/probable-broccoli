import os
import subprocess
import requests

def initialize_repo_if_not_exists(repo_owner, repo_name, access_token):
    repo_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 404:
        # Repository doesn't exist, so create it
        create_repo_url = "https://api.github.com/user/repos"
        payload = {
            "name": repo_name,
            "private": False
        }
        
        create_response = requests.post(create_repo_url, headers=headers, json=payload)
        
        if create_response.status_code != 201:
            raise Exception("Failed to create repository")
    elif response.status_code != 200:
        raise Exception("Failed to retrieve repository information")

def add_commit_push(access_token, repo_owner, repo_name, files_and_dirs, commit_message):
    # Initialize the repository if it doesn't exist
    initialize_repo_if_not_exists(repo_owner, repo_name, access_token)
    
    # Clone the repository if it doesn't exist locally
    if not os.path.exists(repo_name):
        subprocess.run(["git", "clone", f"https://github.com/{repo_owner}/{repo_name}.git"])
    
    # Change to the repository directory
    os.chdir(repo_name)
    
    # Add files and directories to staging
    subprocess.run(["git", "add"] + files_and_dirs)
    
    # Commit changes
    subprocess.run(["git", "commit", "-m", commit_message])
    
    # Pull any changes from the remote repository, allowing unrelated histories
    subprocess.run(["git", "pull", "origin", "master", "--allow-unrelated-histories"])
    
    # Push to GitHub
    subprocess.run(["git", "push", "origin", "master"])


if __name__ == "__main__":
    access_token = "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"
    repo_owner = "danielshemesh"
    repo_name = "ma-index"
    files_and_dirs = ["./data"]  # List of files and/or directories
    commit_message = "data"  # Your commit message
    
    add_commit_push(access_token, repo_owner, repo_name, files_and_dirs, commit_message)
