import hashlib

def md5_hash(password):
    return hashlib.md5(password.encode()).hexdigest()

password = input("Enter the password: ")
hashed_password = md5_hash(password)
print(f"MD5 Hash: {hashed_password}")
