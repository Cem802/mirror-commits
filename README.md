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

### Automated Setup
To simplify the setup process, use the provided automation scripts.

#### macOS/Linux:
Run the following Bash script:
```bash
./setup.sh
```

#### Windows:
Run the following Batch script:
```cmd
setup.bat
```

These scripts will:

1. Create and activate a virtual environment.
2. Install the necessary dependencies.
3. Run the setup.py script.

### Manual Virtual Environment Setup (Optional)
To prevent conflicts with your system Python environment, create and activate a virtual environment manually:

1. Create a virtual environment:

- macOS/Linux:
```bash
python3 -m venv venv
```

-Windows:
```cmd
python -m venv venv
```

2. Activate the virtual environment:

- On macOS/Linux:
```bash
source venv/bin/activate
```

- On Windows:
```cmd
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. To deactivate the virtual environment after usage:
```bash
deactivate
```

## Usage
### Pre-Push Hook
Automatically mirror commits before pushing a branch:

```bash
git push origin feature-branch
```

## Security
- Use SSH or Personal Access Tokens for private repository access.

## Contributing
Feel free to submit issues or pull requests to improve this tool!

## License
This project is open-source and licensed under the MIT License.