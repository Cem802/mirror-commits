# Mirror Commits

Mirror Commits is a Python tool for developers who work with squash merge workflows. It ensures that all your commits show up in your GitHub contribution graph by mirroring them into a "fake" repository.

## Features
- Mirror commits authored by you from a branch to a fake repository.
- Analyze all branches and sync commits.
- Automatically remove mirrored commits when they are merged into the default branch.
- Designed for use with private repositories.

## Setup

### Prerequisites
- Python 3.7+
- GitPython library

Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration
1. Clone the original repository:
```bash
git clone https://github.com/yourusername/original-repo.git
```

2. Create a private repository to host mirrored commits:
```bash
git clone https://github.com/yourusername/fake-repo.git
```

3. Set the paths in the scripts:
- REPO_PATH: Path to the original repository.
- FAKE_REPO_PATH: Path to the fake repository.

4.Add a post-push Git hook:
```bash
ln -s /path/to/post_push.py .git/hooks/post-push
```

## Usage
### Post-Push Hook
Automatically mirror commits after pushing a branch:

```bash
git push origin feature-branch
```

### Analyze All Branches
Manually analyze all branches and mirror commits:

```bash
python analyze_all_branches.py
```

## Security
- Use SSH or Personal Access Tokens for private repository access.
- Tokens should be stored as environment variables.

## Contributing
Feel free to submit issues or pull requests to improve this tool!

## License
This project is open-source and licensed under the MIT License.