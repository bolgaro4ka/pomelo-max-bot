"""
SSE Listener module

This module contains functions for listening to updates for a scan with the given scan ID.

Contains functions for:

- Checking if a scan is fully completed based on the given scan JSON.
- Asynchronously listening to updates for a scan with the given scan ID.

By Bolgaro4ka / 2025
"""

import json
import requests
from sseclient import SSEClient

def is_scan_fully_completed(scan_json: dict) -> bool:
    """
    Check if a scan is fully completed based on the given scan JSON.

    Args:
        scan_json (dict): The scan JSON containing the status and aiAnalysis fields.

    Returns:
        bool: True if the scan is fully completed, False otherwise.
    """
    status = scan_json.get("status")
    ai_analysis = scan_json.get("aiAnalysis")

    return status == "completed" and ai_analysis is not None


async def listen_scan_updates(scan_id: str, get_scan_result, on_error=None):
    """
    Asynchronously listens to updates for a scan with the given scan ID.

    Args:
        scan_id (str): The ID of the scan.
        get_scan_result (async function): A function that retrieves the scan result for the given scan ID.
        on_error (async function, optional): A function that handles errors that occur during the scan. Defaults to None.

    Returns:
        None

    This function sends a GET request to the specified URL to receive SSE updates for the given scan ID. It listens to the SSE events and performs the following actions based on the event data:

    - If the event data indicates an error (failed, analysis_failed, or recognition_failed), the provided `on_error` function is called with the error status as an argument, and the function exits.
    - If the event data indicates that the scan is completed or ai_analysis_completed, the provided `get_scan_result` function is called with the scan ID to retrieve the scan result. The function then checks if the scan is fully completed. If not, it continues to listen for SSE updates. If the scan is fully completed, it retrieves the links and attachments from the scan response, and performs further actions.

    Note: The `get_scan_result` and `on_error` functions are defined outside of this function and are not accessible outside of the scope of this function.
    """
    url = f"https://pomelo.colorbit.ru/api/scans/{scan_id}/status-updates"

    with requests.get(url, stream=True) as response:
        client = SSEClient(response)

        for event in client.events():
            try:
                data = json.loads(event.data)
                status = data.get("status")
                print("SSE event:", status)

                # If error -> call on_error
                if status in ("failed", "analysis_failed", "recognition_failed"):
                    if on_error:
                        await on_error(status)
                    break

                # If status is completed or ai_analysis_completed -> request real result
                if status in ("completed", "ai_analysis_completed"):

                    # вызываем то же, что делает frontend
                    await get_scan_result(scan_id)

                    # get_scan_result will decide for himself whether everything is ready or not.
                    # If not ready — listen for updates
                    continue

            except Exception as e:
                if on_error:
                    await on_error(str(e))
                break
