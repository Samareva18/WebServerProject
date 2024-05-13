import asyncio
import datetime
import socket
import threading
import handle_request
import request
import response
import log
from Server import update_config


class HTTPServer:

    def __init__(self, host, port, server_name):
        self._host = host
        self._port = port
        self._server_name = server_name
        self.log = log.Log('', '', '', '')

    async def serve_forever(self):
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)

        folder_thread = threading.Thread(target=update_config.check_for_new_folders())
        folder_thread.start()

        try:
            serv_sock.bind((self._host, self._port))
            serv_sock.listen()

            while True:
                conn, addr = serv_sock.accept() #блокирующая
                self.log.addr = addr
                self.log.date = datetime.datetime.now()
                await asyncio.create_task(self.serve_client(conn))

                # try:
                #     self.serve_client(conn)
                # except Exception as e:
                #     print('Client serving failed', e)
        finally:
            serv_sock.close()

    async def serve_client(self, conn):
        # try:

        data = conn.recv(8192).decode() #блокирующая
        #print(data)

        if data:
            request = self.parse_request(data)
            resp = self.handle_request(request)
            await self.send_response(conn, resp)
        else:
            resp = response.Response('200', 'OK', {'Date': '1', 'Server': '2'}, 'null_packet')
            await self.send_response(conn, resp)
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
    async def send_response(self, conn, resp): # вся функция блокирующая
        wfile = conn.makefile('wb')
        status_line = f'HTTP/1.1 {resp.status} {resp.comment}\r\n'
        wfile.write(status_line.encode('iso-8859-1'))
        if resp.headers:  # TODO возможно убрать эту проверку
            for (key, value) in resp.headers.items():
                header_line = f'{key}: {value}\r\n'
                wfile.write(header_line.encode('iso-8859-1'))  #блокирующая

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
        asyncio.run(serv.serve_forever())
    except KeyboardInterrupt:
        pass
