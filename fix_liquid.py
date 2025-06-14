#!/usr/bin/env python3
import re
import glob
import os

def fix_template_literals(content):
    """Fix template literals by escaping them for Jekyll."""
    # Pattern to find code blocks and wrap them
    lines = content.split('\n')
    in_code_block = False
    result_lines = []
    
    for line in lines:
        # Check if we're entering or leaving a code block
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result_lines.append(line)
        elif in_code_block and '${' in line:
            # Escape template literals in code blocks
            escaped_line = re.sub(r'\$\{([^}]+)\}', r'{% raw %}${\1}{% endraw %}', line)
            result_lines.append(escaped_line)
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
