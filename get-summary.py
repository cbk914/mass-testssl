#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914

import os
import argparse
from bs4 import BeautifulSoup
from datetime import datetime
import re

def analyze_testssl_html(input_path, output_dir):
    vulnerabilities_summary = {}

    # Check if input_path is a directory or a file
    if os.path.isdir(input_path):
        files = [os.path.join(input_path, filename) for filename in os.listdir(input_path)]
        project_name = os.path.basename(os.path.normpath(input_path))
    elif os.path.isfile(input_path):
        files = [input_path]
        project_name = os.path.splitext(os.path.basename(input_path))[0]
    else:
        print(f"Error: {input_path} is not a valid file or directory.")
        return

    # Define patterns to identify vulnerability and host information
    host_pattern = re.compile(r'Start.*-->>(.*?)<<--')
    vulnerability_keywords = ['vulnerable', 'risk', 'exposure', 'insecure']
    false_positive_keywords = ['ok', 'not vulnerable', 'no risk', 'secure']

    # Loop through all files
    for file_path in files:
        # Skip files that are 4KB or less as they are considered failed scans
        if os.path.getsize(file_path) <= 4096:
            continue

        # Open and parse the HTML file
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'lxml')

        # Find the host information
        host_name = None
        host_name_tag = soup.find('span', text=host_pattern)
        if host_name_tag:
            match = host_pattern.search(host_name_tag.text)
            if match:
                host_name = match.group(1).strip()
        if not host_name:
            continue

        # Find the vulnerabilities section
        vulnerabilities_section = soup.find('span', text=lambda x: x and 'Testing vulnerabilities' in x)
        if not vulnerabilities_section:
            continue

        # Parse vulnerabilities and weak ciphers
        for vuln in vulnerabilities_section.find_all_next('span'):
            vuln_text = vuln.text.strip()
            vuln_lower = vuln_text.lower()

            # Skip false positives or benign findings
            if any(keyword in vuln_lower for keyword in false_positive_keywords):
                continue

            # Check if the text contains any key vulnerability indicators
            if not any(keyword in vuln_lower for keyword in vulnerability_keywords):
                continue

            # Extract vulnerability name using regex
            vuln_name_match = re.search(r'^([\w\s-]+?):', vuln_text) or re.search(r'^([\w\s-]+?) ', vuln_text)
            vuln_name = vuln_name_match.group(1).strip() if vuln_name_match else vuln_text

            # Capture additional metadata (e.g., "experimental")
            is_experimental = 'experimental' in vuln_lower
            if is_experimental:
                vuln_text = f"[Experimental] {vuln_text}"

            # Store the vulnerability and affected host
            if vuln_name not in vulnerabilities_summary:
                vulnerabilities_summary[vuln_name] = {'hosts': set(), 'details': set()}
            vulnerabilities_summary[vuln_name]['hosts'].add(host_name)
            vulnerabilities_summary[vuln_name]['details'].add(vuln_text)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Construct the output filename
    current_date = datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(output_dir, f"summary-{project_name}-{current_date}.html")

    # Write the summary to an output HTML file
    with open(output_file, 'w') as output:
        output.write('<html><body>\n')
        output.write('<h1>TestSSL Summary</h1>\n')

        for vuln_name, data in vulnerabilities_summary.items():
            output.write(f'<h2>Vulnerability: {vuln_name}</h2>\n')
            output.write('<h3>Affected Hosts:</h3>\n<ul>\n')
            for host in data['hosts']:
                output.write(f'  <li>{host}</li>\n')
            output.write('</ul>\n')

            output.write('<h3>Details:</h3>\n<ul>\n')
            for detail in data['details']:
                output.write(f'  <li>{detail}</li>\n')
            output.write('</ul>\n')

        output.write('</body></html>\n')

    print(f"Summary written to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Analyze testssl HTML output files and generate a summary.')
    parser.add_argument('-i', '--input', required=True, help='Input file or directory containing testssl HTML files.')
    parser.add_argument('-o', '--output', required=True, help='Output directory for the summary and result files.')
    args = parser.parse_args()

    analyze_testssl_html(args.input, args.output)

if __name__ == "__main__":
    main()
