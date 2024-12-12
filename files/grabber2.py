import subprocess
import requests
import time
import dns.resolver
from colorama import Fore, Style, init
import re

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

def find_subdomains_with_subfinder(domain):
    """Menggunakan Subfinder untuk mencari subdomain yang tersedia."""
    try:
        print(f"[+] Grabbing subdomains for: {domain}")
        result = subprocess.run(['subfinder', '-d', domain, '-silent'], capture_output=True, text=True)

        # Memeriksa jika ada error dalam menjalankan Subfinder
        if result.returncode != 0:
            print(f"[{red}Error{clear}] Failed to run Subfinder: {result.stderr}")
            return []

        # Menyimpan subdomain yang ditemukan
        subdomains = result.stdout.splitlines()
        return subdomains

    except Exception:
        # Tidak mencetak pesan kesalahan
        return []

def ensure_http(url):
    """Tambahkan http:// atau https:// jika belum ada."""
    return f"http://{url}" if not url.startswith(("http://", "https://")) else url

def save_to_file(filename, url):
    """Simpan hasil ke file tanpa skema atau www."""
    # Menghapus skema dan prefiks www
    cleaned_url = url.replace("http://", "").replace("https://", "").replace("www.", "")
    with open(filename, "a") as file:
        file.write(cleaned_url + "\n")

def is_valid_url(url):
    """Memeriksa apakah URL valid atau tidak."""
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # Skema http atau https
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # Domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # IP
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # IPv6
        r'(?::\d+)?'  # Port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def scan_cms(url):
    """Scan CMS untuk URL tertentu dan simpan hasilnya."""
    cms_found = False
    try:
        if not is_valid_url(url):
            print(f"[{red}Error{clear}] Invalid URL: {url}")
            return
        
        cms_response = requests.get(url, timeout=5, allow_redirects=True)
        
        # Tangani pengalihan
        if cms_response.history:
            for resp in cms_response.history:
                if resp.status_code in [301, 302]:
                    print(f"[{yellow}Redirected{clear}] {url} -> {cms_response.url}")
        
        for cms, keywords in cms_dict.items():
            if any(keyword in cms_response.text for keyword in keywords):
                cms_found = True
                print(f"[{yellow}*{clear}] {url} [ {yellow}{cms} Detected{clear} ]")
                save_to_file(f"{cms.lower()}.txt", url)
                break
        
        if not cms_found:
            print(f"[{yellow}*{clear}] {url} [ {red}No CMS Detected{clear} ]")
            save_to_file("no_cms_detected.txt", url)

    except requests.RequestException as e:
        return

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
            # Tidak mencetak pesan kesalahan
            time.sleep(2)
    # Tidak mencetak pesan kesalahan jika semua percobaan gagal
    return None

print(yellow + "[==============================]")
print(yellow + "   Priv8 Domain Grabber, Subfinder & CMS Scanner")
print(yellow + "   Version  : 1.0")
print(yellow + "   Fatcat Cyber ft Jack007")
print(yellow + "[==============================]")

# Input untuk domain
tld = input("Input TLD (e.g., ac.id): ")
output_file = input("Input Output File Name (e.g., output.txt): ")

# Mencari domain dengan TLD yang diberikan
domains = search_domains(tld)

# Temukan subdomain dan scan CMS untuk setiap domain
for domain in domains:
    print(f"[{yellow}+{clear}] Grabbing: {domain}")
    
    # Temukan subdomain menggunakan Subfinder
    subdomains = find_subdomains_with_subfinder(domain)
    all_domains = [domain] + subdomains

    # Scan CMS untuk domain dan subdomain
    for result in all_domains:
        url = ensure_http(result)
        scan_cms(url)

print("Grabbing completed!")
print(f"Results saved to {output_file}")
print(clear)
