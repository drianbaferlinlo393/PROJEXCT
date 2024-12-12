import argparse

def filter_lines(input_file, output_file, keywords, encoding='utf-8'):
    # Membuka file input untuk dibaca dan file output untuk ditulis
    with open(input_file, 'r', encoding=encoding, errors='ignore') as infile, open(output_file, 'w', encoding=encoding) as outfile:
        # Membaca setiap baris dari file input
        for line in infile:
            # Menulis baris ke file output jika baris mengandung salah satu kata kunci
            if any(keyword in line for keyword in keywords):
                outfile.write(line)

if __name__ == "__main__":
    # Meminta input nama file dan kata kunci dari pengguna
    input_file = input("Masukkan nama file input (misalnya, 'input.txt'): ")
    output_file = input("Masukkan nama file output (misalnya, 'output.txt'): ")
    keywords = input("Masukkan kata kunci : (misalnya, '/admin/login'): ").split()

    # Menjalankan fungsi untuk memfilter baris
    filter_lines(input_file, output_file, keywords)
    print(f"Baris yang mengandung kata kunci telah disaring dan disimpan di {output_file}")
