import requests
import os


BASE_API = 'https://pomelo.colorbit.ru'

def send_scan(image):
    img = requests.get(image).content

    res = requests.post(
        f'{BASE_API}/api/scans',
        headers={'Authorization': f'Bearer {os.getenv("API_POMELO")}'},
        files={
            'photo': ('image.jpg', img, 'image/jpeg'),
        },
        data={
            'type': 'food'
        }
    )
    print(res.json())
    return res

def get_scan(id):
    res = requests.get(
        f'{BASE_API}/api/scans/{id}',
        headers={'Authorization': f'Bearer {os.getenv("API_POMELO")}'}
    )
    print(res.json())
    return res