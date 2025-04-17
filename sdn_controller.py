#!/usr/bin/env python3
import socket
import threading
import base64
import hashlib
import hmac
import os
import argparse

#load auth from file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'auth.conf')

SALT = None
PASSWORD_HASH = None

with open(CONFIG_PATH, 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key, val = line.split('=', 1)
        if key == 'salt':
            SALT = val.encode()
        elif key == 'password_hash':
            PASSWORD_HASH = base64.b64decode(val)

if SALT is None or PASSWORD_HASH is None:
    raise RuntimeError("auth.conf must contain salt and password_hash")

def hash_password(password: str) -> bytes: 
    return hashlib.pbkdf2_hmac('sha256', password.encode(), SALT, 100_000)


def handle_client(conn: socket.socket, addr):
    print(f"[INFO] Connection from {addr}")
    authenticated = False

    try:
        #handshake
        hello = conn.recv(1024).decode().strip()
        if hello != "HELLO":
            conn.sendall(b"ERROR\n")
            return
        conn.sendall(b"Handshake complete\n")

        while True:
            data = conn.recv(4096)
            if not data:
                break
            msg = data.decode().strip()
            print(f"[RECV] {addr}: {msg}")

            #auth
            if msg.startswith("AUTH "):
                _, pw = msg.split(maxsplit=1)
                candidate_hash = hash_password(pw)
                if hmac.compare_digest(candidate_hash, PASSWORD_HASH):
                    authenticated = True
                    conn.sendall(b"AUTH_OK\n")
                    print(f"[AUTH] {addr} authenticated")
                else:
                    conn.sendall(b"AUTH_FAIL\n")
                    print(f"[AUTH] {addr} failed authentication")

            elif msg.startswith("PACKET_IN"):
                content = msg[len("PACKET_IN"):].strip()
                resp = f"PACKET_OUT {content}\n"
                conn.sendall(resp.encode())

            elif msg.startswith("GET_FILE"):
                if not authenticated:
                    conn.sendall(b"ERROR: Not authenticated\n")
                    continue

                parts = msg.split(maxsplit=1)
                if len(parts) != 2:
                    conn.sendall(b"ERROR: GET_FILE requires <path>\n")
                    continue

                path = parts[1]
                try:
                    with open(path, "rb") as f:
                        data = f.read()
                    payload = base64.b64encode(data).decode()
                    conn.sendall(f"FILE_DATA {payload}\n".encode())
                    print(f"[FILE] Sent {path} to {addr}")
                except Exception as e:
                    err = f"ERROR: Could not read file: {e}\n"
                    conn.sendall(err.encode())
                    print(f"[ERROR] {addr}: {e}")

            else:
                conn.sendall(b"ERROR: Unknown command\n")

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        conn.close()
        print(f"[CLOSED] {addr}")

def run_controller():
    p = argparse.ArgumentParser()
    p.add_argument('--host', required=True)
    p.add_argument('--port', type=int, required=True)
    args = p.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.host, args.port))
    sock.listen(5)
    print(f"[STARTED] Controller listening on {args.host}:{args.port}")

    try:
        while True:
            client, address = sock.accept()
            t = threading.Thread(target=handle_client, args=(client, address))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN]")
    finally:
        sock.close()

if __name__ == "__main__":
    run_controller()
