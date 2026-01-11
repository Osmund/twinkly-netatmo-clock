#!/usr/bin/env python3
"""
Icon Editor for Twinkly Square
Web-based editor for creating and editing 24x16 icons
"""
from flask import Flask, render_template, request, jsonify
import json
import os
import re
from pathlib import Path

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

ICONS_FILE = Path(__file__).parent / 'icons.py'


def parse_icons_from_file():
    """Parser eksisterende ikoner fra icons.py"""
    with open(ICONS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Finn LOCATION_ICONS dictionary
    icons = {}
    
    # Find the LOCATION_ICONS dictionary section
    dict_match = re.search(r'LOCATION_ICONS\s*=\s*\{(.*)\n\}', content, re.DOTALL)
    if not dict_match:
        return icons
    
    dict_content = dict_match.group(1)
    
    # Split by icon entries - look for pattern: 'name': [
    # Use a more robust approach: find each 'name': and capture until the next 'name': or end
    icon_entries = []
    lines = dict_content.split('\n')
    
    current_icon_name = None
    current_icon_lines = []
    
    for line in lines:
        # Check if this line starts a new icon definition
        name_match = re.match(r"\s*'([^']+)':\s*\[", line)
        if name_match:
            # Save previous icon if exists
            if current_icon_name and current_icon_lines:
                icon_entries.append((current_icon_name, current_icon_lines))
            # Start new icon
            current_icon_name = name_match.group(1)
            current_icon_lines = [line]
        elif current_icon_name:
            # Continue collecting lines for current icon
            current_icon_lines.append(line)
            # Check if this is the end of the icon (closing bracket with optional comma)
            if re.match(r'\s*\],?\s*$', line):
                # Icon complete
                icon_entries.append((current_icon_name, current_icon_lines))
                current_icon_name = None
                current_icon_lines = []
    
    # Parse each icon entry
    for icon_name, icon_lines in icon_entries:
        rows = []
        for line in icon_lines:
            # Look for lines with array data [0, 1, 0, ...]
            if '[' in line and any(c.isdigit() for c in line):
                # Extract numbers from the line
                numbers_str = re.search(r'\[([0-9,\s]+)\]', line)
                if numbers_str:
                    row = [int(x.strip()) for x in numbers_str.group(1).split(',') if x.strip()]
                    if len(row) == 24:
                        rows.append(row)
        
        if len(rows) == 16:
            icons[icon_name] = rows
    
    return icons


def save_icon_to_file(icon_name, icon_data):
    """Lagrer eller oppdaterer et ikon i icons.py"""
    # Les eksisterende fil
    with open(ICONS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Format icon data som Python code - aldri split array-elementer over flere linjer
    icon_str_lines = [f"    '{icon_name}': ["]
    for row in icon_data:
        # Skriv hele raden på én linje - Python håndterer lange linjer fint
        row_str = '[' + ', '.join(str(x) for x in row) + '],'
        icon_str_lines.append(f"        {row_str}")
    # Fjern siste komma og legg til avsluttende bracket
    if icon_str_lines[-1].endswith(','):
        icon_str_lines[-1] = icon_str_lines[-1][:-1]
    icon_str_lines.append("    ],")
    icon_str = '\n'.join(icon_str_lines)
    
    # Find the LOCATION_ICONS dictionary
    dict_match = re.search(r'(LOCATION_ICONS\s*=\s*\{)(.*?)(\n\})', content, re.DOTALL)
    if not dict_match:
        raise Exception("Could not find LOCATION_ICONS dictionary")
    
    dict_start = dict_match.group(1)
    dict_content = dict_match.group(2)
    dict_end = dict_match.group(3)
    
    # Check if icon exists
    icon_pattern = rf"\s*'{re.escape(icon_name)}':\s*\[.*?\],?\s*"
    
    # Try to find and replace existing icon
    lines = dict_content.split('\n')
    new_lines = []
    skip_until_end = False
    icon_found = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if skip_until_end:
            # Skip lines until we find the closing bracket
            if re.match(r'\s*\],?\s*$', line):
                skip_until_end = False
            i += 1
            continue
        
        # Check if this line starts our icon
        if re.match(rf"\s*'{re.escape(icon_name)}':\s*\[", line):
            # Found it, replace with new version
            new_lines.append(icon_str)
            skip_until_end = True
            icon_found = True
            i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    if not icon_found:
        # Add new icon at the end (before last line which should be empty)
        # Remove trailing empty lines
        while new_lines and not new_lines[-1].strip():
            new_lines.pop()
        
        # Add comma to last icon if needed
        if new_lines and not new_lines[-1].rstrip().endswith(','):
            new_lines[-1] = new_lines[-1].rstrip() + ','
        
        new_lines.append(icon_str)
    
    # Rebuild content
    new_dict_content = '\n'.join(new_lines)
    new_content = dict_start + new_dict_content + dict_end
    
    # Replace the dictionary in the original content
    content = content[:dict_match.start()] + new_content + content[dict_match.end():]
    
    # Skriv tilbake til fil
    with open(ICONS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)


@app.route('/')
def index():
    """Hovedside for icon editor"""
    return render_template('icon_editor.html')


@app.route('/api/icons', methods=['GET'])
def get_icons():
    """Hent alle tilgjengelige ikoner"""
    try:
        icons = parse_icons_from_file()
        return jsonify({'success': True, 'icons': icons})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/icons/<icon_name>', methods=['GET'])
def get_icon(icon_name):
    """Hent et spesifikt ikon"""
    try:
        icons = parse_icons_from_file()
        if icon_name in icons:
            return jsonify({'success': True, 'icon': icons[icon_name], 'name': icon_name})
        else:
            return jsonify({'success': False, 'error': 'Icon not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/icons/<icon_name>', methods=['POST'])
def save_icon(icon_name):
    """Lagre eller oppdater et ikon"""
    try:
        data = request.json
        icon_data = data.get('icon')
        
        # Valider data
        if not icon_data or len(icon_data) != 16:
            return jsonify({'success': False, 'error': 'Invalid icon data: must be 16 rows'}), 400
        
        for row in icon_data:
            if len(row) != 24:
                return jsonify({'success': False, 'error': 'Invalid icon data: each row must have 24 columns'}), 400
            if not all(x in [0, 1] for x in row):
                return jsonify({'success': False, 'error': 'Invalid icon data: values must be 0 or 1'}), 400
        
        # Lagre ikon
        save_icon_to_file(icon_name, icon_data)
        
        return jsonify({'success': True, 'message': f'Icon "{icon_name}" saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/icons/<icon_name>', methods=['DELETE'])
def delete_icon(icon_name):
    """Slett et ikon"""
    try:
        # Les eksisterende fil
        with open(ICONS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fjern ikon-entry
        pattern = rf",?\s*'{re.escape(icon_name)}':\s*\[((?:\s*\[[^\]]+\],?)*)\s*\]"
        
        if not re.search(pattern, content):
            return jsonify({'success': False, 'error': 'Icon not found'}), 404
        
        content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
        
        # Skriv tilbake
        with open(ICONS_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({'success': True, 'message': f'Icon "{icon_name}" deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Icon Editor for Twinkly Square")
    print("=" * 60)
    print("Åpne nettleser på: http://localhost:5000")
    print("Trykk Ctrl+C for å stoppe")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
