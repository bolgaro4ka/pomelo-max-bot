"""
Pomelo API async wrapper

This module provides async functions for interacting with the Pomelo API.

Functions:

- `send_scan(image)`: Sends a scan request to the Pomelo API with the given image.
- `send_text(text)`: Sends a text request to the Pomelo API with the given text.
- `get_scan(id)`: Retrieves a scan from the Pomelo API by its ID.

By Bolgaro4ka / 2025
"""

import os
import aiohttp
import asyncio

BASE_API = 'https://pomelo.colorbit.ru'


async def send_scan(image: str) -> aiohttp.ClientResponse:
    """
    Sends a scan request to the Pomelo API with the given image.

    Parameters:
        image (str): The URL of the image to be scanned.

    Returns:
        aiohttp.ClientResponse: The response object containing the result of the scan request.
    """
    token = os.getenv("API_POMELO")

    async with aiohttp.ClientSession() as session:
        # Download image
        async with session.get(image) as img_resp:
            img_bytes = await img_resp.read()

        form = aiohttp.FormData()
        form.add_field('photo', img_bytes, filename='image.jpg', content_type='image/jpeg')
        form.add_field('type', 'food')

        async with session.post(
            f'{BASE_API}/api/scans',
            headers={'Authorization': f'Bearer {token}'},
            data=form
        ) as resp:
            return await resp.json()


async def send_text(text: str) -> aiohttp.ClientResponse:
    """
    Sends a text request to the Pomelo API with the given text.

    Parameters:
        text (str): The text to be sent.

    Returns:
        aiohttp.ClientResponse: The response object containing the result of the request.
    """
    token = os.getenv("API_POMELO")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{BASE_API}/api/scans',
            headers={'Authorization': f'Bearer {token}'},
            data={
                "composition": text,
                "type": "food",
            }
        ) as resp:
            return await resp.json()


async def get_scan(id: str) -> aiohttp.ClientResponse:
    """
    Retrieves a scan from the Pomelo API by its ID.

    Args:
        id (str): The ID of the scan to retrieve.

    Returns:
        aiohttp.ClientResponse: The response object containing the result of the GET request.
    """
    token = os.getenv("API_POMELO")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{BASE_API}/api/scans/{id}',
            headers={'Authorization': f'Bearer {token}'}
        ) as resp:
            return await resp.json()