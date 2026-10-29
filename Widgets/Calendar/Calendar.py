from PySide6.QtCore import (
    QObject,
    QTimer,
    QAbstractListModel,
    QModelIndex,
    Qt,
    QUrl
)
from PySide6.QtGui import QGuiApplication
from icalevents.icalevents import events
from PySide6.QtQuick import QQuickView
from PySide6.QtCore import Property, Signal
from datetime import datetime
from pathlib import Path
import json

class CalendarEvent: # MARK: Calendar Event
    def __init__(self, title, subject, dueDate, overdue):
        self.title = title
        self.subject = subject
        self.dueDate = dueDate
        self.overdue = overdue


class CalendarModel(QAbstractListModel): # MARK: Calendar Model
    TitleRole = Qt.UserRole + 1
    SubjectRole = Qt.UserRole + 2
    DueDateRole = Qt.UserRole + 3
    OverdueRole = Qt.UserRole + 4

    def __init__(self, events=None):
        super().__init__()
        self._events = events or []

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        event = self._events[index.row()]
        if role == self.TitleRole:
            return event.title
        if role == self.SubjectRole:
            return event.subject
        if role == self.DueDateRole:
            return event.dueDate
        if role == self.OverdueRole:
            return event.overdue
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._events)

    def roleNames(self):
        return {
            self.TitleRole: b"title",
            self.SubjectRole: b"subject",
            self.DueDateRole: b"dueDate",
            self.OverdueRole: b"overdue",
        }

    def setEvents(self, events):
        self.beginResetModel()
        self._events = events
        self.endResetModel()


class Backend(QObject): # MARK: Backend
    modelChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = CalendarModel()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateData)
        self.timer.start(1000 * 60 * 60 * 3) # 3 hours
        self.updateData()

    def getModel(self):
        return self._model

    model = Property(QObject, getModel, notify=modelChanged)

    def parse_course(self, summary):
        try:
            return summary.split("[")[1].split("-")[0].strip().capitalize()
        except:
            return "Unknown"

    def fetchCalData(self): # MARK: Fetch Calendar Data
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        with open(BASE_DIR / ".ENV.json") as f:
            config = json.load(f)

        all_events = []
        for cal in config["Calender"].values():
            all_events += events(url=cal["URL"], fix_apple=cal["FixApple"])

        output = []
        now = datetime.now()
        for e in all_events:
            course = self.parse_course(e.summary)
            title = e.summary.split("[")[0].strip()
            subject = course

            for cal in config["Calender"].values():
                subject_data = cal.get("Subjects", {}).get(course)
                if subject_data:
                    subject = subject_data["Name"]
                    title = title.split("[")[0]
                    break

            output.append(
                CalendarEvent(
                    title=title,
                    subject=subject,
                    dueDate=e.end.strftime("%Y-%m-%d"),
                    overdue=e.end.replace(tzinfo=None) < now,
                )
            )

        output.sort(key=lambda x: x.dueDate)
        return output

    def updateData(self):
        events = self.fetchCalData()
        self._model.setEvents(events)
        self.modelChanged.emit()


# MARK: Metadata & Init
WIDGET_INFO = {"name": "Calendar", "slot": "wide"}
def init(context=None): return Backend()

if __name__ == "__main__":
    import sys, os
    os.environ["QT_LOGGING_RULES"] = "qt.qpa.wayland.textinput.warning=false"
    parentDir = Path(__file__).resolve().parent.parent
    if str(parentDir) not in sys.path:
        sys.path.insert(0, str(parentDir))
    from ColorUtils import ColorPallete
    pallete = ColorPallete()
    

    app = QGuiApplication(sys.argv)

    backend = Backend()

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.rootContext().setContextProperty("backend", backend)
    view.setSource(QUrl.fromLocalFile("Widgets/Calendar/Calendar.qml"))
    view.rootContext().setContextProperty("sysColorPallete", pallete)
    view.setColor(Qt.transparent)
    view.setWidth(400)
    view.setHeight(400)
    view.show()

    sys.exit(app.exec())