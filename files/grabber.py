import time
import requests

yellow = '\033[1;33m'
red = '\033[1;31m'
clear = '\033[0m'

print(yellow + "[==============================]")
print(yellow + "   " + yellow + "Priv8 Domain Graber")
print(yellow + "   " + yellow + "Version  : 4.0")
print(yellow + "   " + yellow + "Fatcat Cyber ft Jack007")
print(yellow + "[==============================]")

domain = input("Input Domains: ")
output_filename = input("Input nama file output (tanpa ekstensi): ") + ".txt"

response = requests.get("https://tranco-list.eu/download/65GX/10000000000000000000000000000000000")
results = [line.split(",")[1] for line in response.text.splitlines() if line.endswith("." + domain)]

with open(output_filename, "w") as file:
    for result in results:
        file.write(result + "\n")

print("Grabbing...")
time.sleep(3)

with open(output_filename, "r") as file:
    for line in file:
        print(line.strip())

print(clear)
