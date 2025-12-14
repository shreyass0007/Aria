
import requests
import ssl
import certifi
import socket
import logging

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

print(f"Certifi path: {certifi.where()}")
print(f"OpenSSL version: {ssl.OPENSSL_VERSION}")

target_url = "https://www.googleapis.com"

print(f"\nAttempting to connect to {target_url}...")

try:
    response = requests.get(target_url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print("✅ Connection successful!")
except requests.exceptions.SSLError as e:
    print(f"\n❌ SSL Error: {e}")
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ Connection Error: {e}")
except Exception as e:
    print(f"\n❌ info Error: {e}")

print("\n--- Low-level Socket Check ---")
try:
    context = ssl.create_default_context(cafile=certifi.where())
    with socket.create_connection(("www.googleapis.com", 443)) as sock:
        with context.wrap_socket(sock, server_hostname="www.googleapis.com") as ssock:
            print(f"Protocol: {ssock.version()}")
            print(f"Cipher: {ssock.cipher()}")
            print("✅ Socket handshake successful!")
except Exception as e:
    print(f"❌ Socket Error: {e}")
