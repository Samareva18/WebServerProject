import json
import os


class UpdateConfig:

    def __init__(self):
        self.base_dir = "C:\\Users\\user\\PycharmProjects\\WebServer\\Server\\"
        self.directory_to_watch = "C:\\Users\\user\\PycharmProjects\\WebServer\\Server\\resources\\www\\"
        self.config_file = "C:\\Users\\user\\PycharmProjects\\WebServer\\Server\\config\\config.json"

    def update_config(self, new_host):
        with open(self.config_file, 'r') as f:
            config_data = json.load(f)

        contains_src_html = any(host.get("host_name") == new_host for host in config_data["virtual_hosts"])

        if not contains_src_html:
            config_data['virtual_hosts'].append({
                "host_name": f"{new_host}",
                "host_root": f"{self.directory_to_watch}\\{new_host}\\"
            })

            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=4)

    def check_for_new_folders(self):
        folder_path = self.directory_to_watch
        existing_folders = set(os.listdir(folder_path))
        initial_folders = existing_folders.copy()

        while True:
            existing_folders = set(os.listdir(folder_path))
            new_folders = existing_folders - initial_folders

            if new_folders:
                for folder in new_folders:
                    self.update_config(folder)

                initial_folders = existing_folders.copy()

