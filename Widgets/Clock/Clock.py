from PySide6.QtCore import QObject, Signal, Property, QTimer, QUrl, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView
from datetime import datetime
import sys

class Backend(QObject): # MARK: Backend
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

    def get_time(self): return self._time
    def get_seconds(self): return self._seconds
    def get_ampm(self): return self._ampm
    def get_date(self): return self._date

    time = Property(str, get_time, notify=timeChanged)
    seconds = Property(int, get_seconds, notify=secondsChanged)
    ampm = Property(str, get_ampm, notify=ampmChanged)
    date = Property(str, get_date, notify=dateChanged)

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
# MARK: Metadata & Init
WIDGET_INFO = {"name": "Clock", "slot": "square"}
def init(context=None):
    return Backend()

if __name__ == "__main__": # MARK: Unit Test
    app = QGuiApplication(sys.argv)

    clockBackend = Backend()

    view = QQuickView()
    view.setWidth(400)
    view.setHeight(400)
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.rootContext().setContextProperty("backend", clockBackend)
    view.setSource(QUrl.fromLocalFile("Widgets/Clock/Clock.qml"))
    view.setColor(Qt.transparent)
    view.setTitle("AlarmClock")

    view.show()

    sys.exit(app.exec())