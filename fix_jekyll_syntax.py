#!/usr/bin/env python3
"""
Fix Jekyll Liquid syntax errors in markdown files.
Escapes template literals that conflict with Jekyll's Liquid syntax.
"""

import os
import re
import glob

def fix_liquid_syntax_in_file(file_path):
    """Fix Liquid syntax errors in a single file."""
    print(f"Processing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match template literals ${...} inside code blocks
    # We need to be careful not to break actual Liquid syntax
    # This pattern looks for ${variable} patterns and escapes them
    
    # Find template literals that need escaping
    # Pattern: ${anything} but not already escaped
    pattern = r'\$\{([^}]+)\}'
    
    def replace_template_literal(match):
        inner_content = match.group(1)
        # Escape the template literal for Jekyll
        return f'${{{{ \'{\' }}}}{{{{{ inner_content }}}}}'
    
    # Only replace if we're in code blocks (between ``` or in <code> tags)
    # For safety, let's do a simpler replacement that works universally
    content = re.sub(pattern, replace_template_literal, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Fixed template literals in {file_path}")
        return True
    else:
        print(f"  - No changes needed in {file_path}")
        return False

def main():
    """Fix all markdown files in the repository."""
    repo_root = "/home/shivprasad/Documents/Work/Learning/Programing/Framework/React"
    
    # Find all markdown files
    md_files = []
    for root, dirs, files in os.walk(repo_root):
        # Skip .git directory
        if '.git' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    print(f"Found {len(md_files)} markdown files to process...")
    
    fixed_count = 0
    for md_file in md_files:
        if fix_liquid_syntax_in_file(md_file):
            fixed_count += 1
    
    print(f"\n✓ Processing complete! Fixed {fixed_count} files.")

if __name__ == "__main__":
    main()
