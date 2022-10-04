#!/usr/bin/env python3
"""Small system tray application to adjust height of a Linak-based desk"""
import os
from config import Config

def _get_gui_type():
    """Detect the GUI type to use"""
    config = Config().get('settings', 'gui')
    if config in ('gtk', 'qt'):
        return config
    if os.environ.get("DESKTOP_SESSION") in ("ubuntu", "cinnamon"):
        return 'gtk'
    return 'qt'

if _get_gui_type() == 'gtk':
    from linak_tray_gtk import LinakTray
else:
    from linak_tray_qt import LinakTray

LinakTray().run()
