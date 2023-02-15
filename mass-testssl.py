#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914
import subprocess
import argparse
import os
import socket
import ipaddress
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser(description='Automate testssl.sh scans on multiple IP addresses')
    parser.add_argument('-f', '--file', required=True, help='Text file containing a list of IP addresses and URLs')
    parser.add_argument('-o', '--output', default='output', help='Output directory for testssl.sh scan results')
    return parser.parse_args()


def scan_ips(ip_list, output_dir):
    unique_ips = set(ip_list)  # create a set of unique IP addresses
    for ip in tqdm(unique_ips, desc='Scanning', unit='IP'):
        # validate the IP address
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            print(f'Invalid IP address: {ip}')
            continue

        # execute testssl.sh with the IP address and output directory
        output_file = os.path.join(output_dir, f'{ip}.html')
        cmd = f'testssl.sh -9 --html --file {output_file} {ip}'
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            print(f'Error scanning IP {ip}: {e.stderr}')


def main():
    args = parse_args()

    # create the output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # read the list of IP addresses and URLs from the input file
    with open(args.file, 'r') as f:
        ip_list = []
        for line in f:
            line = line.strip()
            if line:
                for delimiter in [',', ';', ' ']:  # add any other delimiters you want to support
                    if delimiter in line:
                        parts = line.split(delimiter)
                        ip_list.extend(parts)
                        break
                else:
                    ip_list.append(line)

    # scan the IP addresses using testssl.sh
    scan_ips(ip_list, args.output)


if __name__ == '__main__':
    main()
