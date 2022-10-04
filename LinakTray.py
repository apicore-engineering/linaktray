#!/usr/bin/env python3
"""Small system tray application to adjust height of a Linak-based desk"""
import os

if os.environ.get("DESKTOP_SESSION") == "ubuntu":
    from linak_tray_gtk import LinakTray
else:
    from linak_tray_qt import LinakTray

LinakTray(config='linaktray.conf').run()
