import json
import os
import time


#TODO переделать чтобы правильно проверял наличие записи в конфиге  и чтобы правильно составлял запись

base_dir = os.path.dirname(os.path.abspath(__file__))

# Путь к каталогу, который необходимо мониторить
directory_to_watch = os.path.join(base_dir, 'resources', 'www')

# Путь к конфигурационному файлу Apache
apache_config_file = os.path.join(base_dir, 'config', 'config.json')

# Функция для обновления конфигурационного файла Apache
def update_apache_config(new_file):
    with open(apache_config_file, 'r') as f:
        config_data = json.load(f)

    # Проверяем, что информация о новом файле еще не добавлена
    if new_file not in config_data:
        config_data[new_file] = {
            "ServerName": "ex.com",
            "DocumentRoot": f"/resources/www/{new_file}"
        }

        with open(apache_config_file, 'w') as f:
            json.dump(config_data, f, indent=4)

        print(f"Добавлена информация о новом виртуальном хосте для файла {new_file}")

# Мониторим каталог на наличие новых файлов
while True:
    new_files = [f for f in os.listdir(directory_to_watch) if os.path.isfile(os.path.join(directory_to_watch, f))]

    for new_file in new_files:
        update_apache_config(new_file)

    # Ждем некоторое время перед повторной проверкой
    time.sleep(10)
