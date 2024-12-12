import os
from colorama import init, Fore, Style

init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.RED}{'='*40}
    {Fore.CYAN}{Style.BRIGHT}FATCAT CYBER TEAM Ft JACK007
{Fore.RED}{'='*40}
{Fore.YELLOW}{'='*40}
          {Fore.GREEN}Main Tools Menu      
{Fore.YELLOW}{'='*40}
 {Fore.BLUE}1. Grabber Premium
 {Fore.BLUE}2. Subfinder Tools
 {Fore.BLUE}3. CMS Scan Tools
 {Fore.BLUE}4. RCE Scan Tools
 {Fore.BLUE}5. Penyatu TXT
 {Fore.BLUE}6. Filter CMS TXT
 {Fore.BLUE}7. Domain Extractor
 {Fore.BLUE}8. Convert ASCII
 {Fore.BLUE}9. Convert Hash MD5
 {Fore.BLUE}10. Reverse IP
 {Fore.BLUE}11. Convert Domain To IP
 {Fore.BLUE}12. Grabber Path Tools
 {Fore.BLUE}13. 4 In 1
 {Fore.BLUE}14. Dorking Google
 {Fore.BLUE}15. WP Username Finder + Brute-forcer
 {Fore.BLUE}16. XMLRPC
 {Fore.BLUE}0. Exit
{Fore.YELLOW}{'='*40}
{Fore.RED}Donasi: https://t.me/fatcatcyberteam
{Fore.RED}        https://t.me/xinxhau
{Fore.YELLOW}{'='*40}
    """
    print(banner)

def main():
    while True:
        print_banner()
        choice = input(f"{Fore.WHITE}Pilih Tools : {Fore.MAGENTA}")

        if choice == '1':
            os.system('python files/grabber3.py')
        elif choice == '2':
            os.system('python files/subfinder.py')
        elif choice == '3':
            os.system('python files/cms-filter.py')
        elif choice == '4':
            os.system('python files/rce.py')
        elif choice == '5':
            os.system('python files/penyatu.py')
        elif choice == '6':
            os.system('python files/script.py')
        elif choice == '7':
            os.system('python files/extract.py')
        elif choice == '8':
            os.system('python files/ascii.py')
        elif choice == '9':
            os.system('python files/hashmd5.py')
        elif choice == '10':
            os.system('python files/rev.py')
        elif choice == '11':
            os.system('python files/domip.py')
        elif choice == '12':
            os.system('python files/grabber2.py')
        elif choice == '13':
            os.system('python files/4in1.py')
        elif choice == '14':
            os.system('python files/dorking.py')
        elif choice == '15':
            os.system('python files/WP.py')
        elif choice == '16':
            os.system('python files/xmlrpc.py')
        elif choice == '0':
            print(f"{Fore.GREEN}Exiting...")
            break
        else:
            print(f"{Fore.RED}Pilihan tidak valid. Silakan coba lagi.")

        input(f"{Fore.YELLOW}Tekan Enter untuk kembali ke menu...")

if __name__ == "__main__":
    main()
