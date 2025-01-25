import git
from mirror_commits import mirror_commits_for_branch


def post_push_hook(repo_path, fake_repo_path, author_name):
    # Load original repo
    repo = git.Repo(repo_path)
    current_branch = repo.active_branch.name

    # Mirror commits for the current branch
    mirror_commits_for_branch(repo_path, fake_repo_path, current_branch, author_name)


if __name__ == "__main__":
    REPO_PATH = "/path/to/original/repo"
    FAKE_REPO_PATH = "/path/to/fake/repo"
    AUTHOR_NAME = "Your Name"

    post_push_hook(REPO_PATH, FAKE_REPO_PATH, AUTHOR_NAME)
