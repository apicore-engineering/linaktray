#!/usr/bin/env python3
"""Small system tray application to adjust height of a Linak-based desk"""
from configparser import ConfigParser
import os
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from LinakDesk import Desk

class LinakTray(QtWidgets.QSystemTrayIcon):
    """System tray icon class"""
    def __init__(self, config=None):
        super().__init__()
        self.desk_mac = None
        self.positions = {}
        self.favourites = []
        self.current_position = None

        if config is not None:
            self._config_read(config)

        self.menu = self._construct_menu()
        self.setContextMenu(self.menu)
        self.activated.connect(lambda reason: self.action_click(reason, self))

    def _config_read(self, path):
        """Read configuration from file"""
        config = ConfigParser(allow_no_value=True)
        config.read(path)

        self.desk_mac = config['desk']['mac']

        self.positions = {}
        for key in config['positions']:
            self.positions[key] = int(config['positions'][key])

        self.favourites.clear()
        for key in config['favourites']:
            self.favourites.append(key)

        if 'icon' in config['settings']:
            self._set_icon(config['settings']['icon'])

        if 'get_position_at_startup' in config['settings']:
            self.get_position()

    def toggle_favourite(self):
        """Toggle between the two favourite positions"""
        next_favourite = self.guess_next_favourite()
        self.set_position(self.positions[next_favourite])

    def guess_favourite_index(self):
        """Determine the favourite preset closest to the current position"""
        return self.favourites.index(min(
            self.favourites,
            key=lambda fav: abs(self.positions[fav] - self.get_saved_position())
        ))

    def guess_next_favourite(self):
        """Determine the next favourite preset after the current one"""
        idx = self.guess_favourite_index() + 1
        if idx >= len(self.favourites):
            idx = 0
        return self.favourites[idx]

    def set_position(self, position):
        """Set desk position to given value"""
        print('Moving to position: ' + str(position))
        self.current_position = Desk(self.desk_mac).oneshot(position)

    def get_position(self):
        """Read desk position from desk"""
        self.current_position = Desk(self.desk_mac).oneshot_read_info()
        print('Current position: ' + str(self.current_position))

    def get_saved_position(self):
        """Return the current position of the desk. Retrieve the data if not present"""
        if self.current_position is None:
            self.get_position()
        return self.current_position

    def _construct_menu(self):
        """Construct a menu from the current configuration"""
        menu = QtWidgets.QMenu()
        self._construct_menu_positions(menu)
        self._construct_menu_quit(menu)
        return menu

    def _construct_menu_positions(self, parent):
        """Create entries for saved positions"""
        for key, value in self.positions.items():
            action = parent.addAction(key)
            action.triggered.connect(lambda state, position=value: self.set_position(position))

    @classmethod
    def _construct_menu_quit(cls, parent):
        """Create quit button"""
        parent.addSeparator()
        action_quit = parent.addAction("Quit")
        action_quit.triggered.connect(lambda _: sys.exit())

    def _set_icon(self, path):
        if not os.path.isabs(path):
            path = self.get_relative_path(path)
        self.setIcon(QtGui.QIcon(path))

    @classmethod
    @QtCore.pyqtSlot()
    def action_click(cls, reason, tray):
        """Toggle menu on click"""
        if reason in [QtWidgets.QSystemTrayIcon.DoubleClick, QtWidgets.QSystemTrayIcon.MiddleClick]:
            tray.toggle_favourite()

    @classmethod
    def get_relative_path(cls, path):
        """Find a relative path to the program itself"""
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


APP = QtWidgets.QApplication([])
APP.setQuitOnLastWindowClosed(False)
LINAKTRAY = LinakTray(
    config=LinakTray.get_relative_path('linaktray.conf'),
)
LINAKTRAY.show()
APP.exec_()
