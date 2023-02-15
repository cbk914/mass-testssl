#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914
import subprocess
import argparse
import os
import socket


def run_testssl(ip, testssl_path, output_dir):
    filename = ip.replace('/', '_').replace(':', '_')
    output_file = os.path.join(output_dir, filename + ".html")
    if os.path.isfile(output_file):
        print("Results for {} already exist".format(ip))
        return
    command = [testssl_path, "-9", "--html", ip]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = proc.stdout.readline()
        if output == b'' and proc.poll() is not None:
            break
        if output:
            try:
                print(output.decode('utf-8'), end="")
            except UnicodeDecodeError:
                print("Error decoding output from testssl.sh")
    return_code = proc.poll()
    if return_code == 0:
        with open(output_file, "w") as f:
            f.write(proc.stdout.read().decode("utf-8"))
        print("Results for {} saved to {}".format(ip, output_file))
    else:
        print("Error running testssl.sh for {}: {}".format(ip, proc.stderr.read().decode("utf-8")))


def main():
    parser = argparse.ArgumentParser(description="Script to run testssl.sh on a list of IP addresses and URLs")
    parser.add_argument("-f", "--file", dest="list_file", help="File containing IP addresses and URLs separated by newlines")
    parser.add_argument("-o", "--output", dest="output_dir", help="Output directory for testssl results")
    args = parser.parse_args()

    if not args.list_file:
        print("Please provide a list of IP addresses and URLs using the -f/--list option")
        return

    if not args.output_dir:
        args.output_dir = "output"

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    with open(args.list_file, "r") as f:
        ip_list = f.read().splitlines()

    testssl_path = None
    try:
        testssl_path = subprocess.check_output(["which", "testssl.sh"]).strip().decode("utf-8")
    except subprocess.CalledProcessError:
        pass

    if not testssl_path:
        print("Could not find testssl.sh on your system. Please install it and make sure it is in your PATH.")
        return

    for i, ip in enumerate(ip_list):
        print("[{}/{}] Running testssl on {}".format(i+1, len(ip_list), ip))
        run_testssl(ip, testssl_path, args.output_dir)


if __name__ == "__main__":
    main()
