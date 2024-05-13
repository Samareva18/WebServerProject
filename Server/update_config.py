import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
directory_to_watch = os.path.join(base_dir, 'resources', 'www')
config_file = os.path.join(base_dir, 'config', 'config.json')


def update_config(new_host):
    with open(config_file, 'r') as f:
        config_data = json.load(f)

    contains_src_html = any(host.get("host_name") == new_host for host in config_data["virtual_hosts"])

    if not contains_src_html:
        config_data['virtual_hosts'].append({
            "host_name": f"{new_host}",
            "host_root": f"{directory_to_watch}\\{new_host}\\"
        })

        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=4)


def check_for_new_folders():
    folder_path = directory_to_watch
    existing_folders = set(os.listdir(folder_path))

    # Сохраняем список папок до проверки
    initial_folders = existing_folders.copy()
    existing_folders = set(os.listdir(folder_path))
    for folder in existing_folders:
        update_config(folder)

    while True:
        existing_folders = set(os.listdir(folder_path))
        new_folders = existing_folders - initial_folders

        if new_folders:
            for folder in new_folders:
                update_config(folder)

            # Обновляем список папок для следующей проверки
            initial_folders = existing_folders.copy()


check_for_new_folders()
