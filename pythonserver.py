import socket
import threading
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import PBKDF2

# ==============================
# Configuration (MUST match client)
# ==============================
PASSWORD = b"strongpassword"
SALT = b"chat_salt"
KEY = PBKDF2(PASSWORD, SALT, dkLen=32)

HOST = "0.0.0.0"
PORT = 5000


# ==============================
# Encryption Functions
# ==============================
def encrypt_message(message):
    cipher = AES.new(KEY, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    encrypted_data = base64.b64encode(cipher.iv + ciphertext)
    return encrypted_data


def decrypt_message(data):
    raw = base64.b64decode(data)
    iv = raw[:16]
    ciphertext = raw[16:]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted.decode()


# ==============================
# Communication Functions
# ==============================
def receive_messages(conn):
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break

            print("\n[Encrypted Received]:", data)
            print("Client (Decrypted):", decrypt_message(data))

        except Exception as e:
            print("Receive error:", e)
            break


def send_messages(conn):
    while True:
        try:
            message = input("You (plaintext): ")

            encrypted = encrypt_message(message)

            print("[Encrypted Sent]:", encrypted)

            conn.sendall(encrypted)

        except Exception as e:
            print("Send error:", e)
            break


# ==============================
# Server Setup
# ==============================
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"Server listening on port {PORT}...")
    conn, addr = server.accept()
    print("Connected by", addr)

    threading.Thread(target=receive_messages, args=(conn,), daemon=True).start()
    send_messages(conn)


if __name__ == "__main__":
    start_server()