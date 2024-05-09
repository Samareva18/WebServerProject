import datetime
import socket
import sys
import threading
import handle_request
import request
import response
import log


class HTTPServer:

    def __init__(self, host, port, server_name):
        self._host = host
        self._port = port
        self._server_name = server_name
        self.log = log.Log('', '', '', '')

    def serve_forever(self):
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)

        try:
            serv_sock.bind((self._host, self._port))
            serv_sock.listen()

            while True:
                conn, addr = serv_sock.accept()
                self.log.addr = addr
                self.log.date = datetime.datetime.now()
                # self.serve_client(conn)

                client_thread = threading.Thread(target=self.serve_client, args=(conn,))
                client_thread.start()

                # try:
                #     self.serve_client(conn)
                # except Exception as e:
                #     print('Client serving failed', e)
        finally:
            serv_sock.close()

    def serve_client(self, conn):
        # try:

        data = conn.recv(8192).decode()

        if data:
            request = self.parse_request(data)
            resp = self.handle_request(request)
            self.send_response(conn, resp)
        else:
            resp = response.Response('200', 'OK', {'Date': '1', 'Server': '2'}, 'null_packet')
            self.send_response(conn, resp)
        # except ConnectionResetError:
        # conn = None
        # except Exception as e:
        # self.send_error(conn, e)

        if conn:
            conn.close()

    def parse_request(self, data):
        method, target, ver = self.parse_request_line(data)
        headers = self.parse_request_headers(data)
        body = self.parse_request_body(data)

        return request.Request(method, target, ver, headers, data)

    def parse_request_line(self, data):

        line = data.split('\r\n')[0]
        self.log.frst_line = line
        parse_line = line.split(' ')

        return parse_line

    def parse_request_body(self, data):
        request_parts = data.split('\r\n\r\n')
        body = request_parts[-1]
        return body

    def parse_request_headers(self, data):
        headers_dict = {}
        split_data = data.split('\r\n')
        split_data.pop(0)
        for header in split_data:
            if header == '':
                break
            split_header = header.split(': ')
            headers_dict[split_header[0]] = split_header[1]

        return headers_dict

    def handle_request(self, req):
        handle_req = handle_request.HandleRequest(req)
        resp = handle_req.handle_request(req)
        self.log.status = resp.status
        self.log.add_log_inf()
        return resp

    # формируем готовый ответ и отправляем его
    def send_response(self, conn, resp):
        wfile = conn.makefile('wb')
        status_line = f'HTTP/1.1 {resp.status} {resp.comment}\r\n'
        wfile.write(status_line.encode('iso-8859-1'))
        if resp.headers:  # TODO возможно убрать эту проверку
            for (key, value) in resp.headers.items():
                header_line = f'{key}: {value}\r\n'
                wfile.write(header_line.encode('iso-8859-1'))

        wfile.write(b'\r\n')

        if resp.body:
            wfile.write(resp.body.encode('utf-8'))

        wfile.flush()
        wfile.close()


if __name__ == '__main__':

    host = '127.0.0.1'
    port = 80
    name = 'name'

    serv = HTTPServer(host, port, name)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass
