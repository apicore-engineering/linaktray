#!/usr/bin/env python3
"""Small system tray application to adjust height of a Linak-based desk"""
from linak_tray_qt import LinakTray

LinakTray(config='linaktray.conf').run()
