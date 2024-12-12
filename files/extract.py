import re
import os

def extract_domains_from_file(input_file, output_file):
    # Cek apakah file input ada
    if not os.path.exists(input_file):
        print(f"File {input_file} tidak ditemukan.")
        return

    try:
        # Membaca file input
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
    except IOError as e:
        print(f"Kesalahan saat membaca file: {e}")
        return

    domains = []
    for line in lines:
        # Ekspresi reguler untuk mengekstrak domain
        match = re.search(r'https?://([^/]+)', line)
        if match:
            domains.append(match.group(1))

    try:
        # Menyimpan hasil ke file output
        with open(output_file, 'w', encoding='utf-8') as file:
            for domain in domains:
                file.write(domain + '\n')
    except IOError as e:
        print(f"Kesalahan saat menulis file: {e}")

if __name__ == "__main__":
    # Meminta input nama file dari pengguna
    input_file = input("Masukkan nama file input (misalnya, 'input.txt'): ")
    output_file = input("Masukkan nama file output (misalnya, 'output.txt'): ")
    
    # Menjalankan fungsi untuk mengekstrak domain
    extract_domains_from_file(input_file, output_file)
    print(f"Domains telah disimpan ke {output_file}")
