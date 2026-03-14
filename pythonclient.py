import socket
import threading
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import PBKDF2

PASSWORD = b"strongpassword"
SALT = b"chat_salt"

KEY = PBKDF2(PASSWORD, SALT, dkLen=32)

def encrypt_message(message):
    cipher = AES.new(KEY, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + ciphertext)

def decrypt_message(data):
    raw = base64.b64decode(data)
    iv = raw[:16]
    ciphertext = raw[16:]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    message = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return message.decode()

def receive_messages(client):
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break
            print("\nServer:", decrypt_message(data))
        except:
            break

def send_messages(client):
    while True:
        message = input("You: ")
        encrypted = encrypt_message(message)
        client.send(encrypted)

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5000))

    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()
    send_messages(client)

if __name__ == "__main__":
    start_client()