import os
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init

# Inisialisasi Colorama
init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.GREEN}{Style.BRIGHT}[==============================]
{Fore.GREEN}{Style.BRIGHT}|                              |
{Fore.CYAN}{Style.BRIGHT}|      Priv8 Subdomain         |
{Fore.YELLOW}{Style.BRIGHT}|         Finder v5.0          |
{Fore.BLUE}{Style.BRIGHT}|      Fatcat Cyber Team       |
{Fore.RED}{Style.BRIGHT}|         Ft Jack007           |
{Fore.GREEN}{Style.BRIGHT}|                              |
{Fore.GREEN}{Style.BRIGHT}[==============================]
    """
    print(banner)

def print_separator():
    print(f"{Fore.MAGENTA}{Style.BRIGHT}{'-'*74}")

def find_subdomains(domain, output_file):
    print(f"{Fore.WHITE}[{Fore.CYAN}>{Fore.WHITE}] {Fore.WHITE}Mencari Subdomain {Fore.YELLOW}{domain}")
    
    # Jalankan subfinder untuk menemukan subdomain
    result = subprocess.run(['subfinder', '-d', domain], capture_output=True, text=True)
    
    # Simpan hasil ke file output secara real-time
    if result.stdout:
        with open(output_file, 'a') as f_out:
            f_out.write(result.stdout)
        print(f"{Fore.WHITE}[{Fore.GREEN}+{Fore.WHITE}] {Fore.WHITE}Hasil untuk {Fore.YELLOW}{domain} {Fore.GREEN}telah disimpan.")
    
    # Cetak pemisah setelah selesai mencari subdomain
    print_separator()

def main():
    # Tampilkan banner
    print_banner()

    # Meminta input nama file input dan output
    input_file = input(f"{Fore.CYAN}Masukkan nama file input (misalnya: {Fore.YELLOW}domains.txt{Fore.CYAN}): ")
    output_file = f"subdo.{input_file}"  # Otomatis membuat nama output

    try:
        # Membaca daftar domain dari file input
        with open(input_file, 'r') as f:
            domains = [line.strip() for line in f.readlines()]

        # Menggunakan ThreadPoolExecutor untuk mencari subdomain secara paralel
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(find_subdomains, domain, output_file): domain for domain in domains}

            for future in as_completed(futures):
                domain = futures[future]
                try:
                    future.result()  # Menjalankan fungsi untuk setiap domain
                except Exception as e:
                    print(f"{Fore.RED}Terjadi kesalahan saat mencari {domain}: {e}")

        print(f"{Fore.GREEN}{Style.BRIGHT}Hasil subdomain telah disimpan di: {Fore.YELLOW}{output_file}")

    except FileNotFoundError:
        print(f"{Fore.RED}File input tidak ditemukan. Pastikan nama file benar.")
    except Exception as e:
        print(f"{Fore.RED}Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
