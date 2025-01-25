import os
import subprocess
import requests
import json
import git

def save_github_token(token):
    """Save the GitHub token in an environment variable for future use."""
    env_file = os.path.expanduser("~/.mirror_commits_env")
    with open(env_file, "w") as file:
        file.write(f"GITHUB_TOKEN={token}\n")
    print(f"GitHub token saved to {env_file}. Make sure it's secure.")
    # Set file permissions to owner-read/write only for security
    os.chmod(env_file, 0o600)

def load_github_token():
    """Load the GitHub token from the environment variable or saved file."""
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
    # Try loading from the saved file
    env_file = os.path.expanduser("~/.mirror_commits_env")
    if os.path.exists(env_file):
        with open(env_file, "r") as file:
            for line in file:
                if line.startswith("GITHUB_TOKEN="):
                    return line.strip().split("=", 1)[1]
    return None

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


def create_fake_repo(token, original_repo_path, use_ssh=False):
    """Create a fake repository on GitHub using the API."""
    # Get the original repository's name
    original_repo_name = os.path.basename(os.path.normpath(original_repo_path))
    print(f"Detected original repository name: {original_repo_name}")
    fake_repo_name = f"{original_repo_name}-mirrored"
    print(f"Creating or verifying fake repository '{fake_repo_name}'...")

    headers = {"Authorization": f"token {token}"}
    data = {
        "name": fake_repo_name,
        "private": True,
        "description": f"Fake repository for mirroring commits from {original_repo_name}.",
    }
    response = requests.post("https://api.github.com/user/repos", headers=headers, json=data)

    if response.status_code == 201:
        print(f"Repository '{fake_repo_name}' created successfully.")
    elif response.status_code == 422:
        print(f"Repository '{fake_repo_name}' already exists. Verifying URL...")
    else:
        print("Failed to create or verify the repository:", response.json())
        exit(1)

    if use_ssh:
        # Get the original remote URL
        repo = git.Repo(original_repo_path)
        origin_url = repo.remotes.origin.url

        # Extract SSH host and user
        if origin_url.startswith("git@"):
            ssh_host, repo_path = origin_url.split(":", 1)
            return f"{ssh_host}:{repo_path.replace(original_repo_name, fake_repo_name)}"
        else:
            raise ValueError("The original repository's remote is not an SSH URL.")
    else:
        # Return the HTTPS URL from the response
        return response.json().get("clone_url")


def install_git_hook(repo_path, venv_path, tool_repo_path):
    """Install the pre-push Git hook."""
    print("Installing Git hook...")

    # Paths for the hook
    hooks_dir = os.path.join(repo_path, ".git", "hooks")
    hook_path = os.path.join(hooks_dir, "pre-push")
    pre_push_script_source = os.path.abspath("pre_push.py")  # Path to the script in the tool repo
    pre_push_script_target = os.path.join(hooks_dir, "pre_push.py")  # Copy to hooks folder

    if not os.path.exists(hooks_dir):
        print(f"Error: '{hooks_dir}' not found. Ensure this is a valid Git repository.")
        exit(1)

    # Inject the tool_repo_path dynamically into the pre_push.py script
    with open(pre_push_script_source, "r") as src_file:
        script_content = src_file.read()
    script_content = script_content.replace("__TOOL_REPO_PATH__", tool_repo_path)

    with open(pre_push_script_target, "w") as target_file:
        target_file.write(script_content)

    # Write the Bash script for the hook
    with open(hook_path, "w") as file:
        file.write(f"""#!/bin/bash

# Activate the virtual environment
source {os.path.abspath(venv_path)}/bin/activate

# Run the pre_push.py script
python {pre_push_script_target}

# Deactivate the virtual environment
deactivate
""")

    # Ensure the hook script is executable
    subprocess.run(["chmod", "+x", hook_path], check=True)

    print(f"Git hook installed successfully at {hook_path}.")


if __name__ == "__main__":
    print("Setting up Mirror Commits...")

    # Step 1: Create virtual environment and install dependencies
    create_virtual_environment()

    # Step 2: Get GitHub token
    GITHUB_TOKEN = load_github_token()
    if not GITHUB_TOKEN:
        GITHUB_TOKEN = input("Enter your GitHub Personal Access Token (with 'repo' scope): ").strip()
        save_github_token(GITHUB_TOKEN)

    # Step 3: Get original repo name and automatically generate the fake repo name
    ORIGINAL_REPO_PATH = input("Enter the path to your original repository: ").strip()

    # Step 4: Create the fake repository
    use_ssh = input("Do you want to use SSH for the fake repository? (y/n): ").strip().lower() == "y"
    FAKE_REPO_URL = create_fake_repo(GITHUB_TOKEN, ORIGINAL_REPO_PATH, use_ssh)

    # Step 5: Install the Git hoaok
    VENV_PATH = os.path.abspath("venv")
    TOOL_REPO_PATH = os.path.abspath(os.path.dirname(__file__))  # Dynamically determine the tool's location
    install_git_hook(ORIGINAL_REPO_PATH, VENV_PATH, TOOL_REPO_PATH)

    # Step 6: Save repository-specific configuration
    AUTHOR_NAME = input("Enter your name (as used in your Git commits): ").strip()
    save_env_vars(ORIGINAL_REPO_PATH, FAKE_REPO_URL, AUTHOR_NAME)

    # Final Output
    print("\nSetup complete!")
    if FAKE_REPO_URL:
        print(f"Fake repository URL: {FAKE_REPO_URL}")
    print("Don't forget to push your local branches to the remote repositories.")

