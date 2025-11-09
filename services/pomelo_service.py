import os
import aiohttp
import json
import requests
from sseclient import SSEClient
from typing import Dict, Any, Optional, Callable, Awaitable
from entities.scan_entity import ScanEntity


class PomeloService:
    """
    Class for interacting with the Pomelo API for food scanning.
    """

    def __init__(self):
        self.base_url = 'https://pomelo.colorbit.ru/api'
        self.token = os.getenv("POMELO_API_TOKEN")
        self._active_subscriptions = {}  # scan_id -> should_stop flag

        if not self.token:
            raise ValueError("API token is required. Provide it in POMELO_API_TOKEN env variable.")

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

    async def createPhotoScan(self, photo_url: str) -> ScanEntity:
        """Create a scan by photo URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(photo_url) as img_resp:
                img_bytes = await img_resp.read()

        form = aiohttp.FormData()
        form.add_field('photo', img_bytes, filename='image.jpg', content_type='image/jpeg')
        form.add_field('type', 'food')

        result = await self._request('POST', '/scans', data=form)
        return ScanEntity(result.get("scan", {}))

    async def createTextScan(self, composition_text: str) -> ScanEntity:
        """Create a scan by composition text"""
        form = aiohttp.FormData()
        form.add_field('composition', composition_text)
        form.add_field('type', 'food')

        result = await self._request('POST', '/scans', data=form)
        return ScanEntity(result.get("scan", {}))

    async def getScanResult(self, scan_id: str) -> ScanEntity:
        """Get scan result by scan ID"""
        result = await self._request('GET', f'/scans/{scan_id}')
        return ScanEntity(result.get("scan", {}))

    async def subscribeScanStatusUpdate(
        self,
        scan_id: str,
        on_status_update: Callable[[str], Awaitable[None]],
        on_error: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> None:
        """
        Subscribe to scan status updates via SSE.
        """
        url = f"{self.base_url}/scans/{scan_id}/status-updates"

        # Mark this subscription as active
        self._active_subscriptions[scan_id] = False

        try:
            with requests.get(url, stream=True) as response:
                client = SSEClient(response)

                for event in client.events():
                    # Check if we should stop this subscription
                    if self._active_subscriptions.get(scan_id, False):
                        print(f"Unsubscribed from scan {scan_id}")
                        break

                    try:
                        data = json.loads(event.data)
                        status = data.get("status")
                        print(f"SSE event: {status}")

                        # Call the callback with status
                        await on_status_update(status)

                    except Exception as e:
                        if on_error:
                            await on_error(str(e))
                        break

        except Exception as e:
            if on_error:
                await on_error(f"Connection error: {str(e)}")
        finally:
            # Clean up subscription
            if scan_id in self._active_subscriptions:
                del self._active_subscriptions[scan_id]

    def unsubscribeFromStatusUpdates(self, scan_id: str) -> None:
        """
        Unsubscribe from scan status SSE updates.
        """
        if scan_id in self._active_subscriptions:
            self._active_subscriptions[scan_id] = True
