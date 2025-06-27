import os
import re
import argparse
import yaml
import json
from pathlib import Path
from fnmatch import fnmatch
from gitignore_parser import parse_gitignore

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def is_text_file(file_path, text_extensions):
    return file_path.suffix.lower() in text_extensions

def should_ignore(file_path, ignore_patterns):
    # Use forward slashes for cross-platform consistency in matching
    file_path_str = str(file_path).replace(os.sep, '/')
    return any(fnmatch(file_path_str, pattern) for pattern in ignore_patterns)

def strip_python_comments(content):
    """
    Strips Python-style comments and docstrings.
    Handles single-line '#' comments and multi-line triple-quoted strings.
    """
    # Remove multi-line strings (docstrings)
    content = re.sub(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')', '', content)
    # Remove single-line comments
    content = re.sub(r'#.*', '', content)
    # Remove resulting blank lines
    content = '\n'.join(line for line in content.splitlines() if line.strip())
    return content

def estimate_tokens(content, token_multiplier):
    tokens = re.findall(r'\w+|[^\w\s]', content, re.UNICODE)
    return int(len(tokens) * token_multiplier)

def write_text_format(outfile, files_data):
    """Write files in plain text format."""
    for file_data in files_data:
        outfile.write(f'--- File: {file_data["path"]} ---\n')
        outfile.write(file_data["content"])
        outfile.write('\n\n')

def write_json_format(outfile, files_data):
    """Write files in JSON format."""
    json_data = {
        "files": [
            {
                "path": file_data["path"],
                "content": file_data["content"],
                "size": len(file_data["content"]),
                "lines": len(file_data["content"].splitlines())
            }
            for file_data in files_data
        ],
        "summary": {
            "total_files": len(files_data),
            "total_size": sum(len(f["content"]) for f in files_data)
        }
    }
    json.dump(json_data, outfile, indent=2, ensure_ascii=False)

def write_xml_format(outfile, files_data):
    """Write files in XML format."""
    outfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    outfile.write('<repository>\n')
    for file_data in files_data:
        path = file_data["path"].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        content = file_data["content"].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        outfile.write(f'  <file path="{path}">\n')
        outfile.write(f'    <content><![CDATA[{content}]]></content>\n')
        outfile.write('  </file>\n')
    outfile.write('</repository>\n')

def write_markdown_format(outfile, files_data):
    """Write files in Markdown format."""
    outfile.write('# Repository Contents\n\n')
    outfile.write(f'Total files: {len(files_data)}\n\n')
    
    for file_data in files_data:
        outfile.write(f'## {file_data["path"]}\n\n')
        
        # Determine language for syntax highlighting
        ext = Path(file_data["path"]).suffix.lower()
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.java': 'java',
            '.cpp': 'cpp', '.c': 'c', '.cs': 'csharp', '.go': 'go',
            '.html': 'html', '.css': 'css', '.json': 'json',
            '.xml': 'xml', '.yaml': 'yaml', '.yml': 'yaml',
            '.toml': 'toml', '.sh': 'bash', '.sql': 'sql'
        }
        lang = lang_map.get(ext, '')
        
        outfile.write(f'```{lang}\n')
        outfile.write(file_data["content"])
        outfile.write('\n```\n\n')

def get_output_format(output_file):
    """Determine output format from file extension."""
    ext = Path(output_file).suffix.lower()
    if ext == '.json':
        return 'json'
    elif ext == '.xml':
        return 'xml'
    elif ext == '.md':
        return 'markdown'
    else:
        return 'text'

