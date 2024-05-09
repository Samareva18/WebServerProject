import datetime
import json
import response


class HandleRequest:

    def __init__(self, request):
        self.request = request

    def handle_request(self, req):
        status = None
        try:
            headers = self.fill_headers(req)
            body = self.create_body(req)
        except:
            status = '500'
            return response.Response(status, 'Internal error', {}, '')
        status = '200'
        return response.Response(status, 'OK', headers, body)

    def get_file_ext(self, req):
        resource = req.target
        file_extension = resource.split('.')[-1]
        return file_extension

    def get_file_path(self, req):
        with open("config/config.json", "r", encoding='utf-8') as file:
            data = json.load(file)
        target = req.target
        host_name = target[1:]
        for virtual_host in data["virtual_hosts"]:
            if virtual_host["host_name"] == host_name:
                document_root = virtual_host["document_root"]
                return document_root

    def define_content_type(self, req):
        file_extension = self.get_file_ext(req)
        with open("config/config.json", "r") as file:
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

    def fill_headers(self, req):
        headers = {}
        headers['Date'] = str(datetime.datetime.now())
        # headers['Server'] = ''
        headers['Content-Length'] = str(self.calculate_content_lehgth(req))
        headers['Content-Type'] = self.define_content_type(req)
        return headers

    # def handle_request(self, req):
    #     if self.request.method == 'GET':
    #         self.handle_get_request(req)
