#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914
#!/usr/bin/env python3

import subprocess
import argparse
import os
import socket

# Parse command line arguments
parser = argparse.ArgumentParser(description='Scan for SSL/TLS security vulnerabilities using testssl.sh')
parser.add_argument('-f', '--file', required=True, help='input file with IP addresses or URLs')
parser.add_argument('-o', '--output', help='output directory for HTML reports')
args = parser.parse_args()

# Find testssl.sh on the system
testssl_path = subprocess.check_output(['which', 'testssl.sh']).strip().decode('utf-8')

# Initialize output directory
if args.output:
    output_dir = args.output
else:
    output_dir = os.getcwd()

# Process input file
ips = set()
with open(args.file, 'r') as f:
    for line in f:
        for ip in line.strip().split(','):
            ips.add(ip.strip())

# Initialize results report
results = {}

# Scan each IP with testssl
for i, ip in enumerate(ips):
    print(f"Scanning IP {ip} ({i+1}/{len(ips)})...")
    # Check if IP is valid
    try:
        socket.inet_aton(ip)
    except socket.error:
        print(f"Error: {ip} is not a valid IP address")
        results[ip] = "Invalid IP address"
        continue
    # Run testssl on IP
    output_file = os.path.join(output_dir, f"testssl_{ip.replace('.', '_')}.html")
    if os.path.isfile(output_file):
        print(f"Skipping IP {ip}: already scanned")
        results[ip] = "Already scanned"
        continue
    testssl_cmd = f"{testssl_path} -9 --html {ip} > {output_file}"
    process = subprocess.Popen(testssl_cmd, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
    output = ""
    while True:
        line = process.stdout.readline()
        if not line:
            break
        print(line, end='')
        output += line
    process.wait()
    # Check for errors
    if process.returncode != 0:
        print(f"Error: testssl returned non-zero exit code ({process.returncode}) for IP {ip}")
        results[ip] = "Scan failed"
        continue
    results[ip] = "Scan successful"

# Print results report
print("\nScan results:")
for ip, result in results.items():
    print(f"{ip}: {result}")
