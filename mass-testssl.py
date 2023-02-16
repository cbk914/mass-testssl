#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914
import subprocess
import argparse
import os
import socket
import validators
import ipaddress

# Parse command line arguments
parser = argparse.ArgumentParser(description='Scan a target list for SSL/TLS security vulnerabilities using testssl.sh')
parser.add_argument('-f', '--file', required=True, help='input file with IP addresses, URLs, or domain names')
parser.add_argument('-o', '--output', help='output directory for HTML reports')
args = parser.parse_args()

# Find testssl.sh on the system
testssl_path = subprocess.check_output(['which', 'testssl.sh']).strip().decode('utf-8')
default_dir = 'output_testssl'

# Initialize output directory
output_dir = os.path.join(os.getcwd(), args.output) if args.output else os.path.join(os.getcwd(), default_dir)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Process input file
ips = set()
with open(args.file, 'r') as f:
    for line in f:
        for ip in line.strip().split(','):
            ip = ip.strip()
            if '-' in ip:  # IP range detected
                start_ip, end_ip = ip.split('-')
                start_octets = start_ip.split('.')
                end_octets = end_ip.split('.')
                if len(start_octets) != 4 or len(end_octets) != 4:
                    print(f"Error: {ip} is not a valid IP range")
                    continue
                for i in range(int(start_octets[0]), int(end_octets[0])+1):
                    for j in range(int(start_octets[1]), int(end_octets[1])+1):
                        for k in range(int(start_octets[2]), int(end_octets[2])+1):
                            for l in range(int(start_octets[3]), int(end_octets[3])+1):
                                ips.add(f"{i}.{j}.{k}.{l}")
            elif '/' in ip:  # CIDR range detected
                try:
                    network = ipaddress.ip_network(ip, strict=False)
                    for addr in network.hosts():
                        ips.add(str(addr))
                except ValueError:
                    print(f"Error: {ip} is not a valid CIDR range")
                    continue
            elif validators.ipv4(ip) or validators.ipv6(ip) or validators.domain(ip) or validators.url(ip):
                ips.add(ip)
            else:
                print(f"Error: {ip} is not a valid IP address, URL, domain name, IP range, or CIDR range")

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
    else:
        open(output_file, 'a').close()

    testssl_cmd = f"{testssl_path} -9 --append --htmlfile {output_file} {ip}"
    process = subprocess.Popen(testssl_cmd, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
    process.wait()

    if process.returncode != 0:
        print(f"Error: testssl returned non-zero exit code ({process.returncode}) for {ip}")
        results[ip] = "Scan failed"
        continue
    results[ip] = "Scan successful"

# Print results report
print("\nScan results:")
for ip, result in results.items():
    print(f"{ip}: {result}")
