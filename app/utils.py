import hashlib


# Function to hash a password for security purposes
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
