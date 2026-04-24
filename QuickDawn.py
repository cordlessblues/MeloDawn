from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
import sys
import os
from Widgets.WidgetManager import WidgetManager

app = QApplication(sys.argv)
engine = QQmlApplicationEngine()

manager = WidgetManager("./Widgets")
manager.load_widgets()

engine.rootContext().setContextProperty("widgetManager", manager)

qml_path = os.path.join(os.path.dirname(__file__), "Main.qml")
engine.load(qml_path)

if engine.rootObjects():
    window = engine.rootObjects()[0]
else:
    print("Failed to load QML!")
    sys.exit(-1)
print("Sys.exit ignore below errors if any.")
sys.exit(app.exec())