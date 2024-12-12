import os

# Fungsi untuk menulis semua baris ke file hasil yang ditentukan oleh pengguna
def write_result_file(output_file, input_files):
    with open(output_file, 'w', encoding='utf-8') as result_file:
        for filename in input_files:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8', errors='ignore') as file:  # Menambahkan errors='ignore'
                    for line in file:
                        result_file.write(line)
            else:
                print(f"File {filename} tidak ditemukan.")

# Main
if __name__ == "__main__":
    # Meminta nama file output dari pengguna
    output_file = input("Masukkan nama file output (misalnya, 'result.txt'): ")
    
    # Meminta pengguna untuk memasukkan nama file yang ingin disatukan
    input_files = []
    print("Masukkan nama file yang ingin disatukan (format: 1.txt, 2.txt, ...). Tekan Enter untuk selesai:")
    
    while True:
        filename = input("Nama file: ")
        if filename:
            input_files.append(filename)
        else:
            break  # Keluar dari loop jika tidak ada input

    # Memanggil fungsi untuk menulis hasil
    write_result_file(output_file, input_files)
    print(f"Semua baris telah disatukan ke dalam {output_file}")
