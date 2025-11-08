import json
import requests
from sseclient import SSEClient

async def listen_scan_updates(scan_id: str, get_scan_result, on_error=None):
    """
    scan_id: ID скана
    get_scan_result: async функция, которую надо вызвать когда статус = completed
    on_error: callback при ошибке
    """

    url = f"https://pomelo.colorbit.ru/api/scans/{scan_id}/status-updates"

    # requests должен быть stream=True
    with requests.get(url, stream=True) as response:
        client = SSEClient(response)

        for event in client.events():
            try:
                data = json.loads(event.data)
                status = data.get("status")
                print("SSE event:", status)

                # Завершён
                if status == "completed":
                    await get_scan_result(scan_id)
                    break

                # Ошибки
                if status in ("failed", "analysis_failed", "recognition_failed"):
                    if on_error:
                        await on_error(status)
                    break

            except Exception as e:
                if on_error:
                    await on_error(str(e))
                break
