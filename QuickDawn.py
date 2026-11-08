from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import qVersion
import sys
import os
from Widgets.WidgetManager import WidgetManager
from ColorUtils.ColorPalletes import ColorPallete

# SILENCE YOU FOOL
os.environ["QT_LOGGING_RULES"] = (
    "qt.qpa.wayland.textinput.warning=false;qt.multimedia.ffmpeg*=false"
)

app = QApplication(sys.argv)
engine = QQmlApplicationEngine()


pallete = ColorPallete()
engine.rootContext().setContextProperty("sysColorPallete", pallete)

manager = WidgetManager("./Widgets")
manager.loadWidgets()

engine.rootContext().setContextProperty("widgetManager", manager)

app.aboutToQuit.connect(manager.stopWidgets)

qmlPath = os.path.join(os.path.dirname(__file__), "Main.qml")
engine.load(qmlPath)

if engine.rootObjects():
    window = engine.rootObjects()[0]
else:
    print("Failed to load QML!")
    sys.exit(-1)
print("Sys.exit ignore below errors if any.")
sys.exit(app.exec())
