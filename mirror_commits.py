import os
import git
from datetime import datetime, timezone
import subprocess


def mirror_commits_for_branch(repo_path, fake_repo_url, branch_name, author_name):
    # Path where the fake repo will be cloned locally (in the parent directory)
    parent_dir = os.path.abspath(os.path.join(repo_path, os.pardir))
    original_repo_name = os.path.basename(os.path.normpath(repo_path))
    fake_repo_local_path = os.path.join(parent_dir, f"{original_repo_name}-mirrored")
    default_branch = "main"  # Specify the default branch here

    # Clone the fake repo if it doesn’t exist
    if not os.path.exists(fake_repo_local_path):
        print(f"Cloning fake repository into {fake_repo_local_path}...")
        fake_repo = git.Repo.clone_from(fake_repo_url, fake_repo_local_path)
        print("Clone completed.")

        # Ensure the fake repo has an initial commit on the default branch
        if not fake_repo.heads:
            print(f"Creating the '{default_branch}' branch in the fake repository...")
            fake_repo.git.checkout("-b", default_branch)  # Create and switch to default branch
            fake_repo.index.commit("Initial commit")
            fake_repo.git.push("--set-upstream", "origin", default_branch)
    else:
        fake_repo = git.Repo(fake_repo_local_path)

    # Ensure we are on the default branch in the fake repo
    if fake_repo.active_branch.name != default_branch:
        print(f"Switching to the '{default_branch}' branch in the fake repository...")
        fake_repo.git.checkout(default_branch)

    # Check out the branch in the original repo
    repo = git.Repo(repo_path)
    repo.git.checkout(branch_name)
    commits = list(repo.iter_commits(branch_name))

    # Iterate through commits authored by the user
    for commit in commits:
        print(f"Processing commit: {commit.hexsha} - {commit.message.strip()}")
        if author_name in commit.author.name:
            if not is_commit_in_default_branch(repo, commit):
                print(f"Commit {commit.hexsha} is not in the default branch.")
            if not is_commit_in_fake_repo(fake_repo, commit):
                print(f"Commit {commit.hexsha} is not in the fake repository.")
                # Mirror the commit into the fake repo
                mirror_commit(fake_repo, commit, branch_name)

    # Push changes to the default branch in the remote fake repo
    print(f"Pushing changes to the '{default_branch}' branch...")
    fake_repo.git.push("origin", default_branch)


def mirror_commit(fake_repo, commit, branch_name):
    """Mirror a commit into the fake repository, preserving the original timestamp and linking to the original commit."""
    print(f"Mirroring commit: {commit.hexsha} - {commit.message.strip()}")

    # Format the original commit date in ISO 8601 format
    original_date = datetime.fromtimestamp(commit.committed_date, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Set environment variables for the commit date
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = original_date
    env["GIT_COMMITTER_DATE"] = original_date

    # Get the original repo's remote URL and construct the HTTPS link
    original_repo_url = commit.repo.remotes.origin.url

    # Parse the repository owner and name from the URL
    if original_repo_url.startswith("git@"):
        # Example: git@github.com-Cem802:Cem802/mirror-test.git
        _, repo_path = original_repo_url.split(":", 1)
    elif original_repo_url.startswith("https://"):
        # Example: https://github.com/Cem802/mirror-test.git
        repo_path = original_repo_url.split("https://")[-1]
    else:
        raise ValueError(f"Unsupported URL format: {original_repo_url}")

    # Remove `.git` suffix if present
    if repo_path.endswith(".git"):
        repo_path = repo_path[:-4]

    # Construct the HTTPS URL
    https_base = "https://www.github.com"
    original_commit_url = f"{https_base}/{repo_path}/commit/{commit.hexsha}"

    # Format the commit message
    commit_message = (
        f"{branch_name}: {commit.message.strip()}\n"
        f"Original Commit: {original_commit_url}\n"
        f"Original Hash: {commit.hexsha}"
    )

    # Log file for mirrored commits
    log_file_path = os.path.join(fake_repo.working_tree_dir, "commit_log.txt")

    # Ensure the log file exists and has at least one change
    with open(log_file_path, "a") as log_file:
        log_entry = (
            f"{datetime.now(timezone.utc).isoformat()} | Branch: {branch_name} | Commit: {commit.hexsha} | "
            f"Original Commit URL: {original_commit_url} | Message: {commit.message.strip()}\n"
        )
        log_file.write(log_entry)

    # Stage all changes (including the log file update)
    result_add = subprocess.run(
        ["git", "add", "-A"],
        cwd=fake_repo.working_tree_dir,
        capture_output=True,
        text=True,
    )
    if result_add.returncode != 0:
        print(f"Error staging changes: {result_add.stderr}")
        raise Exception(f"Failed to stage changes: {result_add.stderr}")

    # Check if there are staged changes
    result_diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=fake_repo.working_tree_dir,
    )
    if result_diff.returncode == 0:
        # No changes to commit
        print(f"No changes to commit for {commit.hexsha}. Skipping...")
        return

    # Commit the changes
    result_commit = subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=fake_repo.working_tree_dir,
        env=env,
        capture_output=True,
        text=True,
    )
    if result_commit.returncode != 0:
        print(f"Error committing to fake repo: {result_commit.stderr}")
        raise Exception(f"Commit failed: {result_commit.stderr}")

    print(f"Mirrored commit {commit.hexsha} to the fake repository.")


def is_commit_in_default_branch(repo, commit):
    # Check if the commit is in the default branch (e.g., main)
    default_branch = repo.active_branch
    return commit in repo.iter_commits(default_branch)


def is_commit_in_fake_repo(fake_repo, commit):
    # Check if the commit is already mirrored in the fake repo
    for fake_commit in fake_repo.iter_commits():
        if commit.hexsha in fake_commit.message:
            print(f"Commit {commit.hexsha} already exists in the fake repository.")
            return True
    return False
