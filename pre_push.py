import os
import json
import git
import logging
import sys

# Placeholder for the path to the mirror-commits tool repo (injected dynamically by setup)
tool_repo_path = "__TOOL_REPO_PATH__"
sys.path.insert(0, tool_repo_path)

# Import the tool module
from mirror_commits import mirror_commits_for_branch


# Set up logging
logging.basicConfig(
    filename="pre_push.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def load_config(repo_path):
    """Load the repository-specific configuration."""
    config_path = os.path.join(repo_path, ".git", "mirror_commits_config.json")
    if not os.path.exists(config_path):
        logging.error(f"Configuration file not found at {config_path}.")
        exit(1)
    with open(config_path, "r") as file:
        return json.load(file)


def pre_push_hook(config):
    """Run the pre-push hook with the loaded configuration."""
    logging.info(f"Starting pre-push hook for repository: {config['repo_path']}")

    try:
        repo = git.Repo(config["repo_path"])
        current_branch = repo.active_branch.name
        logging.info(f"Current branch: {current_branch}")
        
        # Attempt to mirror commits
        mirror_commits_for_branch(config["repo_path"], config["fake_repo_url"], current_branch, config["author_name"])
        logging.info(f"Successfully mirrored commits for branch: {current_branch}")
    
    except Exception as e:
        logging.error(f"Error during pre-push hook: {e}", exc_info=True)
        logging.error("Ensure that the fake repository has been cloned or is accessible.")



if __name__ == "__main__":
    # Get repository path dynamically from the current directory
    print("hook triggered")
    REPO_PATH = os.getcwd()
    config = load_config(REPO_PATH)
    pre_push_hook(config)
