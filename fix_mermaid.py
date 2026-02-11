#!/usr/bin/env python3
"""
Fix Mermaid Overlapping Subgraphs
Flattens nested subgraphs by converting subgraph labels to title nodes
"""

import re
import os
from pathlib import Path

def find_mermaid_blocks(content):
    """Find all mermaid code blocks in content"""
    pattern = r'```mermaid\n(.*?)```'
    return list(re.finditer(pattern, content, re.DOTALL))

def fix_subgraph(mermaid_code):
    """
    Fix subgraph labels by:
    1. Finding subgraphs with content labels
    2. Converting label to empty and adding a title node
    """
    lines = mermaid_code.split('\n')
    fixed_lines = []
    subgraph_stack = []
    modifications = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Match subgraph with label: subgraph Name["Label Text"]
        subgraph_match = re.match(r'^(\s*)subgraph\s+(\w+)\s*\["([^"]+)"\]', line)
        if subgraph_match:
            indent = subgraph_match.group(1)
            name = subgraph_match.group(2)
            label = subgraph_match.group(3)
            
            # Check if label is not empty
            if label.strip() and label.strip() != " ":
                # Create title node ID
                title_id = f"{name}_title"
                
                # Replace subgraph with empty label
                fixed_lines.append(f'{indent}subgraph {name}[" "]')
                
                # Add title node inside subgraph
                inner_indent = indent + "    "
                # Clean up label for node (escape special chars)
                clean_label = label.replace('<br/>', '<br/>')
                fixed_lines.append(f'{inner_indent}{title_id}["{clean_label}"]')
                fixed_lines.append(f'{inner_indent}style {title_id} fill:none,stroke:none,color:#333,font-weight:bold')
                
                subgraph_stack.append((name, title_id))
                modifications += 1
                continue
        
        # Match simple subgraph: subgraph Name
        simple_match = re.match(r'^(\s*)subgraph\s+(\w+)\s*$', line)
        if simple_match:
            subgraph_stack.append((simple_match.group(2), None))
        
        # Match end of subgraph
        if stripped == 'end':
            if subgraph_stack:
                subgraph_stack.pop()
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), modifications

def process_file(filepath):
    """Process a single markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return 0
    
    original_content = content
    total_mods = 0
    
    # Find all mermaid blocks
    blocks = find_mermaid_blocks(content)
    
    # Process in reverse order to maintain correct positions
    for match in reversed(blocks):
        mermaid_code = match.group(1)
        fixed_code, mods = fix_subgraph(mermaid_code)
        
        if mods > 0:
            # Replace the mermaid block
            start = match.start()
            end = match.end()
            content = content[:start] + '```mermaid\n' + fixed_code + '```' + content[end:]
            total_mods += mods
    
    if total_mods > 0:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ {filepath}: Fixed {total_mods} subgraphs")
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return 0
    
    return total_mods

def main():
    base_path = Path('/run/media/qv/S/DE/Fun')
    
    # Priority folders
    folders = ['fundamentals', 'papers', 'tools', 'platforms', 'interview', 'usecases', 'mindset', 'roadmap', 'projects']
    
    total_files = 0
    total_fixes = 0
    
    for folder in folders:
        folder_path = base_path / folder
        if not folder_path.exists():
            print(f"Folder not found: {folder_path}")
            continue
        
        print(f"\n📁 Processing {folder}/")
        print("-" * 40)
        
        for md_file in folder_path.glob('*.md'):
            fixes = process_file(md_file)
            if fixes > 0:
                total_files += 1
                total_fixes += fixes
    
    print("\n" + "=" * 40)
    print(f"✅ Total: Fixed {total_fixes} subgraphs in {total_files} files")

if __name__ == '__main__':
    main()
