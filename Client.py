#!/usr/bin/env python3

import socket

HOST = '34.71.37.77'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Estoy preparado para recibir un archivo...')
    data = s.recv(1024)

print('Received', repr(data))