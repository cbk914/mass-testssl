#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914
import os
import argparse
from bs4 import BeautifulSoup
from datetime import datetime

def analyze_testssl_html(input_path, output_dir):
    summary = {}

    # Check if input_path is a directory or a file
    if os.path.isdir(input_path):
        files = [os.path.join(input_path, filename) for filename in os.listdir(input_path)]
        project_name = os.path.basename(os.path.normpath(input_path))  # Use directory name as project name
    elif os.path.isfile(input_path):
        files = [input_path]
        project_name = os.path.splitext(os.path.basename(input_path))[0]  # Use file name (without extension) as project name
    else:
        print(f"Error: {input_path} is not a valid file or directory.")
        return

    # Loop through all files
    for file_path in files:
        # Skip files that are 2KB or less as they are considered failed scans
        if os.path.getsize(file_path) <= 2048:
            continue

        # Open and parse the HTML file
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'lxml')
        
        # Find the host information in the file
        host_info = soup.find('span', text=lambda x: x and 'Testing vulnerabilities' in x)
        if not host_info:
            continue

        host_name = soup.find('span', text=lambda x: x and 'Start' in x)
        if host_name:
            host_name = host_name.text.split('-->>')[1].split('<<--')[0].strip()
        
        # Gather vulnerabilities
        vulnerabilities = []
        vulnerabilities_section = soup.find('span', text=lambda x: x and 'Testing vulnerabilities' in x)
        if vulnerabilities_section:
            # Find all vulnerabilities in the section
            for vuln in vulnerabilities_section.find_all_next('span'):
                # Skip entries that explicitly state "OK", "not vulnerable", or indicate no risk
                if any(keyword in vuln.text.lower() for keyword in ['ok', 'not vulnerable', 'no risk']):
                    continue
                vulnerabilities.append(vuln.text.strip())
        
        # If there are any vulnerabilities, add them to the summary
        if vulnerabilities:
            summary[host_name] = vulnerabilities

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
        for host, vulns in summary.items():
            output.write(f'<h2>Host: {host}</h2>\n<ul>\n')
            for vuln in vulns:
                output.write(f'  <li>{vuln}</li>\n')
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
