import os
import tempfile
import unittest
from pathlib import Path
import yaml
import json
from git2one import (
    load_config, is_text_file, should_ignore, strip_python_comments,
    estimate_tokens, concatenate_repo
)


class TestGit2One(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test config
        self.test_config = {
            'text_extensions': ['.py', '.md', '.txt', '.json'],
            'default_exclusions': ['*.exe', '*.png', '.git/*'],
            'default_output': 'test_output.txt',
            'token_multiplier': 1.3
        }
        
        # Write test config file
        self.config_path = self.test_path / 'test_config.yaml'
        with open(self.config_path, 'w') as f:
            yaml.dump(self.test_config, f)
    
    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_load_config(self):
        """Test configuration loading."""
        config = load_config(self.config_path)
        self.assertEqual(config['text_extensions'], ['.py', '.md', '.txt', '.json'])
        self.assertEqual(config['token_multiplier'], 1.3)
    
    def test_load_config_file_not_found(self):
        """Test loading non-existent config file."""
        with self.assertRaises(FileNotFoundError):
            load_config('nonexistent.yaml')
    
    def test_is_text_file(self):
        """Test text file detection."""
        text_extensions = ['.py', '.md', '.txt']
        
        self.assertTrue(is_text_file(Path('test.py'), text_extensions))
        self.assertTrue(is_text_file(Path('README.md'), text_extensions))
        self.assertFalse(is_text_file(Path('image.png'), text_extensions))
        self.assertFalse(is_text_file(Path('binary.exe'), text_extensions))
    
    def test_should_ignore(self):
        """Test file/directory ignore patterns."""
        ignore_patterns = ['*.exe', '.git/*', 'temp/*']
        
        self.assertTrue(should_ignore(Path('app.exe'), ignore_patterns))
        self.assertTrue(should_ignore(Path('.git/config'), ignore_patterns))
        self.assertTrue(should_ignore(Path('temp/file.txt'), ignore_patterns))
        self.assertFalse(should_ignore(Path('src/main.py'), ignore_patterns))
    
    def test_strip_python_comments(self):
        """Test Python comment stripping."""
        code_with_comments = '''
# This is a comment
def hello():
    """This is a docstring"""
    print("Hello")  # Inline comment
    return True

# Another comment
'''
        
        stripped = strip_python_comments(code_with_comments)
        self.assertNotIn('#', stripped)
        self.assertNotIn('"""', stripped)
        self.assertIn('def hello():', stripped)
        self.assertIn('print("Hello")', stripped)
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        content = "Hello world! This is a test."
        tokens = estimate_tokens(content, 1.0)
        self.assertGreater(tokens, 0)
        
        # Test with multiplier
        tokens_with_multiplier = estimate_tokens(content, 1.5)
        self.assertGreater(tokens_with_multiplier, tokens)
    
    def create_test_repo(self):
        """Create a test repository structure."""
        # Create files
        (self.test_path / 'main.py').write_text('print("Hello, World!")')
        (self.test_path / 'README.md').write_text('# Test Project\nThis is a test.')
        (self.test_path / 'config.json').write_text('{"key": "value"}')
        (self.test_path / 'binary.exe').write_bytes(b'\x00\x01\x02\x03')
        
        # Create subdirectory
        subdir = self.test_path / 'src'
        subdir.mkdir()
        (subdir / 'utils.py').write_text('def utility_function():\n    pass')
        
        # Create .gitignore
        (self.test_path / '.gitignore').write_text('*.exe\n*.log\n')
    
    def test_concatenate_repo_basic(self):
        """Test basic repository concatenation."""
        self.create_test_repo()
        output_file = self.test_path / 'output.txt'
        
        concatenate_repo(
            repo_path=str(self.test_path),
            output_file=str(output_file),
            config=self.test_config
        )
        
        self.assertTrue(output_file.exists())
        content = output_file.read_text()
        
        # Check that text files are included
        self.assertIn('--- File: main.py ---', content)
        self.assertIn('--- File: README.md ---', content)
        self.assertIn('--- File: config.json ---', content)
        self.assertIn('--- File: src/utils.py ---', content)
        
        # Check that binary files are excluded
        self.assertNotIn('binary.exe', content)
    
    def test_concatenate_repo_with_include_patterns(self):
        """Test concatenation with include patterns."""
        self.create_test_repo()
        output_file = self.test_path / 'output.txt'
        
        concatenate_repo(
            repo_path=str(self.test_path),
            output_file=str(output_file),
            config=self.test_config,
            include_patterns=['*.py']
        )
        
        content = output_file.read_text()
        self.assertIn('--- File: main.py ---', content)
        self.assertIn('--- File: src/utils.py ---', content)
        self.assertNotIn('--- File: README.md ---', content)
        self.assertNotIn('--- File: config.json ---', content)
    
    def test_concatenate_repo_with_exclude_patterns(self):
        """Test concatenation with exclude patterns."""
        self.create_test_repo()
        output_file = self.test_path / 'output.txt'
        
        concatenate_repo(
            repo_path=str(self.test_path),
            output_file=str(output_file),
            config=self.test_config,
            exclude_patterns=['*.md']
        )
        
        content = output_file.read_text()
        self.assertIn('--- File: main.py ---', content)
        self.assertNotIn('--- File: README.md ---', content)
    
    def test_concatenate_repo_strip_comments(self):
        """Test concatenation with comment stripping."""
        self.create_test_repo()
        
        # Create Python file with comments
        py_file = self.test_path / 'commented.py'
        py_file.write_text('''
# This is a comment
def test():
    """Docstring"""
    return True  # Inline comment
''')
        
        output_file = self.test_path / 'output.txt'
        
        concatenate_repo(
            repo_path=str(self.test_path),
            output_file=str(output_file),
            config=self.test_config,
            strip_comments=True
        )
        
        content = output_file.read_text()
        # Comments should be stripped from Python files
        self.assertNotIn('# This is a comment', content)
        self.assertNotIn('"""Docstring"""', content)


if __name__ == '__main__':
    unittest.main() 