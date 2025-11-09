

import os
import aiohttp
from typing import Dict, Any, Optional


class PomeloService:
    """
    Class for interacting with the Pomelo API for food scanning.
    """
    def __init__(self):
        self.base_url = 'https://pomelo.colorbit.ru'
        self.token = os.getenv("API_POMELO")

        if not self.token:
            raise ValueError("API token is required. Provide it via constructor or API_POMELO env variable.")

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send API request with token"""
        url = f'{self.base_url}{endpoint}'
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.token}'

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                headers=headers,
                data=data,
                **kwargs
            ) as resp:
                return await resp.json()

    async def createPhotoScan(self, photo_url: str) -> Dict[str, Any]:
        """Create a scan by photo URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(photo_url) as img_resp:
                img_bytes = await img_resp.read()

        form = aiohttp.FormData()
        form.add_field('photo', img_bytes, filename='image.jpg', content_type='image/jpeg')
        form.add_field('type', 'food')

        return await self._request('POST', '/api/scans', data=form)

    async def createTextScan(self, composition_text: str) -> Dict[str, Any]:
        """Create a scan by composition text"""
        data = {
            "composition": composition_text,
            "type": "food",
        }

        return await self._request('POST', '/api/scans', data=data)

    async def getScanResult(self, scan_id: str) -> Dict[str, Any]:
        """Get scan result by scan ID"""
        return await self._request('GET', f'/api/scans/{scan_id}')
