"""
Scan Tracker Service

This module contains the ScanTracker class responsible for managing scan lifecycle:
- Subscribing to SSE updates
- Processing status updates
- Managing scan sessions
"""

import asyncio
import logging
from typing import Callable, Awaitable
from services.pomelo_service import PomeloService


logger = logging.getLogger(__name__)


class ScanTracker:
    """Manages scan lifecycle and status updates"""

    def __init__(self, pomelo_service: PomeloService):
        self.pomelo_service = pomelo_service
        self.active_scans = []

    async def track_scan(
        self,
        user_id: str,
        scan_id: str,
        on_status: Callable[[str, object], Awaitable[None]],
        on_complete: Callable[[object], Awaitable[None]],
        on_error: Callable[[str], Awaitable[None]]
    ) -> bool:
        """
        Start tracking scan status updates

        Args:
            user_id: User identifier
            scan_id: Scan ID to track
            on_status: Callback for status updates (status, scan_entity)
            on_complete: Callback when scan is fully completed (scan_entity)
            on_error: Callback for errors (error_message)

        Returns:
            True if tracking started, False if user already has active scan
        """
        # Check if user already has active scan
        if user_id in self.active_scans:
            return False

        # Add user to active scans
        self.active_scans.append(user_id)
        logger.info(f"Started tracking scan {scan_id} for user {user_id}")

        # Internal callback for SSE status updates
        async def handle_status_update(status: str):
            """Process status update from SSE"""
            logger.info(f"Scan {scan_id}: status '{status}'")

            # Handle error statuses
            if status in ("failed", "analysis_failed", "recognition_failed"):
                await on_error(f"Scan failed: {status}")
                self._cleanup_scan(scan_id, user_id)
                return

            # Handle completion statuses
            if status in ("completed", "ai_analysis_completed"):
                # Fetch full scan result
                scan_entity = await self.pomelo_service.getScanResult(scan_id)

                # Check if scan is fully completed
                if not scan_entity.is_fully_completed():
                    logger.info(f"Scan {scan_id} almost done, waiting for AI analysis...")
                    return

                logger.info(f"Scan {scan_id} fully completed")

                # Notify about completion
                await on_complete(scan_entity)
                self._cleanup_scan(scan_id, user_id)
            else:
                # Notify about status change
                await on_status(status, None)

        # Internal callback for SSE errors
        async def handle_error(error: str):
            """Process SSE connection error"""
            logger.error(f"SSE connection error for scan {scan_id}: {error}")
            await on_error(f"Connection error: {error}")
            self._cleanup_scan(scan_id, user_id)

        # Subscribe to status updates
        asyncio.create_task(
            self.pomelo_service.subscribeScanStatusUpdate(
                scan_id, handle_status_update, handle_error
            )
        )

        return True

    def _cleanup_scan(self, scan_id: str, user_id: str) -> None:
        """Clean up resources after scan completion"""
        # Remove from active scans
        if user_id in self.active_scans:
            self.active_scans.remove(user_id)
            logger.info(f"User {user_id} removed from active scans")

        # Unsubscribe from updates
        self.pomelo_service.unsubscribeFromStatusUpdates(scan_id)
        logger.info(f"Unsubscribed from scan {scan_id} updates")
