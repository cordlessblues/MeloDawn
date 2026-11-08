import inspect
import os
import sys
import json
from pathlib import Path
from PySide6.QtCore import QObject, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView


class BaseWidget(QObject):
    # Default metadata (subclasses override this)
    WIDGET_INFO = {"name": "BaseWidget", "slot": "wide"}

    def __init__(self, parent=None):
        super().__init__(parent)

    @classmethod
    def getQMLPath(cls):
        module = inspect.getmodule(cls)
        if module and module.__file__:
            module_path = Path(module.__file__)
            qml_file = module_path.with_suffix(".qml")
            if qml_file.exists():
                return str(qml_file)
        return ""

    @classmethod
    def loadConfig(cls):
        with open("conf.json", "r") as f:
            config = json.load(f)[cls.WIDGET_INFO["name"]]
            return config

    @classmethod
    def standalone(cls):
        os.environ["QT_LOGGING_RULES"] = (
            "qt.qpa.wayland.textinput.warning=false;qt.multimedia.ffmpeg*=false"
        )

        # Automatically resolve parent path for shared resources like ColorUtils
        module = inspect.getmodule(cls)
        palette = None
        if module and module.__file__:
            parentDir = Path(module.__file__).resolve().parent.parent.parent
            if str(parentDir) not in sys.path:
                sys.path.insert(0, str(parentDir))
            try:
                from ColorUtils.ColorPalletes import ColorPallete

                palette = ColorPallete()
            except ImportError as e:
                print(f"[Error][MeloDawnWidget]: {e.msg}")

        app = QGuiApplication(sys.argv)
        backend = cls()
        backend._isDebug = True

        view = QQuickView()
        view.setColor(Qt.transparent)
        view.setResizeMode(QQuickView.SizeRootObjectToView)
        view.rootContext().setContextProperty("backend", backend)
        view.rootContext().setContextProperty("isDebugMode", backend._isDebug)
        if palette:
            view.rootContext().setContextProperty("sysColorPallete", palette)
        view.setTitle(cls.WIDGET_INFO.get("name", "Widget Preview"))

        qml_path = cls.getQMLPath()
        if qml_path:
            view.setSource(QUrl.fromLocalFile(qml_path))
        else:
            print(
                f"[BaseWidget] Warning: Could not find companion QML for {cls.__name__}"
            )

        if view.status() == QQuickView.Error:
            print("QML Error:")
            for error in view.errors():
                print(error.toString())
            sys.exit(1)

        rootItem = view.rootObject()
        if rootItem:
            rootItem.setProperty("backend", backend)
            rootItem.setProperty("isDebugMode", backend._isDebug)

        view.setWidth(400)
        view.setHeight(400)
        view.show()

        sys.exit(app.exec())
