import json
import os
import os.path
import requests


def via_post(
        api_base: str, url_relative: str, token: str, filepath: str) -> int:

    url = api_base + url_relative
    headers = {
        'Authorization': 'Bearer ' + token
    }

    name = os.path.basename(filepath)
    size = os.stat(filepath).st_size

    params = {
        'name': name,
        'size': size
    }

    resp = requests.post(url, headers=headers, params=params).json()

    upload_url = resp['upload_url']
    data = resp['upload_params']
    name = resp['file_param']

    with open(filepath, "rb") as f:
        resp = requests.post(
            upload_url, data=data, files=[(name, f)])

    return json.loads(resp.text)['id']
