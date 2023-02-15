#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914
import subprocess
import argparse
import os
import socket

def run_testssl(ip_list_file):
    # Check if the input file exists and is a file
    if not os.path.isfile(ip_list_file):
        print(f"Input file '{ip_list_file}' does not exist or is not a file")
        return

    # Read in the list of IP addresses, ranges, and URLs from the provided file
    with open(ip_list_file, 'r') as f:
        ip_list = [line.strip() for line in f]

    # Filter out any empty or commented lines
    ip_list = [line for line in ip_list if line and not line.startswith('#')]

    # Create a subdirectory for the testssl.sh output files
    output_dir = 'testssl_output'
    os.makedirs(output_dir, exist_ok=True)

    # Get the total number of IP addresses, ranges, and URLs in the list
    total_ips = len(ip_list)

    # Run testssl.sh for each IP address, range, and URL in the list
    for index, ip in enumerate(ip_list):
        # Split the line on commas to handle CSV format
        ips = [i.strip() for i in ip.split(',')]

        # Validate each IP address or URL in the list
        for i in ips:
            # Skip empty or invalid IP addresses or URLs
            try:
                socket.getaddrinfo(i, None, socket.AF_INET)
            except socket.gaierror:
                print(f"Invalid IP address or URL: {i}")
                continue

            # Build the testssl.sh command for the current IP address or URL
            command = ['testssl.sh', '-9', '--html', i]

            # Run testssl.sh for the current IP address or URL
            print(f"Running testssl.sh for {i}... ({round((index + 1) / total_ips * 100, 2)}%)")
            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=output_dir)

                if result.returncode == 0:
                    print(f"Successfully ran testssl.sh for {i}")
                else:
                    print(f"Error running testssl.sh for {i}: {result.stderr}")
            except subprocess.CalledProcessError as e:
                print(f"Error running testssl.sh for {i}: {e.stderr}")
            except Exception as e:
                print(f"Unknown error running testssl.sh for {i}: {e}")

def parse_args():
    parser = argparse.ArgumentParser(description="Run testssl.sh for a list of IP addresses, ranges, and URLs")
    parser.add_argument("-f", "--file", type=str, required=True, help="Path to file containing list of IP addresses, ranges, and URLs")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run_testssl(args.file)

