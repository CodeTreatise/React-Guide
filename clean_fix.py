#!/usr/bin/env python3
"""
Clean up malformed raw tags and properly fix template literals.
"""

import re

def clean_and_fix_file(filepath):
    """Remove all raw tags and properly re-apply them."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove all existing raw tags
    content = re.sub(r'\{\% raw \%\}\n?', '', content)
    content = re.sub(r'\n?\{\% endraw \%\}', '', content)
    
    # Now properly wrap code blocks that contain template literals
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

# Fix the problematic file
filepath = '01-JavaScript-Prerequisites/01-ES6-Features.md'
fixed_content = clean_and_fix_file(filepath)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print(f"Cleaned and fixed: {filepath}")
