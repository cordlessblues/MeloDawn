import os
import importlib.util
from PySide6.QtCore import QObject, Slot

class WidgetManager(QObject):
    def __init__(self, widgets_path):
        super().__init__()
        self.widgetsPath = widgets_path
        self.widgets = []
        self._modules = {}

    def loadWidgets(self, context=None): # MARK: Load Widgets
        self.widgets.clear()

        for folder in os.listdir(self.widgetsPath):
            widgetDir = os.path.join(self.widgetsPath, folder)
            if not os.path.isdir(widgetDir):
                continue

            backendPath = os.path.join(widgetDir, f"{folder}.py")
            qmlPath = os.path.join(widgetDir, f"{folder}.qml")

            if not os.path.exists(backendPath):
                print(f"[WidgetManager] Skipping {folder}: no {folder}.py")
                continue

            try:
                module = self._loadModule(folder, backendPath)
                self._modules[folder] = module

                info = getattr(module, "WIDGET_INFO")
                name = info.get("name", folder)
                slot = info.get("slot", "wide")

                backend = None
                if hasattr(module, "init"):
                    backend = module.init(context or {})
                    print(f"[WidgetManager] Backend for {name}:", backend)
                widget = {
                    "id": folder,
                    "name": name,
                    "slot": slot,
                    "qml": qmlPath,
                    "backend": backend
                }

                self.widgets.append(widget)
                print(f"[WidgetManager] Loaded: {name} ({slot})")

            except Exception as e:
                print(f"[WidgetManager] Failed to load {folder}: {e}")

    def _loadModule(self, name, path): # MARK: Load Module
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @Slot(str, result='QVariantList')
    def getBySlot(self, slot):
        result = []
        for w in self.widgets:
            if w["slot"] == slot:
                backendObject = w["backend"] if w["backend"] else None
                result.append({
                    "qml": w["qml"],
                    "backend": backendObject
                })
        return result

    @Slot(result='QVariantList')
    def getAll(self):
        result = []
        for w in self.widgets:
            result.append({
                "qml": w["qml"],
                "backend": w["backend"],
                "slot": w["slot"],
                "name": w["name"]
            })
        return result

    def get_by_id(self, widget_id):
        for w in self.widgets:
            if w["id"] == widget_id:
                return w
        return None

    def reload_widget(self, widget_id, context=None): # MARK: Reload Widget
        widget = self.get_by_id(widget_id)
        if not widget:
            print(f"[WidgetManager] No widget with id {widget_id}")
            return

        backend_path = os.path.join(self.widgetsPath, widget_id, "backend.py")

        try:
            module = self._loadModule(widget_id, backend_path)
            self._modules[widget_id] = module

            if hasattr(module, "init"):
                widget["backend"] = module.init(context or {})

            print(f"[WidgetManager] Reloaded: {widget_id}")

        except Exception as e:
            print(f"[WidgetManager] Failed to reload {widget_id}: {e}")