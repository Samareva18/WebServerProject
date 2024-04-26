import socket

HOST = 'localhost'  # Адрес сервера
PORT = 80  # Порт сервера

# Создаем сокет
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Подключаемся к серверу
client_socket.connect((HOST, PORT))

# Отправляем запрос на сервер
client_socket.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')

# Получаем ответ от сервера
response = b''
while True:
    data = client_socket.recv(1024)
    if not data:
        break
    response += data

print(response.decode('iso-8859-1'))  # Декодируем ответ и выводим его

# Закрываем соединение
client_socket.close()
