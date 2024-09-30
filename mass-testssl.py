#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914

import subprocess
import argparse
import os
import ipaddress
import logging
from urllib.parse import urlparse

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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

def is_ip_with_port(s):
    try:
        ip, port = s.split(':')
        ipaddress.ip_address(ip.strip())
        return port.isdigit() and 1 <= int(port) <= 65535
    except ValueError:
        return False

def find_testssl():
    try:
        return subprocess.check_output(['which', 'testssl.sh']).strip().decode('utf-8')
    except subprocess.CalledProcessError:
        logging.error("Error: testssl.sh not found in PATH. Please ensure that testssl.sh is installed and available in your PATH.")
        exit(1)

def initialize_output_directory(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def parse_input_file(input_file):
    ips = set()
    with open(input_file, 'r') as f:
        for line in f:
            for ip in line.strip().split(','):
                ip = ip.strip()
                if is_ip_with_port(ip):
                    ips.add(ip)
                elif validators.ipv4(ip) or validators.ipv6(ip) or validators.domain(ip) or validators.url(ip):
                    ips.add(ip)
                elif '-' in ip:  # IP range potentially detected
                    if is_valid_ip_range(ip):
                        start_ip, end_ip = ip.split('-')
                        start_ip = ipaddress.ip_address(start_ip.strip())
                        end_ip = ipaddress.ip_address(end_ip.strip())
                        for ip_int in range(int(start_ip), int(end_ip) + 1):
                            ips.add(str(ipaddress.ip_address(ip_int)))
                    else:
                        logging.error(f"Error: {ip} is not a valid IP range")
                elif '/' in ip:  # CIDR range detected
                    try:
                        network = ipaddress.ip_network(ip, strict=False)
                        for addr in network.hosts():
                            ips.add(str(addr))
                    except ValueError:
                        logging.error(f"Error: {ip} is not a valid CIDR range")
                else:
                    logging.error(f"Error: {ip} is not a valid IP address, URL, domain name, IP range, or CIDR range")
    return ips

def scan_with_testssl(ip, testssl_path, output_dir):
    # Adjust the output filename to handle "IP:port"
    safe_ip = ip.replace('.', '_').replace(':', '_')
    output_file = os.path.join(output_dir, f"{safe_ip}.html")

    if os.path.isfile(output_file):
        logging.info(f"Skipping {ip}: already scanned")
        return ip, "Already scanned"

    testssl_cmd = f"{testssl_path} -9 --append --htmlfile {output_file} {ip}"
    process = subprocess.Popen(testssl_cmd, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
    process.wait()

    if process.returncode != 0:
        logging.error(f"Error: testssl returned non-zero exit code ({process.returncode}) for {ip}")
        return ip, "Scan failed"

    return ip, "Scan successful"

def main():
    parser = argparse.ArgumentParser(description='Scan a target list for SSL/TLS security vulnerabilities using testssl.sh')
    parser.add_argument('-f', '--file', required=True, help='Input file with IP addresses, URLs, or domain names')
    parser.add_argument('-o', '--output', default='testssl_output', help='Output directory for HTML reports (default: testssl_output)')
    args = parser.parse_args()

    testssl_path = find_testssl()
    output_dir = initialize_output_directory(args.output)
    ips = parse_input_file(args.file)

    results = {}
    for i, ip in enumerate(ips):
        logging.info(f"Scanning {ip} ({i+1}/{len(ips)})...")
        ip, result = scan_with_testssl(ip, testssl_path, output_dir)
        results[ip] = result

    logging.info("\n-----------------\n+ Scan results: +\n-----------------")
    for ip, result in results.items():
        logging.info(f"{ip}: {result}")

if __name__ == "__main__":
    main()
