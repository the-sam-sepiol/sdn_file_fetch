
import hashlib
import base64
import argparse
import sys

def main():
    p = argparse.ArgumentParser(description="generate hash")
    p.add_argument('--salt', required=True)
    p.add_argument('--pw', required=True)
    args = p.parse_args()

    salt_bytes = args.salt.encode('utf-8')
    pw_bytes = args.pw.encode('utf-8')

    dk = hashlib.pbkdf2_hmac('sha256', pw_bytes, salt_bytes, 100_000)

    hash_b64 = base64.b64encode(dk).decode('utf-8')

    with open("auth.conf", 'w', encoding='utf-8') as f:
        f.write(f"salt={args.salt}\n")
        f.write(f"password_hash={hash_b64}\n")

if __name__ == "__main__":
    sys.exit(main())
