import datetime
import json
import socket
import sys

MAX_LINE = 64 * 1024
MAX_HEADERS = 100


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
        #try:
        request = self.parse_request(conn)
        response = self.handle_request(request)  # TODO
        self.send_response(conn, response)
        #except ConnectionResetError:
            #conn = None
        #except Exception as e:
            #self.send_error(conn, e)

        if conn:
            conn.close()

    def parse_request(self, conn):

        rfile = conn.makefile('rb')

        # content = rfile.read()
        # print(content)
        #method, target, ver = self.parse_request_line(rfile)
        method = 'GET'
        target = '/'
        ver = 'http'
        #print(method, target, ver)
        headers = self.parse_request_headers(rfile)
        body = self.parse_request_body(rfile)
        # host = headers.get('Host') TODO все ошибки обрабатываем в хэндл реквест и отправляем пользователю
        # if not host:
        #     raise Exception('Bad request')
        # if host not in (self._server_name,
        #                 f'{self._server_name}:{self._port}'):
        #     raise Exception('Not found')  # ??

        return Request(method, target, ver, headers, rfile)


    def parse_request_line(self, rfile):
        line = rfile.readline().decode('iso-8859-1')
        line = line.split(' ')
        print(line)
        method = line[0]
        target = line[1]
        ver = line[2]
        print(method)
        print(target)
        print(ver)
        return line

    def parse_request_body(self, rfile):
        # content = rfile.read().decode('iso-8859-1') тут исключение
        # request_parts = content.split('\r\n\r\n')
        # body = request_parts[-1]
        body = ''
        return body

    def parse_request_headers(self, rfile): # TODO исключение в 93 строке + подумать с тем что когда считали 1 строку в другом методе сдвинется ли каретка
        headers = []
        frst_line = rfile.readline()
        i=0
        while i < 5:
            i+=1
            line = rfile.readline(MAX_LINE + 1)
            if len(line) > MAX_LINE:
                raise Exception('Header line is too long')

            if line in (b'\r\n', b'\n', b''):
                # завершаем чтение заголовков
                break

            headers.append(line)
            if len(headers) > MAX_HEADERS:
                raise Exception('Too many headers')

        hdict = {}
        for h in headers:
            h = h.decode('iso-8859-1')
            k, v = h.split(':', 1)
            hdict[k] = v

        return hdict

    def handle_request(self, req):
        headers = {'Date': '1', 'Server': '2'}
        return Response('200', 'OK', headers, 'test')

    # def handle_request(self, req):
    #     if req.method == 'GET':
    #         self.handle_get_request(req)

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
            wfile.write(resp.body.encode('iso-8859-1'))
            #wfile.write(resp.body)

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

    def create_body(self, req):
        host_name = req.target
        with open("config/config.json", "r") as file:
            data = json.load(file)

        # Запрашиваемый host_name
        requested_host_name = "example.com"

        # Поиск document_root по host_name
        for virtual_host in data["virtual_hosts"]:
            if virtual_host["host_name"] == requested_host_name:
                document_root = virtual_host["document_root"]
                print(f"Для host_name '{requested_host_name}' найден document_root: {document_root}")
                break
        else:
            print(f"Host_name '{requested_host_name}' не найден")

class Response:
    def __init__(self, status, comment, headers, body):
        self.status = status
        self.comment = comment
        self.date = datetime.datetime.now()  # TODO подумать как сделать лучше
        self.headers = headers
        self.body = body


class Request:
    def __init__(self, method, target, version, headers, body):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.body = body


# class HandleRequest:
#
#     def __init__(self, request):
#         self.request = request
#
#     def handle_get_request(self): ->Response
#
#
#     def define_content_type(self):
#         pass
#
#     def create_body(self):
#         pass
#
#     def calculate_content_lehgth(self):
#         pass
#
#     def is_target_exist(self):
#
#     def define_status(self):
#         pass
#
#     def define_reason(self):
#         pass
#
#     def fill_headers(self): #TODO в завимисоти от статуса, если не ошибка
#         headers = [[]]
#         headers['Date'] = ''
#         headers['Server'] = ''
#         headers['Content-Length'] = self.calculate_content_lehgth()
#         headers['Content-Type'] = self.define_content_type()
#
#     def handle_request(self):
#         if self.request.method == 'GET':
#             self.handle_get_request()


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
