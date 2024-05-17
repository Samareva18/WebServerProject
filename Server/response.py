class Response:
    def __init__(self, status, comment, headers, body):
        self.status = status
        self.comment = comment
        self.headers = headers
        self.body = body
