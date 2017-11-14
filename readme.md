ddns_update.py
Written by Nicholas Hill <njhill@mix.wvu>.

This script uses GoDaddys API to change the A DNS record to point to the current machine.
This script was made to be placed into the crontab to allow dnyamic DNS functionality through GoDaddy.

optional arguments:

-h, --help                      show this help message and exit
--key key, -k key               GoDaddy API key
--secret secret, -s secret      GoDaddy API secret
--domain domain, -d             Domain name registered with GoDaddy
--verbose, -v                   Verbose output for debugging   
