#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914
import subprocess
import argparse
import os
import socket

# Function to check if an IP address is valid
def is_valid_ip(ip):
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except socket.error:
        return False

# Function to check if a URL is valid
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# Parse command line arguments
parser = argparse.ArgumentParser(description='Scan IPs and URLs with testssl.sh')
parser.add_argument('-f', '--file', help='Input file containing IPs and URLs')
args = parser.parse_args()

# Check if input file was provided
if not args.file:
    parser.error('Please provide an input file using the -f option')

# Get the absolute path of the testssl.sh script
testssl_path = subprocess.check_output('which testssl.sh', shell=True, encoding='utf-8').strip()

# Read input file
with open(args.file, 'r') as f:
    lines = f.readlines()

# Initialize list to keep track of scanned IPs and URLs
scanned = []

# Loop through lines in the input file
for i, line in enumerate(lines):
    # Strip whitespace from the line
    line = line.strip()
    
    # Split line into individual IPs and URLs
    addrs = [addr.strip() for addr in line.split(',')]

    # Loop through IPs and URLs in the line
    for addr in addrs:
        # Check if the IP or URL has already been scanned
        if addr in scanned:
            continue
        
        # Add the IP or URL to the list of scanned addresses
        scanned.append(addr)

        # Check if the address is a valid IP
        if is_valid_ip(addr):
            print(f'Scanning IP address: {addr}')
        # Check if the address is a valid URL
        elif is_valid_url(addr):
            print(f'Scanning URL: {addr}')
        else:
            print(f'Invalid address: {addr}')
            continue

        # Run testssl.sh on the address
        command = f'{testssl_path} -9 --html {addr}'
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='latin-1')

        # Initialize variables to keep track of progress
        total_lines = 0
        lines_read = 0

        # Loop through the output of testssl.sh
        for line in iter(process.stdout.readline, ''):
            # Count the total number of lines in the output
            if not total_lines:
                total_lines = len(line)
                print(f'Total lines: {total_lines}')
            
            # Replace non-ASCII characters with a placeholder
            line = ''.join([c if ord(c) < 128 else '?' for c in line])
            
            # Print the line
            print(line.strip())

            # Increment the number of lines read
            lines_read += 1

            # Print the progress
            progress = int((lines_read/total_lines)*100)
            print(f'Progress: {progress}%')

        # Print any errors
        for line in iter(process.stderr.readline, ''):
            print(line.strip())

        # Wait for the process to finish
        process.wait()

