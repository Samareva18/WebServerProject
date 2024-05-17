
class ParseRequest:
    def __init__(self, request, log):
        self.request = request
        self.log = log

    def parse_request_line(self):
        data = self.request
        line = data.split('\r\n')[0]
        parse_line = line.split(' ')
        self.log.frst_line = line

        return parse_line

    def parse_request_body(self):
        data = self.request
        request_parts = data.split('\r\n\r\n')
        body = request_parts[-1]
        return body

    def parse_request_headers(self):
        data = self.request
        headers_dict = {}
        split_data = data.split('\r\n')
        split_data.pop(0)
        for header in split_data:
            if header == '':
                break
            split_header = header.split(': ')
            headers_dict[split_header[0]] = split_header[1]

        return headers_dict