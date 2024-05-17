class Log:
    def __init__(self, addr, date, frst_line, status):
        self.addr = addr
        self.date = date
        self.frst_line = frst_line
        self.status = status

    def get_string_repres(self):
        return f'{self.addr} -- {self.date}  {self.frst_line} {self.status} \n'

    def add_log_inf(self):
        with open("log/log.txt", 'a', encoding='utf-8') as f:
            data = self.get_string_repres()
            f.write(data)