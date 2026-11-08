from datetime import datetime
from PySide6.QtCore import Property, QTimer, Signal
from pathlib import Path
import sys

parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from MeloDawnWidget import BaseWidget


class ClockBackend(BaseWidget):
    WIDGET_INFO = {"name": "Clock", "slot": "square"}

    timeChanged = Signal()
    secondsChanged = Signal()
    ampmChanged = Signal()
    dateChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._time = ""
        self._seconds = 0
        self._ampm = ""
        self._date = ""

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)
        self.updateTime()

    def getTime(self):
        return self._time

    def getSeconds(self):
        return self._seconds

    def getAmPm(self):
        return self._ampm

    def getDate(self):
        return self._date

    time = Property(str, getTime, notify=timeChanged)
    seconds = Property(int, getSeconds, notify=secondsChanged)
    ampm = Property(str, getAmPm, notify=ampmChanged)
    date = Property(str, getDate, notify=dateChanged)

    def updateTime(self):
        now = datetime.now()
        self._time = now.strftime("%I:%M")
        self._ampm = now.strftime("%p")
        self._date = now.strftime("%A, %B %d")
        self._seconds = now.second

        self.timeChanged.emit()
        self.secondsChanged.emit()
        self.ampmChanged.emit()
        self.dateChanged.emit()

    def cleanup(self):
        self.timer.stop()


def init(context=None):
    return ClockBackend()


if __name__ == "__main__":
    ClockBackend.standalone()
