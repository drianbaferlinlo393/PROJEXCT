#!/usr/bin/env python3
# Author: Maxim3lian

import requests
import os
import re
from multiprocessing.dummy import Pool as ThreadPool
from colorama import Fore, Style, init

init(autoreset=True)

banner = f"""
{Fore.YELLOW}{'='*40}
        {Fore.CYAN}{Style.BRIGHT}FATCAT CYBER TEAM Ft JACK007
{Fore.YELLOW}{'='*40}
                {Fore.GREEN}Reverse IP
{Fore.YELLOW}{'='*40}
"""

def rapid_dns(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/60.0.3112.107 Mobile Safari/537.36'
        }
        x = requests.get('https://rapiddns.io/sameip/'+url+'?full=1&down=1#result/', headers=headers, timeout=30).text
        if '<th scope="row ">' in x:
            regex = re.findall('<td>(?!\-)(?:[a-zA-Z\d\-]{0,62}[a-zA-Z\d]\.){1,126}(?!\d+)[a-zA-Z]{1,63}</td>', x)
            for domain_name in regex:
                website_url = 'http://' + domain_name.replace('<td>', '').replace('</td>', '').replace('ftp.', '').replace('images.', '').replace('cpanel.', '').replace('cpcalendars.', '').replace('cpcontacts.', '').replace('webmail.', '').replace('webdisk.', '').replace('hostmaster.', '').replace('mail.', '').replace('ns1.', '').replace('ns2.', '').replace('autodiscover.', '')
                print("GRABBED: {}".format(website_url))
                with open('Reversed.txt', 'a') as file:
                    file.write(website_url + '\n')
        else:
            print("BAD : " + url)
    except Exception as e:
        print(f"Error with {url}: {e}")

def reverse_ip_lookup(url):
    try:
        rapid_dns(url)
    except Exception as e:
        print(f"Failed to lookup {url}: {e}")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(banner)  # Display the banner
    try:
        ip_list = input("IPS LIST : ")
        with open(ip_list, 'r') as file:
            urls = file.read().splitlines()
        num_threads = input("THREAD : ")
        pool = ThreadPool(int(num_threads))
        pool.map(reverse_ip_lookup, urls)
        pool.close()
        pool.join()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
