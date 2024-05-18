import asyncio
import datetime
import socket
import threading
import handle_request
import request
import log
import parse_request
import update_config


class HTTPServer:

    def __init__(self, host, port, server_name):
        self._host = host
        self._port = port
        self._server_name = server_name
        self.log = log.Log('', '', '', '')

    async def serve_forever(self):
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)

        self.update_config()


        try:
            serv_sock.bind((self._host, self._port))
            serv_sock.listen()

            while True:
                conn, addr = serv_sock.accept()
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

        data = conn.recv(8192).decode()  # блокирующая
        print(data)

        req = ''
        if data:
            req = self.parse_request(data)
            resp = self.handle_request(req)
            await self.send_response(conn, resp)
        # except ConnectionResetError:
        # conn = None
        # except Exception as e:
        # self.send_error(conn, e)

        if not self.is_keep_alive(req):
            conn.close()

    def update_config(self):
        upd_conf = update_config.UpdateConfig()
        folder_thread = threading.Thread(target=upd_conf.check_for_new_folders)
        folder_thread.start()

    def is_keep_alive(self, req):
        if req:
            headers_d = req.headers
            for header in headers_d:
                if header == 'Connection':
                    if headers_d[header] == 'keep-alive':
                        return True
        return False

    def parse_request(self, data):
        try:
            pars_req = parse_request.ParseRequest(data, self.log)
            method, target, ver = pars_req.parse_request_line()
            headers = pars_req.parse_request_headers()
            body = pars_req.parse_request_body()
        except ValueError:
            return request.Request(None, None, None, None, None)

        return request.Request(method, target, ver, headers, body)

    def handle_request(self, req):
        handle_req = handle_request.HandleRequest(req)
        resp = handle_req.handle_request()
        self.log.status = resp.status
        self.log.add_log_inf()
        return resp

    async def send_response(self, conn, resp):
        wfile = conn.makefile('wb')
        status_line = f'HTTP/1.1 {resp.status} {resp.comment}\r\n'
        wfile.write(status_line.encode('iso-8859-1'))
        if resp.headers:
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
        asyncio.run(serv.serve_forever())
    except KeyboardInterrupt:
        pass
