import requests
import sys
import threading
import os
from termcolor import colored
from colorama import Fore, init

init(autoreset=True)

def Banner():
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.LIGHTCYAN_EX + "========================================")
    print(Fore.LIGHTGREEN_EX + "        FATCAT CYBER TEAM Ft JACK007")
    print(Fore.LIGHTCYAN_EX + "========================================")
    print(Fore.LIGHTRED_EX + "                XMLRPC")
    print(Fore.LIGHTCYAN_EX + "========================================")

def check_xmlrpc_enabled(url):
    xmlrpc_endpoint = url + '/xmlrpc.php'
    
    try:
        response = requests.post(xmlrpc_endpoint, data="", timeout=15)
        if response.status_code == 200:
            return (url, "YES", "XML-RPC server accepts POST requests only.")
        else:
            return (url, "NO", "XML-RPC server doesn't accept POST requests.")
    except requests.exceptions.RequestException:
        return (url, "NO", "XML-RPC server doesn't accept POST requests.")

def process_domain(domain, save_file, lock):
    result = check_xmlrpc_enabled(domain)
    if result and result[1] == "YES":
        with lock:
            with open(save_file, "a") as f:
                f.write(domain + "\n")
    
    if result:
        status = result[1]
        message = result[2]
        color = "green" if status == "YES" else "red"
        message_color = "blue" if status == "YES" else "yellow"
        if status == "NO":
            message_color = "red"
        if status == "TIMEOUT":
            message_color = "magenta"
        result_line = f"- {colored(result[0], color)} [ {colored(status, color)} ] {colored(message, message_color)}"
        print(result_line)

def main():
    Banner() 
    input_file = input(f"{Fore.LIGHTRED_EX}[{Fore.LIGHTGREEN_EX}?{Fore.LIGHTRED_EX}] {Fore.WHITE}List? : ")
    save_file = "xmlrpc.txt"
    
    with open(input_file, "r") as f:
        raw_domains = f.read().splitlines()

    domains = ["http://" + domain if not domain.startswith("http://") and not domain.startswith("https://") else domain for domain in raw_domains]
    
    num_threads = min(len(domains), os.cpu_count() * 2)  
    lock = threading.Lock()
    
    threads = []
    for domain in domains:
        thread = threading.Thread(target=process_domain, args=(domain, save_file, lock))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
