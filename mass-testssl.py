#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914
import subprocess
import argparse
import os
import socket


def parse_ips(ips_file):
    with open(ips_file, 'r') as f:
        ips = f.read()
    ips = ips.replace('\n', ',')
    ips = ips.replace(' ', ',')
    ips = ips.strip(',')
    ips = ips.split(',')
    ips = list(set(ips))
    return ips


def run_testssl(ip, testssl_path, output_path):
    print(f"Scanning {ip}...")
    cmd = f"{testssl_path} -9 --html {ip} > {output_path}/{ip}.html"
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Finished scanning {ip}.")


def main():
    parser = argparse.ArgumentParser(description='Scan IPs with testssl.sh')
    parser.add_argument('-f', '--file', dest='ips_file', required=True, help='Text file containing list of IPs to scan')
    parser.add_argument('-t', '--testssl', dest='testssl_path', default='testssl.sh', help='Path to testssl.sh')
    parser.add_argument('-o', '--output', dest='output_path', default='output', help='Output directory for HTML results')
    args = parser.parse_args()

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    ips = parse_ips(args.ips_file)

    results = []
    for ip in ips:
        try:
            run_testssl(ip, args.testssl_path, args.output_path)
            results.append((ip, 'SUCCESS'))
        except Exception as e:
            print(f"Failed to scan {ip}. Error message: {str(e)}")
            results.append((ip, 'FAILED'))

    print("\n=== Scan Results ===")
    for ip, result in results:
        print(f"{ip}: {result}")


if __name__ == '__main__':
    main()