def concatenate_repo(repo_path, output_file, config, include_patterns=None, exclude_patterns=None,
                    ignore_gitignore=False, strip_comments=False, output_format=None):
    repo_path = Path(repo_path).resolve()  
    output_path = Path(output_file).resolve()

    # Determine output format
    if output_format is None:
        output_format = get_output_format(output_file)

    # Process and normalize exclusion patterns for fnmatch
    all_exclude_patterns = (exclude_patterns or []) + config.get('default_exclusions', [])
    ignore_patterns = []
    if all_exclude_patterns:
        for p in all_exclude_patterns:
            # Use forward slashes for consistency, and remove leading './'
            norm_p = p.replace(os.sep, '/')
            if norm_p.startswith('./'):
                norm_p = norm_p[2:]
            
            if norm_p.endswith('/'):
                # This is a directory pattern. Match the directory itself and all its contents.
                # e.g. 'tests/' -> match 'tests' and 'tests/*'
                dir_path = norm_p.rstrip('/')
                ignore_patterns.append(dir_path)
                ignore_patterns.append(f"{dir_path}/*")
            else:
                # This is a file or glob pattern
                ignore_patterns.append(norm_p)

    # Process and normalize inclusion patterns for fnmatch
    processed_include_patterns = []
    if include_patterns:
        for p in include_patterns:
            norm_p = p.replace(os.sep, '/')
            if norm_p.startswith('./'):
                norm_p = norm_p[2:]
            
            # If user provides 'src/', they mean everything inside.
            if norm_p.endswith('/'):
                processed_include_patterns.append(f"{norm_p}*")
            else:
                processed_include_patterns.append(norm_p)
    include_patterns = processed_include_patterns

    gitignore_matcher = None
    if not ignore_gitignore and (repo_path / '.gitignore').exists():
        try:
            # base_dir is important for gitignore_parser to resolve paths correctly
            gitignore_matcher = parse_gitignore(repo_path / '.gitignore', base_dir=repo_path)
            print(f"Using .gitignore from {repo_path / '.gitignore'}")
        except Exception as e:
            print(f"Error parsing .gitignore: {e}")
            gitignore_matcher = None
            
    total_tokens = 0
    file_count = 0
    files_data = []
    
    for root, dirs, files in os.walk(repo_path, topdown=True):
            root_path = Path(root).resolve()
            try:
                rel_root = root_path.relative_to(repo_path)
                # Use a placeholder for the root directory itself for cleaner output
                print(f"Processing directory: {'.' if str(rel_root) == '.' else rel_root}")
            except ValueError:
                print(f"Skipping directory outside repo: {root}")
                continue

            # Prune directories based on custom exclude patterns first
            dirs[:] = [d for d in dirs if not should_ignore(rel_root / d, ignore_patterns)]
            
            # Then, prune directories based on .gitignore
            if gitignore_matcher:
                dirs[:] = [d for d in dirs if not gitignore_matcher(root_path / d)]

            for file in files:
                file_path = root_path / file
                try:
                    rel_path = file_path.relative_to(repo_path)
                except ValueError:
                    print(f"Skipping file outside repo: {file_path}")
                    continue

                # Normalize path for matching
                norm_path_str = str(rel_path).replace(os.sep, '/')

                if include_patterns and not any(fnmatch(norm_path_str, pattern) for pattern in include_patterns):
                    # This check is silent for less verbose output unless debugging
                    # print(f"Skipping file (not in include patterns): {rel_path}")
                    continue

                if should_ignore(rel_path, ignore_patterns):
                    print(f"Skipping file (matches exclude patterns): {rel_path}")
                    continue

                if gitignore_matcher and gitignore_matcher(file_path):
                    # This check is silent for less verbose output unless debugging
                    # print(f"Skipping file (matches .gitignore): {rel_path}")
                    continue
                
                if is_text_file(file_path, config['text_extensions']):
                    try:
                        with file_path.open('r', encoding='utf-8') as infile:
                            content = infile.read()
                            if strip_comments and file_path.suffix == '.py':
                                content = strip_python_comments(content)
                            if content.strip():
                                print(f"Including file: {rel_path}")
                                files_data.append({
                                    "path": norm_path_str,
                                    "content": content
                                })
                                file_count += 1
                                total_tokens += estimate_tokens(content, config['token_multiplier'])
                            else:
                                print(f"Skipping empty file after processing: {rel_path}")
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"Skipping file due to error: {rel_path} ({str(e)})")
                else:
                    # This check is silent for less verbose output unless debugging
                    # print(f"Skipping non-text file: {rel_path}")
                    pass

    # Write output in the specified format
    with output_path.open('w', encoding='utf-8') as outfile:
        if output_format == 'json':
            write_json_format(outfile, files_data)
        elif output_format == 'xml':
            write_xml_format(outfile, files_data)
        elif output_format == 'markdown':
            write_markdown_format(outfile, files_data)
        else:  # default to text format
            write_text_format(outfile, files_data)

    print(f"\nConcatenated {file_count} files into {output_file} ({output_format} format)")
    print(f"Estimated token count: {total_tokens} (approximate for GPT/Claude/Gemini)")

def main():
    parser = argparse.ArgumentParser(description="Concatenate a Git repository into a single text file.")
    parser.add_argument("repo_path", help="Path to the Git repository")
    parser.add_argument("--output", help="Output file name")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    parser.add_argument("--include", nargs='*', help="Include only files/directories matching these patterns")
    parser.add_argument("--exclude", nargs='*', help="Exclude files/directories matching these patterns")
    parser.add_argument("--ignore-gitignore", action="store_true", help="Ignore .gitignore file")
    parser.add_argument("--strip-comments", action="store_true", help="Strip Python-style comments and docstrings")
    parser.add_argument("--format", choices=['text', 'json', 'xml', 'markdown'], help="Output format (auto-detected from file extension if not specified)")
    args = parser.parse_args()
    
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: Config file not found at '{args.config}'")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing YAML config file: {e}")
        return

    output_file = args.output or config.get('default_output', 'repo_combined.txt')
    
    concatenate_repo(
        repo_path=args.repo_path,
        output_file=output_file,
        config=config,
        include_patterns=args.include,
        exclude_patterns=args.exclude,
        ignore_gitignore=args.ignore_gitignore,
        strip_comments=args.strip_comments,
        output_format=args.format
    )

if __name__ == "__main__":
    main()