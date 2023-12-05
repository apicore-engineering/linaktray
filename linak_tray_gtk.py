"""Small system tray application to adjust height of a Linak-based desk"""
# pylint: disable=wrong-import-position,wrong-import-order
import os
import sys
import gi
from linak_controller import LinakController

gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import AyatanaAppIndicator3 as appindicator
from gi.repository import Gtk as gtk

class LinakTray(LinakController):
    """System tray icon class"""
    def __init__(self):
        super().__init__()
        self.indicator = self._create_indicator()
        self.menu = self._construct_menu()
        self.indicator.set_menu(self.menu)
        self._set_icon()

    @staticmethod
    def run():
        """Run the main loop"""
        gtk.main()

    def _create_indicator(self):
        indicator = appindicator.Indicator.new(
            "LinakTray",
            self._get_icon_fallback(),
            appindicator.IndicatorCategory.APPLICATION_STATUS,
        )
        indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        return indicator

    def _construct_menu(self):
        """Construct a menu from the current configuration"""
        menu = gtk.Menu()
        self._construct_menu_toggle(menu)
        self._construct_menu_separator(menu)
        self._construct_menu_positions(menu)
        self._construct_menu_separator(menu)
        self._construct_menu_quit(menu)
        menu.show()
        return menu

    def _construct_menu_positions(self, parent):
        """Create entries for saved positions"""
        for key, value in self.positions.items():
            action = gtk.MenuItem(label=key)
            action.connect("activate", lambda state, position=value: self.set_position(position))
            action.show()
            parent.append(action)

    def _construct_menu_toggle(self, parent):
        """Create toggle favourite button"""
        action_toggle = gtk.MenuItem(label="Toggle")
        action_toggle.connect("activate", lambda _: self.toggle_favourite())
        action_toggle.show()
        self.indicator.set_secondary_activate_target(action_toggle)
        parent.append(action_toggle)

    @classmethod
    def _construct_menu_quit(cls, parent):
        """Create quit button"""
        action_quit = gtk.MenuItem(label="Quit")
        action_quit.connect("activate", lambda _: sys.exit())
        action_quit.show()
        parent.append(action_quit)

    @classmethod
    def _construct_menu_separator(cls, parent):
        """Create a separator menu item"""
        separator = gtk.SeparatorMenuItem()
        separator.show()
        parent.append(separator)

    def _set_icon(self, active=False):
        path = self._get_icon_path(active=active)
        if path is None:
            return
        self.indicator.set_icon_theme_path(os.path.dirname(path))
        self.indicator.set_icon_full(os.path.splitext(os.path.basename(path))[0], "Icon")
        if active:
            gtk.main_iteration_do(True)
