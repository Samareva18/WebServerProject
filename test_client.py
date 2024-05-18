import socket
import tempfile
import webbrowser

HOST = 'localhost'
PORT = 80

request = "GET /index.html HTTP/1.1\r\nHost: site2.com\r\n\r\n"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(request.encode())

    response = b''
    while True:
        data = s.recv(1024)
        if not data:
            break
        response += data

print(response.decode())
s.close()
