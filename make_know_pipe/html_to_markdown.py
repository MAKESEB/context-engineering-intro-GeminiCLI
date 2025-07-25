#!/usr/bin/env python3
"""
Simple HTML to Markdown Converter
Converts HTML content to clean Markdown format
"""

import re
import sys

def html_to_markdown(html_content):
    """Convert HTML content to Markdown"""
    content = html_content
    
    # Remove CSS styles and scripts
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    
    # Convert headings
    content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', content, flags=re.DOTALL)
    content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', content, flags=re.DOTALL)
    content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', content, flags=re.DOTALL)
    content = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', content, flags=re.DOTALL)
    content = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1', content, flags=re.DOTALL)
    content = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1', content, flags=re.DOTALL)
    
    # Convert paragraphs
    content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', content, flags=re.DOTALL)
    
    # Convert lists
    content = re.sub(r'<ul[^>]*>', '', content)
    content = re.sub(r'</ul>', '\n', content)
    content = re.sub(r'<ol[^>]*>', '', content)
    content = re.sub(r'</ol>', '\n', content)
    content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', content, flags=re.DOTALL)
    
    # Convert links
    content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', content, flags=re.DOTALL)
    
    # Convert emphasis
    content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', content, flags=re.DOTALL)
    content = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', content, flags=re.DOTALL)
    content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', content, flags=re.DOTALL)
    content = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', content, flags=re.DOTALL)
    
    # Convert code
    content = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', content, flags=re.DOTALL)
    content = re.sub(r'<pre[^>]*>(.*?)</pre>', r'```\n\1\n```', content, flags=re.DOTALL)
    
    # Convert time elements
    content = re.sub(r'<time[^>]*datetime="([^"]*)"[^>]*>[^<]*</time>', r'**Date: \1**', content)
    
    # Convert tables (basic)
    content = re.sub(r'<table[^>]*>', '\n', content)
    content = re.sub(r'</table>', '\n', content)
    content = re.sub(r'<tr[^>]*>', '', content)
    content = re.sub(r'</tr>', '\n', content)
    content = re.sub(r'<th[^>]*>(.*?)</th>', r'| **\1** ', content, flags=re.DOTALL)
    content = re.sub(r'<td[^>]*>(.*?)</td>', r'| \1 ', content, flags=re.DOTALL)
    
    # Remove remaining HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Clean up HTML entities
    entities = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&mdash;': '—',
        '&ndash;': '–',
        '&hellip;': '…'
    }
    
    for entity, replacement in entities.items():
        content = content.replace(entity, replacement)
    
    # Clean up whitespace
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)
    content = content.strip()
    
    return content

def convert_file(input_file, output_file=None):
    """Convert HTML file to Markdown"""
    if output_file is None:
        output_file = input_file
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"Converting {input_file}...")
        print(f"Original size: {len(html_content)} characters")
        
        markdown_content = html_to_markdown(html_content)
        
        # Add header
        header = """# Developer Documentation

*Converted from HTML to Markdown*

---

"""
        
        final_content = header + markdown_content
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"Converted size: {len(final_content)} characters")
        print(f"✅ Conversion completed: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python html_to_markdown.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_file(input_file, output_file)