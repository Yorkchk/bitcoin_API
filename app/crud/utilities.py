import hashlib


def verify_APIkey_hashedkey(stored_key: str, provided_key: str) -> bool:
        salt_hex, hashed_key = stored_key.split(':')
        salt = bytes.fromhex(salt_hex)
        provided_hashed = hashlib.sha256(salt + provided_key.encode()).hexdigest()
        return provided_hashed == hashed_key