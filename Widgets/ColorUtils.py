from PySide6.QtCore import QObject, Property, Signal, QFileSystemWatcher, Slot
from pathlib import Path

class ColorPallete(QObject):
    colorsChanged = Signal()

    def __init__(self):
        super().__init__()
        self.colorPallete = {}
        self._colorPalleteFilePath = Path(__file__).resolve().parent / "ColorPallete.txt"
        self.updateColors()

        self.watcher = QFileSystemWatcher([str(self._colorPalleteFilePath)])
        self.watcher.fileChanged.connect(self.onFileChanged)
        
    
    def __str__(self):
        string = "Color Palette:\n"
        for key, value in self.colorPallete.items():
            string += f"\t{key}: {value}\n"
        return string
    
    def updateColors(self):
        try:
            with open(self._colorPalleteFilePath, "r") as file:
                new_palette = {}
                for line in file:
                    if " = " in line:
                        key, value = line.replace("\"", "").removesuffix('\n').split(" = ")
                        new_palette[key] = value if value.startswith("#") else f"#{value}"
                self.colorPallete = new_palette
        except Exception as e:
            print(f"[ColorPallete] Failed to read color palette: {e}")
        
    def onFileChanged(self, path):
        print("[ColorPallete] Palette file changed, reloading colors...")
        self.updateColors()
        self.colorsChanged.emit()
        
        if not self.watcher.files():
            self.watcher.addPath(str(self._colorPalleteFilePath))
    
    @Slot(str, str)
    def setColor(self, key, value):
        self.colorPallete[key] = value
        self.colorsChanged.emit()
    
    @Slot()
    def saveColors(self):
        with open(self._colorPalleteFilePath, "w") as file:
            for key, color in self.colorPallete.items():
                print(f'{key} = "{color if color.startswith("#") else f"#{color}"}"')

    @Property(dict, notify=colorsChanged)
    def colors(self):
        return self.colorPallete

if __name__ == "__main__":
    pallate = ColorPallete()
    pallate.saveColors()