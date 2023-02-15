#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914
import subprocess
import argparse
import os
import socket


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='input text file with IPs or URLs')
    parser.add_argument('-o', '--output', help='output directory for HTML results')
    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r') as f:
            ips_urls = f.read().replace('\n', ',').replace(' ', '').split(',')
    else:
        parser.error('Please specify an input text file with -f.')

    if args.output:
        output_dir = args.output
    else:
        output_dir = os.getcwd() + '/output'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    processed_ips_urls = set()

    for ip_url in ips_urls:
        if ip_url not in processed_ips_urls:
            processed_ips_urls.add(ip_url)
            try:
                ip = socket.gethostbyname(ip_url)
            except socket.gaierror:
                print(f'Invalid IP or URL: {ip_url}')
                continue

            cmd = ['testssl.sh', '-9', '--html', ip]
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = proc.communicate()
                if error:
                    print(error.decode('utf-8'))
                else:
                    print(output.decode('utf-8'))

                output_path = os.path.join(output_dir, f'{ip}.html')
                with open(output_path, 'wb') as f:
                    f.write(output)
            except subprocess.CalledProcessError:
                print(f'Error running testssl.sh on {ip_url}')

if __name__ == '__main__':
    main()
