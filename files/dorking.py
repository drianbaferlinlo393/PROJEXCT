import requests
from bs4 import BeautifulSoup
import re
from colorama import Fore, Style, init

# Inisialisasi Colorama
init(autoreset=True)

# Fungsi untuk mengekstrak domain dari URL
def extract_domain(url):
    match = re.search(r"https?://(www\.)?([^/]+)", url)
    return match.group(2) if match else None

# Fungsi untuk scraping domain menggunakan Google Dorking
def scrape_domains(dork, max_pages=30):
    domains = set()

    print(f"{Fore.YELLOW}Mulai pencarian dengan query: {dork}{Style.RESET_ALL}")

    for page_count in range(max_pages):
        print(f"{Fore.CYAN}Mencari halaman {page_count + 1}...{Style.RESET_ALL}")
        start = page_count * 30
        url = f"https://www.google.com/search?q={dork}&start={start}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            results = soup.find_all('h3')

            if not results:
                print(f"{Fore.RED}Tidak ada hasil di halaman {page_count + 1}.{Style.RESET_ALL}")
                break

            for result in results:
                link = result.find_parent('a')['href']
                domain = extract_domain(link)
                if domain:
                    domains.add(domain)
                    print(f"{Fore.GREEN}Domain ditemukan: {domain}{Style.RESET_ALL}")

        except requests.RequestException as e:
            print(f"{Fore.RED}Kesalahan saat mengambil data dari Google: {e}{Style.RESET_ALL}")
            break

    return domains

# Fungsi untuk menyimpan domain ke file
def save_to_file(domains, filename):
    with open(filename, "w") as file:
        for domain in domains:
            file.write(domain + "\n")
    print(f"{Fore.GREEN}Domain disimpan di {filename}{Style.RESET_ALL}")

# Fungsi utama
def main():
    print(f"{Fore.YELLOW}Google Dorking Domain Scraper (Tanpa API){Style.RESET_ALL}")
    dork = input("Masukkan query Google Dorking (misalnya, inurl:login): ")
    output_file = input("Masukkan nama file output (misalnya, domains.txt): ")

    domains = scrape_domains(dork, max_pages=30)

    if domains:
        save_to_file(domains, output_file)
    else:
        print(f"{Fore.RED}Tidak ada domain yang ditemukan.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
