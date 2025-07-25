#!/usr/bin/env python3
import re

# Read the HTML file
with open('intake/data/developerdocs.md', 'r', encoding='utf-8') as f:
    content = f.read()

print('Processing HTML content...')

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

# Add header
header = '''# Developer Documentation

*Converted from HTML to Markdown*

---

'''

final_content = header + content

# Write back to file
with open('intake/data/developerdocs.md', 'w', encoding='utf-8') as f:
    f.write(final_content)

print('✅ HTML to Markdown conversion completed!')
print('File saved: intake/data/developerdocs.md')