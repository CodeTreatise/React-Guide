#!/usr/bin/env python3
import re
import glob
import os

def fix_template_literals(content):
    """Fix template literals by wrapping entire code blocks with raw tags."""
    lines = content.split('\n')
    result_lines = []
    in_code_block = False
    code_block_lines = []
    
    for line in lines:
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block - check if it has template literals
                code_content = '\n'.join(code_block_lines)
                if '${' in code_content:
                    # Wrap the entire code block content with raw tags
                    result_lines.append('{% raw %}')
                    result_lines.extend(code_block_lines)
                    result_lines.append('{% endraw %}')
                else:
                    result_lines.extend(code_block_lines)
                result_lines.append(line)  # Add closing ```
                code_block_lines = []
                in_code_block = False
            else:
                # Start of code block
                result_lines.append(line)  # Add opening ```
                in_code_block = True
        elif in_code_block:
            code_block_lines.append(line)
        else:
            result_lines.append(line)
    
    return '\n'.join(result_lines)

def process_file(filepath):
    """Process a single markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '${' in content:
            fixed_content = fix_template_literals(content)
            if fixed_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"Fixed: {filepath}")
                return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    
    return False

def main():
    """Process all markdown files."""
    fixed_count = 0
    
    for root, dirs, files in os.walk('.'):
        if '.git' in root:
            continue
        
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                if process_file(filepath):
                    fixed_count += 1
    
    print(f"Fixed {fixed_count} files total")

if __name__ == '__main__':
    main()
