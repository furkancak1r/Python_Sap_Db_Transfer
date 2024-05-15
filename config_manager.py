import json
import os

config_file_path = "db_config.json"

def save_config(data, config_type):
    if os.path.exists(config_file_path):
        with open(config_file_path, "r+") as file:
            configs = json.load(file)
            configs[config_type] = data
            file.seek(0)
            json.dump(configs, file, indent=4)
            file.truncate()
    else:
        with open(config_file_path, "w") as file:
            json.dump({config_type: data}, file, indent=4)

def read_config(config_type):
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as file:
            configs = json.load(file)
            return configs.get(config_type, {})
    return {}

def delete_config(config_type):
    if os.path.exists(config_file_path):
        with open(config_file_path, "r+") as file:
            configs = json.load(file)
            configs.pop(config_type, None)
            file.seek(0)
            json.dump(configs, file, indent=4)
            file.truncate()
def update_config(data, config_type):
    save_config(data, config_type)
