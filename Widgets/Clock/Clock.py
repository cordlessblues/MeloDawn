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
    colorChanged = Signal()

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
    from PySide6.QtCore import Qt, QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQuick import QQuickView
    from pathlib import Path
    import os, sys
    #SILENCE YOU FOOL
    os.environ["QT_LOGGING_RULES"] = "qt.qpa.wayland.textinput.warning=false"
    
    parentDir = Path(__file__).resolve().parent.parent
    if str(parentDir) not in sys.path:
        sys.path.insert(0, str(parentDir))
    from ColorUtils import ColorPallete
    pallete = ColorPallete()

    app = QGuiApplication(sys.argv)
    backend = init()
    backend._isDebug = True

    view = QQuickView()
    view.setColor(Qt.transparent)
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.rootContext().setContextProperty("backend", backend)
    view.rootContext().setContextProperty("isDebugMode", backend._isDebug)
    view.rootContext().setContextProperty("sysColorPallete", pallete)
    view.setTitle("AlarmClock")

    qmlFile = os.path.join(os.path.dirname(__file__), "Clock.qml")
    view.setSource(QUrl.fromLocalFile(qmlFile))

    rootItem = view.rootObject()
    if not rootItem:
        sys.exit("Failed to load QML frontend")
        
    if view.status() == QQuickView.Error:
        print("QML Error:")
        for error in view.errors():
            print(error.toString())
        sys.exit(1)

    rootItem.setProperty("backend", backend)
    rootItem.setProperty("isDebugMode", backend._isDebug)

    view.setWidth(400)
    view.setHeight(400)
    view.show()

    sys.exit(app.exec())