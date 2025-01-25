import git


def clone_repo(repo_url, local_path, token=None):
    if token:
        repo_url = repo_url.replace("https://", f"https://{token}@")
    return git.Repo.clone_from(repo_url, local_path)
