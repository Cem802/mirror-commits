import git


def mirror_commits_for_branch(repo_path, fake_repo_path, branch_name, author_name):
    repo = git.Repo(repo_path)
    fake_repo = git.Repo(fake_repo_path)

    # Check out the branch in the original repo
    repo.git.checkout(branch_name)
    commits = list(repo.iter_commits(branch_name))

    # Iterate through commits authored by the user
    for commit in commits:
        if author_name in commit.author.name:
            if not is_commit_in_default_branch(repo, commit) and not is_commit_in_fake_repo(fake_repo, commit):
                # Mirror the commit into the fake repo
                mirror_commit(fake_repo, commit)


def mirror_commit(fake_repo, commit):
    # Create a new commit in the fake repo
    fake_repo.index.commit(
        f"Mirror Commit: {commit.message}\nOriginal Hash: {commit.hexsha}"
    )


def is_commit_in_default_branch(repo, commit):
    # Check if the commit is in the default branch (e.g., main)
    default_branch = repo.active_branch
    return commit in repo.iter_commits(default_branch)


def is_commit_in_fake_repo(fake_repo, commit):
    # Check if the commit is already mirrored in the fake repo
    for fake_commit in fake_repo.iter_commits():
        if commit.hexsha in fake_commit.message:
            return True
    return False
