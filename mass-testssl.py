#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914
import subprocess
import argparse
import os
import socket
import validators
import ipaddress


def is_valid_ip_range(ip_range: str) -> bool:
    if '-' not in ip_range:
        return False
    
    start_ip, end_ip = ip_range.split('-')
    
    try:
        start_ip = ipaddress.ip_address(start_ip.strip())
        end_ip = ipaddress.ip_address(end_ip.strip())
    except ValueError:
        return False
    
    return start_ip.version == end_ip.version and start_ip <= end_ip

def is_url_with_port(s):
    if ":" in s and "." in s:
        parts = s.split(":")
        if len(parts) == 2:
            if validators.domain(parts[0]) and parts[1].isdigit():
                return True
    return False

# Parse command line arguments
parser = argparse.ArgumentParser(description='Scan a target list for SSL/TLS security vulnerabilities using testssl.sh')
parser.add_argument('-f', '--file', required=True, help='input file with IP addresses, URLs, or domain names')
parser.add_argument('-o', '--output', help='output directory for HTML reports')
args = parser.parse_args()

# Find testssl.sh on the system
try:
    testssl_path = subprocess.check_output(['which', 'testssl.sh']).strip().decode('utf-8')
except subprocess.CalledProcessError:
    print("Error: testssl.sh not found in PATH. Please ensure that testssl.sh is installed and available in your PATH.")
    exit(1)

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
            if validators.ipv4(ip) or validators.ipv6(ip) or validators.domain(ip) or validators.url(ip) or is_url_with_port(ip):
                ips.add(ip)
            elif '-' in ip:  # IP range potentially detected
                ip_split = ip.split('-')
                if len(ip_split) == 2:
                    try:
                        start_ip = ipaddress.ip_address(ip_split[0].strip())
                        end_ip = ipaddress.ip_address(ip_split[1].strip())
                        for ip_int in range(int(start_ip), int(end_ip) + 1):
                            ips.add(str(ipaddress.ip_address(ip_int)))
                    except ValueError:
                        print(f"Error: {ip} is not a valid IP range")
                        continue
                else:
                    print(f"Error: {ip} is not a valid IP range")
                    continue
            elif '/' in ip:  # CIDR range detected
                try:
                    network = ipaddress.ip_network(ip, strict=False)
                    for addr in network.hosts():
                        ips.add(str(addr))
                except ValueError:
                    print(f"Error: {ip} is not a valid CIDR range")
                    continue
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
print("\n-----------------")
print("\n+ Scan results: +")
print("\n-----------------")
for ip, result in results.items():
    print(f"{ip}: {result}")
