"""
Pomelo API wrapper

This module provides functions for interacting with the Pomelo API.

Functions:

- `send_scan(image)`: Sends a scan request to the Pomelo API with the given image.
- `send_text(text)`: Sends a text request to the Pomelo API with the given text.
- `get_scan(id)`: Retrieves a scan from the Pomelo API by its ID.

By Bolgaro4ka / 2025
"""


import requests
import os

# Pomelo API
BASE_API = 'https://pomelo.colorbit.ru'

def send_scan(image : str) -> requests.Response:
    """
    Sends a scan request to the Pomelo API with the given image.

    Parameters:
        image (str): The URL of the image to be scanned.

    Returns:
        requests.Response: The response object containing the result of the scan request.
    """
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
    return res

def send_text(text : str) -> requests.Response:
    """
    Sends a text request to the Pomelo API with the given text.

    Parameters:
        text (str): The text to be sent.

    Returns:
        requests.Response: The response object containing the result of the request.
    """
    res = requests.post(
        f'{BASE_API}/api/scans',
        headers={'Authorization': f'Bearer {os.getenv("API_POMELO")}'},
        data={
            "composition": text,
            'type': 'food'
        }
    )
    return res

def get_scan(id : str) -> requests.Response:
    """
    Retrieves a scan from the Pomelo API by its ID.

    Args:
        id (str): The ID of the scan to retrieve.

    Returns:
        requests.Response: The response object containing the result of the GET request.
    """

    res = requests.get(
        f'{BASE_API}/api/scans/{id}',
        headers={'Authorization': f'Bearer {os.getenv("API_POMELO")}'}
    )
    return res