from mirror_commits import mirror_commits_for_branch, cleanup_fake_repo
import git


def analyze_all_branches(repo_path, fake_repo_path, author_name):
    repo = git.Repo(repo_path)
    fake_repo = git.Repo(fake_repo_path)

    # Get all branches
    branches = repo.branches

    for branch in branches:
        mirror_commits_for_branch(repo_path, fake_repo_path, branch.name, author_name)

    # Cleanup: Remove mirrored commits merged into the default branch
    cleanup_fake_repo(repo, fake_repo)


def cleanup_fake_repo(repo, fake_repo):
    default_branch = repo.active_branch
    default_commits = {commit.hexsha for commit in repo.iter_commits(default_branch)}

    for fake_commit in list(fake_repo.iter_commits()):
        # Extract the original hash from the mirrored commit message
        original_hash = extract_original_hash(fake_commit.message)
        if original_hash and original_hash in default_commits:
            # Remove the mirrored commit from the fake repo
            fake_repo.git.revert(fake_commit.hexsha, no_edit=True)


def extract_original_hash(commit_message):
    # Extract the original commit hash from the mirrored commit message
    for line in commit_message.splitlines():
        if line.startswith("Original Hash:"):
            return line.split(":")[1].strip()
    return None


if __name__ == "__main__":
    REPO_PATH = "/path/to/original/repo"
    FAKE_REPO_PATH = "/path/to/fake/repo"
    AUTHOR_NAME = "Your Name"

    analyze_all_branches(REPO_PATH, FAKE_REPO_PATH, AUTHOR_NAME)
