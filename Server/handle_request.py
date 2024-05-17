import datetime
import json
import response
import errors


class HandleRequest:

    def __init__(self, request):
        self.request = request

    def handle_get_request(self):
        try:
            headers = self.fill_headers()
            body = self.create_body()
        except FileNotFoundError:
            return self.handle_error('404')
        except Exception as e:
            status = '500'
            return response.Response(status, 'Internal error', {}, e)
        status = '200'
        return response.Response(status, 'OK', headers, body)

    def check_method_implement(self):
        req = self.request
        not_impl = True
        with open("config/config.json", "r", encoding='utf-8') as file:
            data = json.load(file)
        req_method = req.method
        for method in data['methods']:
            if method['method'] == req_method:
                not_impl = False
        if not_impl:
            raise errors.NotImplementedMethodError

    def check_bad_request(self):
        req = self.request
        if req.method or req.target or req.version is None:
            raise errors.BadRequestError

        if 'Host' not in req.headers:
            raise errors.BadRequestError


    def handle_error(self, error_code):
        status = ''
        comment = ''
        with open("config/config.json", "r", encoding='utf-8') as file:
            data = json.load(file)
        for error in data['errors_code']:
            if error['code'] == error_code:
                status = error['code']
                comment = error['comment']
                page_path = error['page_root']
                with open(page_path, 'r', encoding='utf-8') as file:
                    body = file.read()

        return response.Response(status, comment, {}, body)

    def get_file_ext(self):
        req = self.request
        resource = req.target
        file_extension = resource.split('.')[-1]
        return file_extension

    def get_host_header(self):
        req = self.request
        headers_d = req.headers
        host = headers_d['Host']
        return host

    def get_file_path(self):
        req = self.request
        host_root = ''
        with open("config/config.json", "r", encoding='utf-8') as file:
            data = json.load(file)
        target = req.target
        host_name = self.get_host_header()
        for virtual_host in data["virtual_hosts"]:
            if virtual_host["host_name"] == host_name:
                host_root = virtual_host["host_root"]
        file_path = host_root + target
        return file_path

    def define_content_type(self):
        file_extension = self.get_file_ext()
        with open("config/config.json", "r") as file:
            data = json.load(file)

        content_type_map = data["content_type_map"][0]

        if file_extension in content_type_map:
            return content_type_map[file_extension]
        else:
            return 'text/html'

    def create_body(self):
        file_extension = self.get_file_ext()
        file_path = self.get_file_path()
        if file_extension == 'txt' or 'html':
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
            return data

        elif file_extension == 'json':
            with open(file_path, 'r') as file:
                data = json.load(file)
            return data

    def calculate_content_lehgth(self):
        body = self.create_body()
        return len(body)

    def fill_headers(self):
        headers = {}
        headers['Date'] = str(datetime.datetime.now())
        # headers['Server'] = ''
        headers['Content-Length'] = str(self.calculate_content_lehgth())
        headers['Content-Type'] = self.define_content_type()
        return headers

    def handle_request(self):
        try:
            self.check_bad_request()
            self.check_method_implement()

            if self.request.method == 'GET':
                return self.handle_get_request()

        except errors.NotImplementedMethodError:
            return self.handle_error('501')
        except errors.BadRequestError:
            return self.handle_error('400')
