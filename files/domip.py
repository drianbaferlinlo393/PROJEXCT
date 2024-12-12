import socket
from colorama import Fore, Style, init

banner = f"""
{Fore.YELLOW}{'='*40}
        {Fore.CYAN}{Style.BRIGHT}FATCAT CYBER TEAM Ft JACK007
{Fore.YELLOW}{'='*40}
                {Fore.GREEN}Domain To IP
{Fore.YELLOW}{'='*40}
"""

def domain_to_ip(domain, output_file):
    try:
        ip_address = socket.gethostbyname(domain)
        print(f"Domain: {domain} -> IP: {ip_address}")
        with open(output_file, 'a') as file:
            file.write(f"{ip_address}\n")
    except socket.gaierror:
        print(f"Error: Tidak dapat menemukan IP untuk domain {domain}")

def read_domains_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            domains = [line.strip() for line in file.readlines() if line.strip()]
        return domains
    except FileNotFoundError:
        print(f"Error: File {file_path} tidak ditemukan.")
        return []

if __name__ == "__main__":
    # Tampilkan banner
    print(banner)
    
    # Input file path
    file_path = input("Masukan List Domain: ")
    
    # Baca daftar domain dari file
    domains = read_domains_from_file(file_path)

    # Nama file hasil IP
    output_file = 'ip_result.txt'

    # Ubah domain menjadi IP dan simpan hanya IP ke ip_result.txt
    for domain in domains:
        domain_to_ip(domain, output_file)

    print(f"Alamat IP disimpan di {output_file}")
