import socket


class HTTPServer:
    def __init__(self, host, port, server_name):
        self._host = host
        self._port = port
        self._server_name = server_name

    def serve_forever(self):  # TODO: многопточка в этом методе
        serv_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            proto=0)

        try:
            serv_sock.bind((self._host, self._port))
            serv_sock.listen()

            while True:
                conn, _ = serv_sock.accept()
                try:
                    self.serve_client(conn)
                except Exception as e:
                    print('Client serving failed', e)
        finally:
            serv_sock.close()

    def serve_client(self, conn):
        response = 'hello world'
        wfile = conn.makefile('wb')
        wfile.write(response.encode('iso-8859-1'))

        wfile.flush()
        wfile.close()

        if conn:
            conn.close()


if __name__ == '__main__':

    host = 'localhost'
    port = 80
    name = 'name'

    serv = HTTPServer(host, port, name)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass
