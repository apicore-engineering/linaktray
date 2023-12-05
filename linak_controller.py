"""Controller class to adjust height of a Linak-based desk"""
import os
from linakdesk import Desk
from config import Config

class LinakController:
    """LinakTray control logic"""
    def __init__(self):
        self.desk_mac = Config().get('desk', 'mac')
        self.positions = {key: int(value) for key, value in Config().items('positions')}
        self.favourites = Config().options('favourites')
        self.current_position = None

        if Config().getboolean('settings', 'get_position_at_startup', fallback=False):
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
        self._set_active(True)
        try:
            print('Moving to position: ' + str(position))
            self.current_position = Desk(self.desk_mac).oneshot(position)
        finally:
            self._set_active(False)

    def get_position(self):
        """Read desk position from desk"""
        self._set_active(True)
        try:
            self.current_position = Desk(self.desk_mac).oneshot_read_info()
            print('Current position: ' + str(self.current_position))
        finally:
            self._set_active(False)

    def get_saved_position(self):
        """Return the current position of the desk. Retrieve the data if not present"""
        if self.current_position is None:
            self.get_position()
        return self.current_position

    def _set_active(self, active):
        self._set_icon(active=active)

    def _set_icon(self, active=False):
        pass

    @staticmethod
    def _get_icon_path(active=False):
        path = Config().get('settings', 'icon_active' if active else 'icon', fallback=None)
        if path is None or os.path.isabs(path):
            return path
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

    @staticmethod
    def _get_icon_fallback():
        return 'object-flip-vertical-symbolic'
