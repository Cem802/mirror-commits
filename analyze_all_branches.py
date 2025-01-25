import os
import json
import git
from mirror_commits import mirror_commits_for_branch, cleanup_fake_repo


def load_all_configs(config_dir):
    """Load all repository configurations from a directory."""
    configs = []
    for file in os.listdir(config_dir):
        if file.endswith(".json"):
            with open(os.path.join(config_dir, file), "r") as f:
                configs.append(json.load(f))
    return configs


def analyze_all_branches(repo_path, fake_repo_path, author_name):
    repo = git.Repo(repo_path)
    fake_repo = git.Repo(fake_repo_path)

    # Get all branches
    branches = repo.branches
    for branch in branches:
        mirror_commits_for_branch(repo_path, fake_repo_path, branch.name, author_name)

    # Cleanup: Remove mirrored commits merged into the default branch
    cleanup_fake_repo(repo, fake_repo)


if __name__ == "__main__":
    # Load all configurations
    CONFIG_DIR = os.path.expanduser("~/.mirror_commits_repos")
    if not os.path.exists(CONFIG_DIR):
        print(f"Error: No configuration directory found at {CONFIG_DIR}.")
        exit(1)

    configs = load_all_configs(CONFIG_DIR)
    for config in configs:
        print(f"Analyzing repository: {config['repo_path']}")
        analyze_all_branches(config["repo_path"], config["fake_repo_url"], config["author_name"])
