import requests
import os.path
import json


def get_json_info(file_dir, url):
    if not os.path.exists(file_dir):
        json_info = requests.get(url).json()
        with open(file_dir, 'w') as json_file:
            json_file.write(json.dumps(json_info))
    else:
        with open(file_dir, 'r') as json_file:
            json_info = json.load(json_file)
    return json_info

