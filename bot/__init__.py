"""
Bot handlers package

This package contains all bot message handlers organized by functionality.

By Bolgaro4ka / 2025
"""

from .start import register_start_handlers
from .help import register_help_handlers
from .about import register_about_handlers
from .disclaimer import register_disclaimer_handlers
from .scanner import register_scanner_handlers


def register_all_handlers(dp):
    """Register all bot handlers"""
    register_start_handlers(dp)
    register_help_handlers(dp)
    register_about_handlers(dp)
    register_disclaimer_handlers(dp)
    register_scanner_handlers(dp)

