import importlib.util
import os, inspect, sys, json
from PySide6.QtCore import QObject, Slot
from pathlib import Path

parentDir = Path(__file__).resolve().parent
if str(parentDir) not in sys.path:
    sys.path.insert(0, str(parentDir))

from MeloDawnWidget import BaseWidget


class WidgetManager(QObject):

    def __init__(self, widgetsPath):
        super().__init__()
        self.widgetsPath = widgetsPath
        self.widgets = []
        self._modules = {}

    def loadWidgets(self, context=None):  # MARK: Load Widgets
        self.stopWidgets()

        config = {}
        try:
            with open("conf.json", "r") as f:
                config = json.load(f)
        except Exception as e:
            print(f"[ERROR][WidgetManager] Failed to load conf.json: {e}")

        for folder in os.listdir(self.widgetsPath):
            widgetDir = os.path.join(self.widgetsPath, folder)
            if not os.path.isdir(widgetDir):
                continue

            widgetConfig = config.get(folder, {})
            if isinstance(widgetConfig, dict) and not widgetConfig.get("enabled", False):
                print(f"[INFO][WidgetManager] Skipping disabled widget: {folder}")
                continue

            backendPath = os.path.join(widgetDir, f"{folder}.py")
            qmlPath = os.path.join(widgetDir, f"{folder}.qml")

            if not os.path.exists(backendPath):
                print(f"[INFO][WidgetManager] Skipping {folder}: no {folder}.py")
                continue

            try:
                module = self._loadModule(folder, backendPath)
                self._modules[folder] = module

                backendClass = None
                for attributeName in dir(module):
                    attr = getattr(module, attributeName)
                    if (
                        inspect.isclass(attr)
                        and issubclass(attr, BaseWidget)
                        and attr is not BaseWidget
                    ):
                        backendClass = attr
                        break

                info = getattr(
                    backendClass,
                    "WIDGET_INFO",
                    getattr(module, "WIDGET_INFO", {"name": folder, "slot": "wide"}),
                )

                name = info.get("name", folder)
                slot = info.get("slot", "wide")

                backend = None
                if hasattr(module, "init"):
                    backend = module.init(context or {})
                    print(f"[DEBUG][WidgetManager] Backend for {name}:", backend)

                widget = {
                    "id": folder,
                    "name": name,
                    "slot": slot,
                    "qml": qmlPath,
                    "backend": backend,
                }

                self.widgets.append(widget)
                print(f"[INFO][WidgetManager] Loaded: {name} ({slot})")

            except Exception as e:
                print(f"[ERROR][WidgetManager] Failed to load {folder}: {e}")

    def _loadModule(self, name, path):  # MARK: Load Module
        widgetDir = os.path.dirname(path)
        if widgetDir not in sys.path:
            sys.path.insert(0, widgetDir)

        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @Slot(str, result="QVariantList")
    def getBySlot(self, slot):
        result = []
        for w in self.widgets:
            if w["slot"] == slot:
                backendObject = w["backend"] if w["backend"] else None
                result.append({"qml": w["qml"], "backend": backendObject})
        return result

    @Slot(result="QVariantList")
    def getAll(self):
        result = []
        for w in self.widgets:
            result.append(
                {
                    "qml": w["qml"],
                    "backend": w["backend"],
                    "slot": w["slot"],
                    "name": w["name"],
                }
            )
        return result

    def getById(self, widgetID):
        for w in self.widgets:
            if w["id"] == widgetID:
                return w
        return None

    def reloadWidget(self, widgetID, context=None):  # MARK: Reload Widget
        widget = self.getById(widgetID)
        if not widget:
            print(f"[ERROR][WidgetManager] No widget with id {widgetID}")
            return

        backendPath = os.path.join(self.widgetsPath, widgetID, f"{widgetID}.py")

        try:  # clean up old instances
            if widget.get("backend") and hasattr(widget["backend"], "cleanup"):
                widget["backend"].cleanup()

            module = self._loadModule(widgetID, backendPath)
            self._modules[widgetID] = module

            if hasattr(module, "init"):
                widget["backend"] = module.init(context or {})

            print(f"[INFO][WidgetManager] Reloaded: {widgetID}")

        except Exception as e:
            print(f"[ERROR][WidgetManager] Failed to reload {widgetID}: {e}")

    def stopWidgets(self):  # MARK: Stop Widgets
        """Safely cleans up and shuts down all active widget backends."""
        for w in self.widgets:
            if w.get("backend") and hasattr(w["backend"], "cleanup"):
                try:
                    w["backend"].cleanup()
                except Exception as e:
                    print(f"[ERROR][WidgetManager] Error during cleanup of {w['id']}: {e}")
        self.widgets.clear()
        print("[INFO][WidgetManager] All widgets stopped and cleaned up.")
