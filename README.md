# mass-testssl
Python script to check with testssl all IP, ranges and URLs included on a text file

# Description

The Python script is designed to automate the execution of testssl.sh for a list of IP addresses, ranges, and URLs, and produce HTML reports for each one. The script takes a list of IP addresses, ranges, and URLs in a text file as input, validates them, and executes testssl.sh with the provided arguments for each IP. The output of testssl.sh is displayed in real-time on the console, and the HTML reports are saved to a subdirectory.

# Instructions

* Install testssl.sh by following the instructions on the GitHub repository: https://github.com/drwetter/testssl.sh
* Save a list of IP addresses, ranges, and URLs to a text file (one per line) in the format "IP_ADDRESS_OR_URL[,IP_ADDRESS_OR_URL...]".
* Run the Python script using the command 
  python testssl_script.py -f PATH_TO_IP_LIST_FILE 
  
Replace "PATH_TO_IP_LIST_FILE" with the path to the text file containing the list of IP addresses, ranges, and URLs. 
