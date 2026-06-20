#!/usr/bin/env python3
"""Deploy hook: called by certbot after a successful certificate renewal.
Sends SIGHUP to the nginx container via the Docker API Unix socket,
causing nginx to reload its config and pick up the new certificate."""
import socket
import sys

DOCKER_SOCKET = "/var/run/docker.sock"
NGINX_CONTAINER = "termopol-nginx"

request = (
    f"POST /containers/{NGINX_CONTAINER}/kill?signal=HUP HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "Content-Length: 0\r\n"
    "Connection: close\r\n\r\n"
)

try:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(DOCKER_SOCKET)
    sock.sendall(request.encode())
    response = sock.recv(1024).decode()
    sock.close()
    status = response.split("\r\n")[0]
    print(f"nginx reload via Docker API: {status}")
    if "204" not in status:
        print("Unexpected response — nginx may not have reloaded", file=sys.stderr)
        sys.exit(1)
except Exception as e:
    print(f"Failed to reload nginx: {e}", file=sys.stderr)
    sys.exit(1)
