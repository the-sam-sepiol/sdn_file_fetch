#!/usr/bin/env python3
import socket
import base64
import argparse
import sys

def recv_line(sock):
    data = b''
    while True:
        chunk = sock.recv(1)
        if not chunk:
            break
        data += chunk
        if chunk == b'\n':
            break
    return data.decode().rstrip('\n')

def main():
    p = argparse.ArgumentParser(description="fetch file from custom sdn controller")
    p.add_argument('--host',    required=True)
    p.add_argument('--port',    type=int)
    p.add_argument('--password',required=True)
    p.add_argument('--remote',  required=True)
    p.add_argument('--out',     default=None)
    args = p.parse_args()

    out_file = args.out or args.remote.split('/')[-1]

    #connect to sdn
    sock = socket.create_connection((args.host, args.port))
    try:
        #send handshake
        sock.sendall(b"HELLO\n")
        resp = recv_line(sock)
        if resp != "Handshake complete":
            print("Handshake failed:", resp, file=sys.stderr)
            return 1

        #send auth
        sock.sendall(f"AUTH {args.password}\n".encode())
        resp = recv_line(sock)
        if resp != "AUTH_OK":
            print("Auth Failed", resp, file=sys.stderr)
            return 1

        #send a GET_FILE request
        sock.sendall(f"GET_FILE {args.remote}\n".encode())
        resp = recv_line(sock)
        if not resp.startswith("FILE_DATA "):
            print("ERROR | response:", resp, file=sys.stderr)
            return 1

        b64 = resp[len("FILE_DATA "):]

        #pad file and decode
        padding = -len(b64) % 4
        if padding:
            b64 += "=" * padding

        try:
            data = base64.b64decode(b64)
        except Exception as e:
            print("ERROR | Base64 Decode Fail:", e, file=sys.stderr)
            return 1

        with open(out_file, "wb") as f:
            f.write(data)

        print(f"Wrote {len(data)} bytes to {out_file}")

    finally:
        sock.close()

if __name__ == "__main__":
    sys.exit(main())
