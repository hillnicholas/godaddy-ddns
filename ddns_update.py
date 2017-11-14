#!/usr/bin/env python

import requests, re, argparse, sys

# ddns_update.py
# Written by Nicholas Hill <njhill@mix.wvu.edu>
# This python script will update an A record for a server that uses GoDaddy to manage DNS.
# Place this script in your cron tab. You will need an API key and secret (free)
#
# dependencies: requests


# Globals are defined here. 
USE_GLOBALS = False                             # set to True to use defined variables below
KEY = None 	                                # api key
SECRET = None           			# api secret 
DOMAIN = "example.com"				# This is the domain name 
VERBOSE = False					# simple verbose flag
PUBLIC_IP_LINK = "http://icanhazip.com"		# This website is used to get the local server's public IP 


# verbose mode 
def verbose( msg ):
	if VERBOSE: print str( msg )
	
	
# Returns the current DNS records in json format.
def get_DNS_entry():
	resp = requests.get("https://api.godaddy.com/v1/domains/" + DOMAIN + "/records", headers = headers ).json();
	return resp


# get your current public IP address, via icanhazip.com
def get_current_public_ip_addr():
	resp = requests.get( PUBLIC_IP_LINK ).text.encode("utf-8").replace("\n","")
	if re.match( "^(?:[0-9]{1,3}.){3}[0-9]{1,3}$" , resp ):
		return resp

	
# extract the A record IP address from a JSON response
def get_A_record_ip( entry ):
	A_record_ip = None
	for record in entry:
		if record["type"] == "A" and record["name"] == "@":
			A_record_ip = record["data"]
	return A_record_ip


# simple loop to replace the A record DNS entry 	
def replace_A_record_ip( entry, ip_addr ):
	for record in entry:
		if record["type"] == "A" and record["name"] == "@":
			record["data"] = ip_addr
	return entry 

		
# push the DNS entry to the server
def push_DNS_entry( entrydata ):
	# send record depending on public IP
	resp = requests.put( "https://api.godaddy.com/v1/domains/" + DOMAIN + "/records",
		headers = headers,
		json= entrydata );
	return resp


# simple print wrapper for failing parse_args()
def fail( error_msg, parser ):
	sys.stderr.write(error_msg + "\n\n" )
	parser.print_help()
	exit(1)
	
# define variables for use in the script
def parse_args():
	
	parser = argparse.ArgumentParser(description='Update GoDaddy entries to point an A record to your current public IP.')
	
	parser.add_argument('--key', '-k', metavar='key', type=str,
                    help='GoDaddy API key')
					
	parser.add_argument('--secret', '-s', metavar='secret', type=str,
                    help='GoDaddy API secret')

	parser.add_argument('--domain', '-d', metavar='domain', type=str,
                    help='Domain name registered with GoDaddy')
					
	parser.add_argument('--verbose', '-v', action="store_true",
                    help='Verbose output for debugging')
		
	p = parser.parse_args()
	
	global VERBOSE, KEY, SECRET, DOMAIN
	
	# handle error messages and define variables
	DOMAIN = p.domain if p.domain != None else fail("Error: no domain specified", parser)
	SECRET = p.secret if p.secret != None else fail("Error: no API secret provided", parser)
	KEY = p.key	if p.key != None else fail("Error: no API key provided", parser)
	# verbose flag doesn't kill the script
	VERBOSE = bool( p.verbose  )
	
	

if __name__ == "__main__":
	# see if global settings have been configured in-script
	if not USE_GLOBALS:
		parse_args()

	headers = { "Authorization": "sso-key " + KEY + ":" + SECRET }
	# get public IP address
	public_ip = get_current_public_ip_addr()
	verbose( "Public IP: '" + str(public_ip) +"'" )
	
	# get current DNS entry using the specified globals
	current_DNS_entry = get_DNS_entry()	
	verbose( "Current DNS entry: " + str(current_DNS_entry) )
	
	# get the current A record IP from the retrieved DNS entry 
	current_DNS_A_record_ip = get_A_record_ip( current_DNS_entry )
	verbose( "Current DNS A record IP: " + str(current_DNS_A_record_ip) )

	# check to see if the DNS A record IP address doesn't match the server's current IP address
	if public_ip != current_DNS_A_record_ip:
		# update the DNS entry locally, don't modify any other records other than A record
		updated_DNS_entry = replace_A_record_ip( current_DNS_entry , public_ip )			
		verbose( "Updated DNS entry: " + str(updated_DNS_entry) )
		
		# push the changes to the server
		response = push_DNS_entry( updated_DNS_entry )
		
		# print, if error
		if VERBOSE or not response.ok:
			print str(response)
			print str(response.text) 
		
	else:
                verbose("Not updating, entry is correct")
