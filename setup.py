import os
import subprocess
import requests
import json


def save_env_vars(repo_path, fake_repo_url, author_name):
    """Save repository-specific configuration locally and globally."""
    config = {
        "repo_path": repo_path,
        "fake_repo_url": fake_repo_url,
        "author_name": author_name,
    }

    # Save local configuration inside the .git folder
    local_config_path = os.path.join(repo_path, ".git", "mirror_commits_config.json")
    with open(local_config_path, "w") as file:
        json.dump(config, file, indent=4)
    print(f"Configuration saved to {local_config_path}.")

    # Save global configuration for managing multiple repositories
    global_config_dir = os.path.expanduser("~/.mirror_commits_repos")
    os.makedirs(global_config_dir, exist_ok=True)
    global_config_path = os.path.join(global_config_dir, f"{os.path.basename(repo_path)}.json")
    with open(global_config_path, "w") as file:
        json.dump(config, file, indent=4)
    print(f"Global configuration saved to {global_config_path}.")


def create_virtual_environment():
    """Create and activate a virtual environment, and install dependencies."""
    print("Creating virtual environment...")
    subprocess.run(["python3", "-m", "venv", "venv"], check=True)
    print("Installing dependencies...")
    subprocess.run(["venv/bin/pip", "install", "-r", "requirements.txt"], check=True)
    print("Virtual environment setup complete.")


def create_fake_repo(token, original_repo_name, use_ssh=False):
    """Create a fake repository on GitHub using the API."""
    fake_repo_name = f"{original_repo_name}-mirrored"
    print(f"Creating fake repository '{fake_repo_name}'...")
    headers = {"Authorization": f"token {token}"}
    data = {
        "name": fake_repo_name,
        "private": True,
        "description": f"Fake repository for mirroring commits from {original_repo_name}.",
    }
    response = requests.post("https://api.github.com/user/repos", headers=headers, json=data)
    if response.status_code == 201:
        print(f"Repository '{fake_repo_name}' created successfully.")
        return response.json()["ssh_url"] if use_ssh else response.json()["clone_url"]
    elif response.status_code == 422:
        print(f"Repository '{fake_repo_name}' already exists.")
        return None
    else:
        print("Failed to create the repository:", response.json())
        exit(1)


def install_git_hook(repo_path):
    """Install the post-push Git hook."""
    print("Installing Git hook...")
    hooks_dir = os.path.join(repo_path, ".git", "hooks")
    hook_path = os.path.join(hooks_dir, "post-push")
    if not os.path.exists(hooks_dir):
        print(f"Error: '{hooks_dir}' not found. Ensure this is a valid Git repository.")
        exit(1)

    # Link the post-push hook script
    subprocess.run(["ln", "-s", os.path.abspath("post_push.py"), hook_path], check=True)
    subprocess.run(["chmod", "+x", hook_path], check=True)
    print("Git hook installed successfully.")


if __name__ == "__main__":
    print("Setting up Mirror Commits...")

    # Step 1: Create virtual environment and install dependencies
    create_virtual_environment()

    # Step 2: Get GitHub token
    GITHUB_TOKEN = input("Enter your GitHub Personal Access Token (with 'repo' scope): ").strip()

    # Step 3: Get original repo name and automatically generate the fake repo name
    ORIGINAL_REPO_PATH = input("Enter the path to your original repository: ").strip()
    original_repo_name = os.path.basename(os.path.normpath(ORIGINAL_REPO_PATH))
    print(f"Detected original repository name: {original_repo_name}")

    # Step 4: Create the fake repository
    use_ssh = input("Do you want to use SSH for the fake repository? (y/n): ").strip().lower() == "y"
    FAKE_REPO_URL = create_fake_repo(GITHUB_TOKEN, original_repo_name, use_ssh)

    # Step 5: Install the Git hook
    install_git_hook(ORIGINAL_REPO_PATH)

    # Step 6: Save repository-specific configuration
    AUTHOR_NAME = input("Enter your name (as used in your Git commits): ").strip()
    save_env_vars(ORIGINAL_REPO_PATH, FAKE_REPO_URL, AUTHOR_NAME)

    # Final Output
    print("\nSetup complete!")
    if FAKE_REPO_URL:
        print(f"Fake repository URL: {FAKE_REPO_URL}")
    print("Don't forget to push your local branches to the remote repositories.")
