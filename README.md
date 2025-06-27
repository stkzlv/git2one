# git2one

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![GitHub issues](https://img.shields.io/github/issues/stkzlv/git2one)](https://github.com/stkzlv/git2one/issues)
[![GitHub stars](https://img.shields.io/github/stars/stkzlv/git2one)](https://github.com/stkzlv/git2one/stargazers)

`git2one` is a Python script that concatenates all text files in a Git repository into a single output file, making it easy to share or analyze the codebase as a single document. It respects `.gitignore` patterns, supports customizable file extensions, and allows including or excluding specific files or directories. This tool is particularly useful for preparing codebases for AI model input, documentation, or analysis.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Options](#command-line-options)
  - [Examples](#examples)
- [Configuration](#configuration)
- [Output Formats](#output-formats)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Functionality
- **Smart File Concatenation**: Combines text files into a single output with clear file separators
- **Gitignore Respect**: Automatically excludes files and directories specified in `.gitignore`
- **Multiple Output Formats**: Supports text, JSON, XML, and Markdown formats
- **Flexible Filtering**: Include/exclude files using glob patterns
- **Comment Stripping**: Optional removal of Python comments and docstrings

### AI/LLM Integration
- **Token Estimation**: Estimates token count for AI model compatibility (GPT, Claude, Gemini)
- **Optimized for AI**: Perfect for preparing codebases for AI analysis and code review
- **Multiple Formats**: JSON and XML formats for programmatic processing

### Developer-Friendly
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Configurable**: Customizable file extensions and exclusion patterns
- **Safe Processing**: Automatically skips binary files and handles encoding errors

## Use Cases

- **🤖 AI Code Analysis**: Prepare entire codebases for AI models (ChatGPT, Claude, etc.)
- **📚 Documentation**: Generate comprehensive code documentation
- **🔍 Code Review**: Create single-file snapshots for easier review
- **📊 Analysis**: Feed code into analysis tools that expect single files
- **📤 Sharing**: Share entire projects as single, readable documents
- **🏗️ Architecture Review**: Get a bird's-eye view of project structure

## Quick Start

```bash
# Clone the repository
git clone https://github.com/stkzlv/git2one.git
cd git2one

# Install dependencies
pip install -r requirements.txt

# Run on any Git repository
python git2one.py /path/to/your/repository
```

## Requirements

- Python 3.7 or higher
- Git repository (the tool works with any Git repository)

## Installation

### Method 1: Clone from GitHub (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/stkzlv/git2one.git
   cd git2one
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Method 2: Manual Installation

1. Download the script files
2. Install dependencies manually:
   ```bash
   pip install gitignore-parser pyyaml
   ```

3. Ensure `config.yaml` is in the same directory as `git2one.py` (see [Configuration](#configuration)).

## Usage
Run the script with the path to the target Git repository:

```bash
python git2one.py /path/to/repository
```

This concatenates all text files into `repo_combined.txt` (default output file).

### Command-Line Options
- `--output <file>`: Specify output file (default: `repo_combined.txt`).
- `--config <file>`: Path to config file (default: `config.yaml`).
- `--include <pattern>`: Include only files matching these patterns (e.g., `*.py`, `src/*`).
- `--exclude <pattern>`: Exclude files matching these patterns (e.g., `poetry.lock`, `tests/`).
- `--ignore-gitignore`: Ignore `.gitignore` file.
- `--strip-comments`: Strip Python-style comments (`#`) and docstrings (`"""..."""`).
- `--format <format>`: Output format (`text`, `json`, `xml`, `markdown`). Auto-detected from file extension if not specified.

### Examples
1. Concatenate all text files in a repository:
   ```bash
   python git2one.py ~/github.com/ProjectA/
   ```
   Output: `repo_combined.txt` with files like `README.md`, `src/*.py`, `config/*.yaml`.

2. Include only Python and Markdown files:
   ```bash
   python git2one.py ~/github.com/ProjectA/ --include "*.py" "*.md"
   ```

3. Exclude large files and strip comments:
   ```bash
   python git2one.py ~/github.com/ProjectA/ --exclude "poetry.lock" --strip-comments
   ```

4. Use a custom output file and bypass `.gitignore`:
   ```bash
   python git2one.py ~/github.com/ProjectA/ --output combined_code.txt --ignore-gitignore
   ```

5. Process specific directories:
   ```bash
   python git2one.py ~/github.com/ProjectA/ --include "src/*" "config/*"
   ```

6. Generate JSON output for programmatic processing:
   ```bash
   python git2one.py ~/github.com/ProjectA/ --output combined.json --format json
   ```

7. Create a Markdown report with syntax highlighting:
   ```bash
   python git2one.py ~/github.com/ProjectA/ --output report.md --format markdown
   ```

8. Export as XML for structured data processing:
   ```bash
   python git2one.py ~/github.com/ProjectA/ --output data.xml --format xml
   ```

## Configuration
The `config.yaml` file controls which files are considered text and which are excluded by default. Example:

```yaml
text_extensions:
  - .py
  - .md
  - .yaml
  - .toml
  - .lock
default_exclusions:
  - "*.exe"
  - "*.png"
  - ".git/*"
  - ".mypy_cache/*"
default_output: repo_combined.txt
token_multiplier: 1.3
```

- `text_extensions`: File extensions considered text (e.g., `.py`, `.md`).
- `default_exclusions`: Patterns to always exclude (e.g., `.git/*`, `*.jpg`).
- `default_output`: Default output file name.
- `token_multiplier`: Multiplier for estimating AI model token count.

## Output Formats

Git2one supports multiple output formats:

### Text Format (Default)
The default text format contains concatenated files, each prefixed with a header:

```
--- File: path/to/file.py ---
[content of file.py]

--- File: path/to/another.md ---
[content of another.md]
```

### JSON Format
JSON format provides structured data with metadata:

```json
{
  "files": [
    {
      "path": "path/to/file.py",
      "content": "[file content]",
      "size": 1234,
      "lines": 45
    }
  ],
  "summary": {
    "total_files": 1,
    "total_size": 1234
  }
}
```

### XML Format
XML format for structured data processing:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<repository>
  <file path="path/to/file.py">
    <content><![CDATA[[file content]]]></content>
  </file>
</repository>
```

### Markdown Format
Markdown format with syntax highlighting for documentation:

```markdown
# Repository Contents

Total files: 2

## path/to/file.py

```python
[file content with syntax highlighting]
```

## path/to/another.md

```markdown
[file content]
```
```

The script logs included/excluded files and estimates the total token count for AI model compatibility.

## Troubleshooting
- **No files included**: Check `config.yaml` for correct `text_extensions`. Verify the repository path:
  ```bash
  ls /path/to/repository/src/*.py
  ```
- **Files in `debug/` or `outputs/` included**: Ensure `.gitignore` excludes these directories. You can test your theory by explicitly excluding them with --exclude "debug/".
- **High token count**: Exclude large files like `poetry.lock`:
  ```bash
  python git2one.py /path/to/repository --exclude "poetry.lock"
  ```
- **`.gitignore` not respected**: Verify `.gitignore` exists in the repository root and contains valid patterns. You can test if it's being ignored by running with --ignore-gitignore.

## Testing

Run the test suite to verify functionality:

```bash
python -m pytest test_git2one.py -v
```

Or run tests with unittest:

```bash
python test_git2one.py
```

The test suite covers:
- Configuration loading
- File filtering and pattern matching
- Comment stripping functionality
- Multiple output formats
- Repository processing with various options

## License
MIT License. See `LICENSE` for details.

## Contributing

We welcome contributions to git2one! This section outlines the process for contributing to this project.

### Getting Started

1. **Fork the repository** on GitHub at [https://github.com/stkzlv/git2one](https://github.com/stkzlv/git2one)
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/git2one.git
   cd git2one
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Guidelines

#### Code Style
- Follow [PEP 8](https://pep8.org/) Python style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

#### Testing
- **Write tests** for all new functionality
- **Run existing tests** to ensure nothing breaks:
  ```bash
  python test_git2one.py
  ```
- Aim for high test coverage of new code
- Test edge cases and error conditions

#### Documentation
- Update the README.md if you add new features
- Add inline comments for complex logic
- Update configuration examples if needed
- Include usage examples for new features

### Submitting Changes

1. **Commit your changes** with clear, descriptive messages:
   ```bash
   git add .
   git commit -m "Add JSON output format support
   
   - Implement JSON formatter with file metadata
   - Add auto-detection of output format from file extension
   - Update CLI to support --format option
   - Add comprehensive tests for new functionality"
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request** on [GitHub](https://github.com/stkzlv/git2one) with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Reference any related issues
   - Screenshots or examples if applicable

### Pull Request Guidelines

- **One feature per PR**: Keep pull requests focused on a single feature or bug fix
- **Update tests**: Ensure all tests pass and add new tests for your changes
- **Update documentation**: Include relevant documentation updates
- **Clean commit history**: Squash commits if necessary to maintain a clean history
- **Respond to feedback**: Address review comments promptly and professionally

### Reporting Issues

When reporting bugs or requesting features:

1. **Search existing issues** first to avoid duplicates
2. **Use the issue templates** if available
3. **Provide detailed information**:
   - Python version
   - Operating system
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Sample code or repository (if applicable)

### Code of Conduct

- **Be respectful** and inclusive in all interactions
- **Provide constructive feedback** in code reviews
- **Help newcomers** and answer questions when possible
- **Focus on the code**, not the person
- **Assume good intentions** from other contributors

### Development Setup

For more advanced development:

1. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run tests with coverage**:
   ```bash
   python -m pytest test_git2one.py --cov=git2one --cov-report=html
   ```

3. **Check code style**:
   ```bash
   flake8 git2one.py test_git2one.py
   ```

### Feature Requests

We're always interested in new features! Before implementing:

1. **Open an issue** to discuss the feature
2. **Explain the use case** and why it would be valuable
3. **Consider backwards compatibility**
4. **Discuss implementation approach** if complex

### Questions?

- Open an issue with the "question" label on [GitHub](https://github.com/stkzlv/git2one/issues)
- Check existing issues and documentation first
- Be specific about what you're trying to achieve

Thank you for contributing to git2one! 🎉

## Support

If you find this tool useful, please consider:
- ⭐ Starring the repository on [GitHub](https://github.com/stkzlv/git2one)
- 🐛 Reporting bugs or requesting features via [Issues](https://github.com/stkzlv/git2one/issues)
- 🔀 Contributing improvements via [Pull Requests](https://github.com/stkzlv/git2one/pulls)

## Author

Created and maintained by [stkzlv](https://github.com/stkzlv).
