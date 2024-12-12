def text_to_ascii_escape(text):
    return ''.join(f'\\x{ord(char):02x}' for char in text)

# Input dari pengguna
user_input = input("Masukkan teks yang ingin dikonversi: ")
ascii_escape_result = text_to_ascii_escape(user_input)

print(f"Hasil konversi: {ascii_escape_result}")
