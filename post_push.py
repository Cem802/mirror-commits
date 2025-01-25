import os
import json
import git
from mirror_commits import mirror_commits_for_branch


def load_config(repo_path):
    """Load the repository-specific configuration."""
    config_path = os.path.join(repo_path, ".git", "mirror_commits_config.json")
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found at {config_path}.")
        exit(1)
    with open(config_path, "r") as file:
        return json.load(file)


def post_push_hook(config):
    """Run the post-push hook with the loaded configuration."""
    repo = git.Repo(config["repo_path"])
    current_branch = repo.active_branch.name
    mirror_commits_for_branch(config["repo_path"], config["fake_repo_url"], current_branch, config["author_name"])


if __name__ == "__main__":
    # Get repository path dynamically from the current directory
    REPO_PATH = os.getcwd()
    config = load_config(REPO_PATH)
    post_push_hook(config)
