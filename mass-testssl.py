#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914
import subprocess
import argparse
import os
import socket
import re

# Define regular expressions for validating IP addresses and URL format
IP_ADDRESS_REGEX = r'^(\d{1,3}\.){3}\d{1,3}$'
URL_REGEX = r'^(http|https)://[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)+.*$'

# Define a function to validate IP addresses
def is_valid_ip_address(ip_address):
    if not re.match(IP_ADDRESS_REGEX, ip_address):
        return False
    try:
        socket.inet_aton(ip_address)
        return True
    except socket.error:
        return False

# Define a function to validate URLs
def is_valid_url(url):
    if not re.match(URL_REGEX, url):
        return False
    return True

# Define a function to run testssl.sh for each IP address, range, and URL in the provided list file
def run_testssl(ip_list_file):
    # Read in the list of IP addresses, ranges, and URLs from the provided file
    with open(ip_list_file, 'r') as f:
        ip_list = [line.strip() for line in f]

    # Create a subdirectory for the testssl.sh output files
    output_dir = 'testssl_output'
    os.makedirs(output_dir, exist_ok=True)

    # Run testssl.sh for each IP address, range, and URL in the list
    for ip in ip_list:
        if is_valid_ip_address(ip):
            command = ['testssl.sh', '-9', '--html', ip]
        elif is_valid_url(ip):
            command = ['testssl.sh', '-9', '--html', ip]
        else:
            print(f'Invalid IP address or URL: {ip}')
            continue

        try:
            subprocess.run(command, check=True, capture_output=True, text=True, cwd=output_dir)
            print(f'Successfully ran testssl.sh for {ip}')
        except subprocess.CalledProcessError as e:
            print(f'Error running testssl.sh for {ip}: {e.stderr}')

# Define a function to parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Run testssl.sh for a list of IP addresses, ranges, and URLs')
    parser.add_argument('-l', '--list', type=str, required=True, help='Path to file containing list of IP addresses, ranges, and URLs')
    return parser.parse_args()

# Run the script
if __name__ == '__main__':
    args = parse_args()
    run_testssl(args.list)
