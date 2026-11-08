from datetime import datetime
import json
from pathlib import Path
import sys

parentDir = Path(__file__).resolve().parent.parent
if str(parentDir) not in sys.path:
    sys.path.insert(0, str(parentDir))

from MeloDawnWidget import BaseWidget
from icalevents.icalevents import events
from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QObject,
    Property,
    Qt,
    QThread,
    QTimer,
    Signal,
    Slot,
)


class CalendarEvent:  # MARK: Calendar Event

    def __init__(self, title, subject, dueDate, overdue):
        self.title = title
        self.subject = subject
        self.dueDate = dueDate
        self.overdue = overdue


class CalendarModel(QAbstractListModel):  # MARK: Calendar Model
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


class CalendarFetchWorker(QThread):

    dataFetched = Signal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            BASE_DIR = Path(__file__).resolve().parent.parent.parent
            with open(BASE_DIR / ".ENV.json") as f:
                config = json.load(f)

            allEvents = []
            for cal in config.get("Calendar", {}).values():
                allEvents += events(url=cal["URL"], fix_apple=cal["FixApple"])

            output = []
            now = datetime.now()
            for e in allEvents:
                try:
                    course = e.summary.split("[")[1].split("-")[0].strip().capitalize()
                except:
                    course = "Unknown"

                title = e.summary.split("[")[0].strip()
                subject = course

                for cal in config.get("Calendar", {}).values():
                    subjectData = cal.get("Subjects", {}).get(course)
                    if subjectData:
                        subject = subjectData["Name"]
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
            self.dataFetched.emit(output)
        except Exception as e:
            print(f"[Calendar] Failed to fetch data: {e}")
            self.dataFetched.emit([])


class CalendarBackend(BaseWidget):  # MARK: Backend
    WIDGET_INFO = {"name": "Calendar", "slot": "wide"}

    modelChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = CalendarModel()
        self._worker = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateData)
        self.timer.start(1000 * 60 * 60 * 3)  # 3 hours

        QTimer.singleShot(1, self.updateData)

    def getModel(self):
        return self._model

    model = Property(QObject, getModel, notify=modelChanged)

    @Slot()
    def updateData(self):
        if self._worker and self._worker.isRunning():
            return

        self._worker = CalendarFetchWorker()
        self._worker.dataFetched.connect(self.onDataReady)
        self._worker.start()

    @Slot(list)
    def onDataReady(self, events_list):
        self._model.setEvents(events_list)
        self.modelChanged.emit()

    def cleanup(self):
        if hasattr(self, "timer"):
            self.timer.stop()
        if self._worker and self._worker.isRunning():
            self._worker.quit()
            if not self._worker.wait(300):
                print("[Hass] Worker thread did not exit in time, forcing shutdown.")


def init(context=None):
    return CalendarBackend()


if __name__ == "__main__":
    CalendarBackend.standalone()
