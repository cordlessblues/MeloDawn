from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex

class BrickModel(QAbstractListModel):
    ColorRole = Qt.UserRole + 1
    TrackIndexRole = Qt.UserRole + 2
    ActiveRole = Qt.UserRole + 3
    WidthRole = Qt.UserRole + 4
    HeightRole = Qt.UserRole + 5
    ScaleYRole = Qt.UserRole + 6
    VelocityRole = Qt.UserRole + 7
    TrackCountRole = Qt.UserRole + 8

    def __init__(self):
        super().__init__()
        self._data = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role):
        if not index.isValid():
            return None

        brick = self._data[index.row()]

        if role == self.ColorRole:
            return brick["color"]
        if role == self.TrackIndexRole:
            return brick["trackIndex"]
        if role == self.ActiveRole:
            return brick["active"]
        if role == self.WidthRole:
            return brick["width"]
        if role == self.HeightRole:
            return brick["height"]
        if role == self.ScaleYRole:
            return brick["scaleY"]
        if role == self.VelocityRole:
            return brick["velocity"]
        if role == self.TrackCountRole:
            return brick["trackCount"]

    def roleNames(self):
        return {
            self.ColorRole: b"color",
            self.TrackIndexRole: b"trackIndex",
            self.ActiveRole: b"active",
            self.WidthRole: b"width",
            self.HeightRole: b"height",
            self.ScaleYRole: b"scaleY",
            self.VelocityRole: b"velocity",
            self.TrackCountRole: b"trackCount",
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