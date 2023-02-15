#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914
import subprocess
import argparse
import os
import socket
import validators

# Parse command line arguments
parser = argparse.ArgumentParser(description='Scan a target list for SSL/TLS security vulnerabilities using testssl.sh')
parser.add_argument('-f', '--file', required=True, help='input file with IP addresses, URLs, or domain names')
args = parser.parse_args()

# Find testssl.sh on the system
testssl_path = subprocess.check_output(['which', 'testssl.sh']).strip().decode('utf-8')

# Initialize output directory
if args.output:
    output_dir = args.output
else:
    output_dir = os.path.join(os.getcwd(), 'output_testssl')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

# Process input file
ips = set()
with open(args.file, 'r') as f:
    for line in f:
        for ip in line.strip().split(','):
            ip = ip.strip()
            if validators.ipv4(ip) or validators.ipv6(ip) or validators.domain(ip) or validators.url(ip):
                ips.add(ip)
            else:
                print(f"Error: {ip} is not a valid IP address, URL, or domain name")

# Initialize results report
results = {}

# Scan each IP with testssl
for i, ip in enumerate(ips):
    print(f"Scanning {ip} ({i+1}/{len(ips)})...")
    # Check if IP is valid
    try:
        socket.inet_aton(ip)
    except socket.error:
        pass  # Not an IP address
    # Run testssl on IP
    output_file = os.path.join(output_dir, f"{ip.replace('.', '_')}.html")
    if os.path.isfile(output_file):
        print(f"Skipping {ip}: already scanned")
        results[ip] = "Already scanned"
        continue
    testssl_cmd = f"{testssl_path} -9 --html {ip}"
    process = subprocess.Popen(testssl_cmd, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
    output = ""
    for line in process.stdout:
        print(line, end='')
        output += line
    process.wait()
    # Write output to file
    with open(output_file, 'w') as f:
        f.write(output)
    # Check for errors
    if process.returncode != 0:
        print(f"Error: testssl returned non-zero exit code ({process.returncode}) for {ip}")
        results[ip] = "Scan failed"
        continue
    results[ip] = "Scan successful"

# Print results report
print("\nScan results:")
for ip, result in results.items():
    print(f"{ip}: {result}")
