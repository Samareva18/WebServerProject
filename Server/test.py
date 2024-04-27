import json


# def get_file_path():
#     with open("config/config.json", "r") as file:
#         data = json.load(file)
#     host_name = "index.html"
#     for virtual_host in data["virtual_hosts"]:
#         if virtual_host["host_name"] == host_name:
#             document_root = virtual_host["document_root"]
#             return document_root
#
#
# print(get_file_path())


with open("C:\\Users\\user\\PycharmProjects\\WebServer\\Server\\resources\\www\\index.html", 'r', encoding='utf-8') as file:
    data = file.read()
    print(data)