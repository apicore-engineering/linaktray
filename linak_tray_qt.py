"""Small system tray application to adjust height of a Linak-based desk"""
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from linak_controller import LinakController

class LinakTray(LinakController, QtWidgets.QSystemTrayIcon):
    """System tray icon class"""
    def __init__(self, config=None):
        self.qt_app = self._init_qt()

        QtWidgets.QSystemTrayIcon.__init__(self)
        LinakController.__init__(self, config=config)

        self.menu = self._construct_menu()
        self.setContextMenu(self.menu)
        self.activated.connect(lambda reason: self.action_click(reason, self))
        self.show()

    def run(self):
        """Run main loop"""
        self.qt_app.exec_()

    @staticmethod
    def _init_qt():
        """Initialize the Qt application"""
        app = QtWidgets.QApplication([])
        app.setQuitOnLastWindowClosed(False)
        return app

    def _construct_menu(self):
        """Construct a menu from the current configuration"""
        menu = QtWidgets.QMenu()
        self._construct_menu_toggle(menu)
        menu.addSeparator()
        self._construct_menu_positions(menu)
        menu.addSeparator()
        self._construct_menu_quit(menu)
        return menu

    def _construct_menu_positions(self, parent):
        """Create entries for saved positions"""
        for key, value in self.positions.items():
            action = parent.addAction(key)
            action.triggered.connect(lambda state, position=value: self.set_position(position))

    def _construct_menu_toggle(self, parent):
        """Create toggle favourite button"""
        action_toggle = parent.addAction("Toggle")
        action_toggle.triggered.connect(lambda _: self.toggle_favourite())

    @classmethod
    def _construct_menu_quit(cls, parent):
        """Create quit button"""
        action_quit = parent.addAction("Quit")
        action_quit.triggered.connect(lambda _: sys.exit())

    def _set_icon(self, path):
        self.setIcon(QtGui.QIcon(self._get_absolute_path(path)))

    @classmethod
    @QtCore.pyqtSlot()
    def action_click(cls, reason, tray):
        """Toggle menu on click"""
        if reason in [QtWidgets.QSystemTrayIcon.DoubleClick, QtWidgets.QSystemTrayIcon.MiddleClick]:
            tray.toggle_favourite()
