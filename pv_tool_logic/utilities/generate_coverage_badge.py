#!/usr/bin/env python3
"""
Simple coverage badge generator that doesn't rely on pkg_resources.
Fallback script for when coverage-badge or genbadge fail.
"""
import json
import os
import sys
from pathlib import Path


def get_coverage_percentage():
    """Extract coverage percentage from coverage.json file."""
    try:
        with open('coverage.json', 'r') as f:
            data = json.load(f)
        return round(data['totals']['percent_covered'], 1)
    except Exception as e:
        print(f"Could not read coverage.json: {e}")
        return None


def generate_simple_badge(percentage, output_path):
    """Generate a simple SVG badge."""
    # Color based on coverage percentage
    if percentage >= 90:
        color = "brightgreen"
    elif percentage >= 80:
        color = "green"
    elif percentage >= 70:
        color = "yellowgreen"
    elif percentage >= 60:
        color = "yellow"
    elif percentage >= 50:
        color = "orange"
    else:
        color = "red"

    # Simple SVG badge template
    svg_template = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="104" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <clipPath id="a">
        <rect width="104" height="20" rx="3" fill="#fff"/>
    </clipPath>
    <g clip-path="url(#a)">
        <path fill="#555" d="M0 0h63v20H0z"/>
        <path fill="url(#b)" d="M0 0h104v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110">
        <text x="325" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="530">coverage</text>
        <text x="325" y="140" transform="scale(.1)" textLength="530">coverage</text>
        <text x="825" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="310">{percentage}%</text>
        <text x="825" y="140" transform="scale(.1)" textLength="310">{percentage}%</text>
    </g>
</svg>'''

    with open(output_path, 'w') as f:
        f.write(svg_template)

    print(f"Coverage badge generated: {output_path} ({percentage}%)")


def main():
    """Main function to generate coverage badge."""
    output_path = sys.argv[1] if len(sys.argv) > 1 else "readme_images/coverage.svg"

    # Try to get coverage percentage
    percentage = get_coverage_percentage()

    if percentage is None:
        print("Could not determine coverage percentage, creating default badge")
        percentage = 0

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Generate the badge
    generate_simple_badge(percentage, output_path)


if __name__ == "__main__":
    main()
