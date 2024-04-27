import datetime
import json
import socket
import sys

MAX_LINE = 64 * 1024
MAX_HEADERS = 100


class HandleRequest:

    def __init__(self, request):
        self.request = request

    def handle_request(self, req):
        status = None
        # try:
        headers = self.fill_headers(req)
        body = self.create_body(req)
        # except:
        #     status = '500'
        #     return Response(status, 'Internal error', {}, '')
        # status = '200'
        return Response(status, 'OK', headers, body)

    def get_file_ext(self, req):
        resource = req.target
        file_extension = resource.split('.')[-1]
        return file_extension

    def get_file_path(self, req):
        with open("C:\\Users\\user\\PycharmProjects\\WebServer\\Server\\config\\config.json", "r", encoding='utf-8') as file: #TODO исключение
            data = json.load(file)
        target = req.target
        host_name = target[1:]
        for virtual_host in data["virtual_hosts"]:
            if virtual_host["host_name"] == host_name:
                document_root = virtual_host["document_root"]
                return document_root

    def define_content_type(self, req):
        file_extension = self.get_file_ext(req)
        with open("C:\\Users\\user\\PycharmProjects\\WebServer\\Server\\config\\config.json", "r") as file:
            data = json.load(file)

        content_type_map = data["content_type_map"][0]

        if file_extension in content_type_map:
            return content_type_map[file_extension]
        else:
            return 'text/html'

    def create_body(self, req):
        file_extension = self.get_file_ext(req)
        file_path = self.get_file_path(req)
        if file_extension == 'txt' or 'html':
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
            return data

        elif file_extension == 'json':
            with open(file_path, 'r') as file:
                data = json.load(file)
            return data

    def calculate_content_lehgth(self, req):
        body = self.create_body(req)
        return len(body)

    def define_reason(self):
        pass

    def fill_headers(self, req):  # TODO в завимисоти от статуса, если не ошибка
        headers = {}
        headers['Date'] = str(datetime.datetime.now())
        # headers['Server'] = ''
        headers['Content-Length'] = str(self.calculate_content_lehgth(req))
        headers['Content-Type'] = self.define_content_type(req)
        return headers

    # def handle_request(self, req):
    #     if self.request.method == 'GET':
    #         self.handle_get_request(req)


class HTTPServer:
    def __init__(self, host, port, server_name):
        self._host = host
        self._port = port
        self._server_name = server_name

    def serve_forever(self):  # TODO: многопточка в этом методе
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)

        try:
            serv_sock.bind((self._host, self._port))
            serv_sock.listen()

            while True:
                conn, _ = serv_sock.accept()
                self.serve_client(conn)
                # try:
                #     self.serve_client(conn)
                # except Exception as e:
                #     print('Client serving failed', e)
        finally:
            serv_sock.close()

    def serve_client(self, conn):
        # try:
        # rfile = conn.makefile('rb')
        # data = rfile.readline().decode('utf-8')

        data = conn.recv(8192).decode()

        print(data)
        if data:
            request = self.parse_request(data)
            response = self.handle_request(request)  # TODO
            self.send_response(conn, response)
        else:
            response = Response('200', 'OK', {'Date': '1', 'Server': '2'}, 'null_packet')
            self.send_response(conn, response)
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
        # host = headers.get('Host') TODO все ошибки обрабатываем в хэндл реквест и отправляем пользователю
        # if not host:
        #     raise Exception('Bad request')
        # if host not in (self._server_name,
        #                 f'{self._server_name}:{self._port}'):
        #     raise Exception('Not found')  # ??

        return Request(method, target, ver, headers, data)

    def parse_request_line(self, data):

        line = data.split('\r\n')[0]
        parse_line = line.split(' ')

        print(parse_line)

        return parse_line

    def parse_request_body(self, data):
        # content = rfile.read().decode('iso-8859-1') тут исключение
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
        print(headers_dict)

        return headers_dict

    def handle_request(self, req):
        handle_req = HandleRequest(req)
        resp = handle_req.handle_request(req)
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
            # wfile.write(resp.body)

        wfile.flush()
        wfile.close()

    def send_error(self, conn, err):  # TODO: возможно внести в респонз
        try:
            status = err.status
            reason = err.reason
            body = (err.body or err.reason).encode('utf-8')
        except:
            status = 500
            reason = b'Internal Server Error'
            body = b'Internal Server Error'
        resp = Response(status, reason,
                        [('Content-Length', len(body))],  # TODO написать объект респонз
                        body)
        self.send_response(conn, resp)


class Response:
    def __init__(self, status, comment, headers, body):
        self.status = status
        self.comment = comment
        self.headers = headers
        self.body = body


class Request:
    def __init__(self, method, target, version, headers, body):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.body = body


if __name__ == '__main__':
    # host = sys.argv[1]
    # port = int(sys.argv[2])
    # name = sys.argv[3]

    host = 'localhost'
    port = 80
    name = 'name'

    serv = HTTPServer(host, port, name)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass
