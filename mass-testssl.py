#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914
import subprocess
import argparse
import os
import socket
import sys

def main():
    parser = argparse.ArgumentParser(description='testssl.sh script.')
    parser.add_argument('-f', '--file', help='File with the list of IP, Ranges or URLs.')
    parser.add_argument('-o', '--output', default='output', help='Output directory for testssl.sh scan results')
    args = parser.parse_args()

    if not args.file:
        print('Please provide a file with the -f option.')
        sys.exit(1)

    with open(args.file) as f:
        content = f.read()

    # Filter out empty lines and duplicates
    ips = set(filter(None, (ip.strip() for ip in content.split(','))))

    # Get testssl.sh path
    try:
        testssl_path = subprocess.check_output(['which', 'testssl.sh']).decode().strip()
    except subprocess.CalledProcessError:
        print('Unable to find testssl.sh on the system.')
        sys.exit(1)

    progress = 0
    total = len(ips)
    for ip in ips:
        try:
            socket.inet_aton(ip)
        except socket.error:
            print(f'Invalid IP address or hostname: {ip}')
            continue

        # Run testssl.sh on the IP
        command = f'{testssl_path} -9 --html {ip}'
        try:
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        except OSError:
            print(f'Unable to execute command: {command}')
            continue

        # Print output while the process is running
        while proc.poll() is None:
            output = proc.stdout.readline().decode('utf-8', errors='replace')
            if output:
                if 'testssl.sh' in output:
                    # Ignore testssl.sh version output
                    continue
                elif ' 100.00%' in output:
                    # Ignore final output lines
                    continue
                else:
                    print(output.strip())

                    # Update progress
                    progress += 1
                    percent_complete = round(progress / total * 100, 2)
                    print(f'Progress: {percent_complete}%')

        # Print any remaining output
        for output in proc.stdout.readlines():
            if output:
                if 'testssl.sh' in output:
                    # Ignore testssl.sh version output
                    continue
                elif ' 100.00%' in output:
                    # Ignore final output lines
                    continue
                else:
                    print(output.decode('utf-8', errors='replace').strip())

                    # Update progress
                    progress += 1
                    percent_complete = round(progress / total * 100, 2)
                    print(f'Progress: {percent_complete}%')

if __name__ == '__main__':
    main()
