# mass-testssl
Python script to check with testssl all IP, ranges and URLs included on a text file

# Description

This script is a simple wrapper around the "testssl.sh" script, which allows you to scan multiple IP addresses, URLs, or domain names for SSL/TLS vulnerabilities. It takes a file as input, where each line can contain one or more comma-separated values that represent an IP address, CIDR ranges, URL, or domain names. The script then runs testssl on each address and saves the output to an HTML file. Finally, the script outputs a report of the scan results to the console.

# Instructions

* Install testssl.sh: You can download testssl.sh from its official website https://testssl.sh/ and install it on your system.

* Install required Python packages: You can install the required Python packages by running 

   pip install -r requirements.txt 

from the terminal.

* Create an input file: Create a file with a list of IP addresses, URLs, or domain names that you want to scan, with one address per line, or separated with commas all together. The addresses can be in any of the following formats: IPv4, IPv6, URL, or domain name. If you want to scan a range of IP addresses, you can use CIDR notation, e.g. 192.168.1.0/24. If you want to scan a range of IP addresses using a hyphen, e.g. 192.168.1.1-192.168.1.10, you can use a tool like fping to generate the IP list.

* Run the script. If you want to specify an output directory for the HTML reports, you can use the -o option.
 
  python mass-testssl.py -f input_file.txt -o output_dir
  
Replace "input_file.txt" with the path to the text file containing the list of IP addresses, ranges, and URLs. 

Additionally it has the -o option to select the output directory for html testssl outputs.

# References

* Testssl.sh official website: https://testssl.sh/

Thanks to Romano and Ruben for bug fixing!!
