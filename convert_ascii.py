#!/usr/bin/env python3
"""
Convert ASCII box diagrams to Mermaid flowcharts
Handles common patterns in the repository
"""

import re
import os
from pathlib import Path

def is_ascii_diagram(block):
    """Check if a code block contains ASCII diagram patterns"""
    # Must have box characters or arrow patterns
    box_patterns = ['+---', '|  ', '───', '│', '-->']
    diagram_indicators = sum(1 for p in box_patterns if p in block)
    return diagram_indicators >= 2 and len(block.split('\n')) >= 5

def convert_ascii_to_mermaid(ascii_block, context=""):
    """
    Convert ASCII diagram to Mermaid markdown table or list format
    For complex diagrams, convert to structured markdown instead
    """
    lines = ascii_block.strip().split('\n')
    
    # Check if it's a table-like structure with consistent columns
    if looks_like_table(ascii_block):
        return convert_to_markdown_table(ascii_block)
    
    # Convert box diagrams to bullet list with sections
    return convert_to_structured_markdown(ascii_block)

def looks_like_table(block):
    """Check if ASCII block looks like a table"""
    lines = [l for l in block.split('\n') if l.strip()]
    # Tables have consistent | characters
    pipe_counts = [l.count('|') for l in lines if '|' in l]
    if len(pipe_counts) >= 3:
        # Check if pipe counts are consistent
        return len(set(pipe_counts)) <= 2
    return False

def convert_to_markdown_table(ascii_block):
    """Convert ASCII table to Markdown table"""
    lines = ascii_block.strip().split('\n')
    
    # Find content lines (not borders)
    content_lines = []
    for line in lines:
        if '+' not in line or '---' not in line:
            # This is a content line
            if '|' in line:
                # Extract content between pipes
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if parts:
                    content_lines.append(parts)
    
    if not content_lines:
        return ascii_block  # Can't convert
    
    # Build markdown table
    if len(content_lines) == 0:
        return ascii_block
        
    # Determine column count
    max_cols = max(len(row) for row in content_lines)
    
    # Build header and rows
    result = []
    if content_lines:
        # First row as header
        header = content_lines[0]
        header = header + [''] * (max_cols - len(header))
        result.append('| ' + ' | '.join(header) + ' |')
        result.append('|' + '|'.join(['---' for _ in range(max_cols)]) + '|')
        
        # Remaining rows
        for row in content_lines[1:]:
            row = row + [''] * (max_cols - len(row))
            result.append('| ' + ' | '.join(row) + ' |')
    
    return '\n'.join(result)

def convert_to_structured_markdown(ascii_block):
    """Convert complex ASCII diagram to structured markdown with headers"""
    lines = ascii_block.strip().split('\n')
    
    # Try to identify a title
    title = None
    for line in lines[:5]:
        if line.strip() and '+' not in line and '|' not in line and '─' not in line:
            title = line.strip()
            break
    
    # Extract key components from box content
    components = []
    current_section = None
    
    for line in lines:
        stripped = line.strip()
        
        # Skip border lines
        if '+' in stripped and ('-' in stripped or '─' in stripped):
            continue
        
        # Look for section headers (lines with content but no box chars)
        if stripped and '|' not in stripped and '+' not in stripped and '│' not in stripped:
            if ':' in stripped:
                current_section = stripped.rstrip(':')
            elif len(stripped) > 3 and not stripped.startswith('-'):
                current_section = stripped
        
        # Look for content in boxes
        if '|' in stripped or '│' in stripped:
            content = stripped.replace('|', '').replace('│', '').strip()
            if content and content not in ['+', '-']:
                if current_section:
                    components.append(f"  - {content}")
                else:
                    components.append(f"- {content}")
    
    if not components:
        return ascii_block  # Can't parse
    
    result = []
    if title:
        result.append(f"**{title}**\n")
    result.extend(components)
    
    return '\n'.join(result)

def process_file(filepath):
    """Process a single markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return 0, 0
    
    original_content = content
    conversions = 0
    
    # Find all code blocks (not mermaid, sql, python, etc.)
    # Pattern: ```\n...\n``` or ```text\n...\n```
    pattern = r'```(?:text)?\n((?:(?!```).)*?)\n```'
    
    def replace_block(match):
        nonlocal conversions
        block = match.group(1)
        
        if is_ascii_diagram(block):
            converted = convert_ascii_to_mermaid(block)
            if converted != block:
                conversions += 1
                # Return without code block markers for markdown tables/lists
                if converted.startswith('|') or converted.startswith('**') or converted.startswith('-'):
                    return converted
        
        return match.group(0)  # Return original if no conversion
    
    new_content = re.sub(pattern, replace_block, content, flags=re.DOTALL)
    
    if conversions > 0 and new_content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✓ {filepath}: Converted {conversions} diagrams")
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return 0, 0
    
    return conversions, 1 if conversions > 0 else 0

def main():
    base_path = Path('/run/media/qv/S/DE/Fun')
    
    # All folders to process
    folders = [
        'interview', 'mindset', 'roadmap', 
        'platforms', 'projects', 'fundamentals'
    ]
    
    total_conversions = 0
    total_files = 0
    
    for folder in folders:
        folder_path = base_path / folder
        if not folder_path.exists():
            continue
        
        print(f"\n📁 Processing {folder}/")
        print("-" * 40)
        
        for md_file in folder_path.glob('*.md'):
            convs, files = process_file(md_file)
            total_conversions += convs
            total_files += files
    
    print("\n" + "=" * 40)
    print(f"✅ Converted {total_conversions} ASCII diagrams in {total_files} files")

if __name__ == '__main__':
    main()
