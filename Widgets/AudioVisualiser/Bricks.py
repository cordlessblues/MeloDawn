from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class BrickModel(QAbstractListModel):
    TrackIndexRole = Qt.UserRole + 1
    ActiveRole = Qt.UserRole + 2
    VelocityRole = Qt.UserRole + 3
    MessagesRole = Qt.UserRole + 4
    ScaleYRole = Qt.UserRole + 5
    TypeRole = Qt.UserRole + 6

    def __init__(self):
        super().__init__()
        self._data = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role):
        if not index.isValid():
            return None

        brick = self._data[index.row()]

        if role == self.TrackIndexRole:
            return brick["trackIndex"]
        if role == self.ActiveRole:
            return brick["active"]
        if role == self.VelocityRole:
            return brick["velocity"]
        if role == self.MessagesRole:
            return brick["messages"]
        if role == self.ScaleYRole:
            return brick.get("scaleY", 1.0)
        if role == self.TypeRole:
            return brick.get("type", "Unknown")
        return None

    def roleNames(self):
        return {
            self.TrackIndexRole: b"trackIndex",
            self.ActiveRole: b"active",
            self.VelocityRole: b"velocity",
            self.MessagesRole: b"messages",
            self.ScaleYRole: b"scaleY",
            self.TypeRole: b"audioType",
        }

    def updateBricks(self, bricks):
        if len(self._data) != len(bricks):
            self.beginResetModel()
            self._data = bricks
            self.endResetModel()
            return

        for i in range(len(bricks)):
            self._data[i] = bricks[i]
            index = self.index(i)
            self.dataChanged.emit(index, index, list(self.roleNames().keys()))
