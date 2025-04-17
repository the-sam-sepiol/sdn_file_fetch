# Python SDN Controller & Secure File Fetch

A minimal, extensible SDN controller framework in pure Python, featuring secure authentication and Base64‑encoded file retrieval over a simple text protocol.

## Repository Structure

- **sdn_controller.py**  
  A lightweight TCP‑based SDN controller that supports:
  - **HELLO** handshake
  - **AUTH `<password>`** using PBKDF2‑HMAC‑SHA256 (salted)
  - **PACKET_IN `<data>`** → responds with `PACKET_OUT <data>`
  - **GET_FILE `<path>`** → returns file (requires prior AUTH)
  - Configuration loaded from **auth.conf** (contains salt and password hash)

- **generateHash.py**  
  CLI tool to generate **auth.conf**.  
  **Usage:**
  ```bash
  python3 generateHash.py \
    --salt "<your_salt>" \
    --pw   "<your_password>"
  ```
  This writes `auth.conf`:
  ```ini
  salt=<your_salt>
  password_hash=<base64_hash>
  ```

- **fileFetch.py**  
  Client utility to fetch files from the SDN controller. Automates handshake, authentication, Base64 padding/decoding, and file save.  
  **Usage:**
  ```bash
  python3 fileFetch.py \
    --host     <controller_ip> \
    --port     <controller_port> \
    --password <your_password> \
    --remote   <remote_file_path> \
    --out      <local_output_filename>
  ```

## Requirements

- Python 3.6 or newer  
- Standard library only (no external dependencies)

## Setup & Quickstart

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sdn_file_fetch.git
   cd sdn_file_fetch
   ```

2. **Generate authentication config**  
   ```bash
   python3 generateHash.py --salt <SALT> --pw <PASSWORD>
   ```
   This produces `auth.conf` in the project root.

3. **Start the SDN Controller**  
   ```bash
   python3 sdn_controller.py --host <hostIP> --port <PORT>
   ```

4. **Fetch a file**  
   ```bash
   python3 fileFetch.py \
     --host 127.0.0.1 --port 6633 \
     --password mySecretPass \
     --remote /path/on/controller/remote.file \
     --out /path/on/local/out.file
      ```

   You can also manually test with netcat:

   ```bash
   nc 127.0.0.1 6633
   HELLO
   AUTH mySecretPass
   GET_FILE /path/on/controller/config.yaml
   ```
