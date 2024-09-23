import requests
import json

def custom_request(url, jwt):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {jwt}'
    }
    
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}")

    return response.json()


def passage_data_to_json(json_name, data):
    with open(json_name, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False ,indent=4)