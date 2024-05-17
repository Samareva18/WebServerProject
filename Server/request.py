class Request:
    def __init__(self, method, target, version, headers, body):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.body = body
