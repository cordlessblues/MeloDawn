from pathlib import Path
import sys

parentDir = Path(__file__).resolve().parent.parent
if str(parentDir) not in sys.path:
    sys.path.insert(0, str(parentDir))

from Bricks import BrickModel
from Cava import CavaPlayer
from MeloDawnWidget import BaseWidget
from Midi import MidiPlayer
from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot
import random


class AudioVisualiserBackend(BaseWidget):  # MARK: Backend
    WIDGET_INFO = {"name": "AudioVisualiser", "slot": "bottom"}

    audioPlaybackTriggered = Signal(bool)
    audioSourceChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.brickModel = BrickModel()
        self._bricks = []
        self._audioSource = ""
        self._mediaIndex = 0

        self.midiPlayer = MidiPlayer(updateCallback=self.handleEngineUpdate)
        self.cavaPlayer = CavaPlayer(updateCallback=self.handleEngineUpdate)
        self.activePlayer = self.midiPlayer

        self._timer = QTimer(self)
        self._timer.setInterval(0)
        self._timer.timeout.connect(self.updateTick)
        self._timer.start()

        self.loadRandomMedia()

    @Property(QObject, constant=True)
    def model(self):
        return self.brickModel

    @Property(str, notify=audioSourceChanged)
    def audioSource(self):
        return self._audioSource

    def setAudioSource(self, source: str):
        if self._audioSource != source:
            self._audioSource = source
            self.audioSourceChanged.emit()

    def handleEngineUpdate(self, newBricks):
        self._bricks = newBricks
        self.brickModel.updateBricks(newBricks)

    def updateTick(self):
        if self.activePlayer:
            self.activePlayer.updateFrame()

    @Slot(str, bool)
    def loadMedia(self, filepath: str, play=False):
        if filepath.startswith("file://"):
            filepath = QUrl(filepath).toLocalFile()

        ext = Path(filepath).suffix.lower()
        if ext in [".mid", ".midi"]:
            self.activePlayer = self.midiPlayer
            self.setAudioSource("")
        else:
            self.activePlayer = self.cavaPlayer
            self.setAudioSource(QUrl.fromLocalFile(filepath).toString())

        print(f"loaded {Path(filepath).name}")
        self.activePlayer.loadMedia(filepath, play)
        self.audioPlaybackTriggered.emit(play)

    @Slot()
    def loadRandomMedia(self):
        try:
            resourcesDir = Path(__file__).resolve().parent / "Resources"
            mediaFiles = (
                list(resourcesDir.glob("*.mid"))
                + list(resourcesDir.glob("*.mp3"))
                + list(resourcesDir.glob("*.wav"))
            )

            if not mediaFiles:
                return

            self._mediaIndex = random.randrange(0, len(mediaFiles))
            chosenFile = mediaFiles[self._mediaIndex]
            self.loadMedia(str(chosenFile), play=False)
        except Exception as e:
            print(f"[Backend] Failed to load random media: {e}")

    @Slot()
    def play(self):
        if self.activePlayer:
            self.activePlayer.play()
            self.audioPlaybackTriggered.emit(True)

    @Slot()
    def stop(self):
        if self.activePlayer:
            self.activePlayer.stop()
            self.audioPlaybackTriggered.emit(False)

    @Slot()
    def next(self):
        try:
            resourcesDir = Path(__file__).resolve().parent / "Resources"
            mediaFiles = (
                list(resourcesDir.glob("*.mid"))
                + list(resourcesDir.glob("*.mp3"))
                + list(resourcesDir.glob("*.wav"))
            )
            if not mediaFiles:
                return
            self._mediaIndex = (self._mediaIndex + 1) % len(mediaFiles)
            self.loadMedia(str(mediaFiles[self._mediaIndex]), play=False)
        except Exception as e:
            print(f"[Backend] Error in next(): {e}")

    @Slot()
    def previous(self):
        try:
            resourcesDir = Path(__file__).resolve().parent / "Resources"
            mediaFiles = (
                list(resourcesDir.glob("*.mid"))
                + list(resourcesDir.glob("*.mp3"))
                + list(resourcesDir.glob("*.wav"))
            )
            if not mediaFiles:
                return
            self._mediaIndex = (self._mediaIndex - 1) % len(mediaFiles)
            self.loadMedia(str(mediaFiles[self._mediaIndex]), play=False)
        except Exception as e:
            print(f"[Backend] Error in previous(): {e}")

    def cleanup(self):
        self.stop()
        self._timer.stop()


def init(context=None):
    return AudioVisualiserBackend()


if __name__ == "__main__":  # MARK: Unit Test
    AudioVisualiserBackend.standalone()
