from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer, QAbstractListModel, Qt, QModelIndex, QUrl
import mido
import time
import subprocess
import random
import json
import sys
from pathlib import Path
import pygame

parentDir = Path(__file__).resolve().parent.parent
if str(parentDir) not in sys.path:
    sys.path.insert(0, str(parentDir))

from ColorUtils import ColorPallete

mido.set_backend('mido.backends.rtmidi')

pygame.mixer.init()


class BrickModel(QAbstractListModel): # MARK: Bricks
    TrackIndexRole = Qt.UserRole + 1
    ActiveRole = Qt.UserRole + 2
    WidthRole = Qt.UserRole + 3
    HeightRole = Qt.UserRole + 4
    ScaleYRole = Qt.UserRole + 5
    VelocityRole = Qt.UserRole + 6
    TrackCountRole = Qt.UserRole + 7
    MessagesRole = Qt.UserRole + 8
    TrackLabelRole = Qt.UserRole + 9

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
        if role == self.MessagesRole:
            return brick["messages"]
        if role == self.TrackLabelRole:
            return brick["trackLabel"]

    def roleNames(self):
        return {
            self.TrackIndexRole: b"trackIndex",
            self.ActiveRole: b"active",
            self.WidthRole: b"width",
            self.HeightRole: b"height",
            self.ScaleYRole: b"scaleY",
            self.VelocityRole: b"velocity",
            self.TrackCountRole: b"trackCount",
            self.MessagesRole: b"messages",
            self.TrackLabelRole: b"trackLabel",
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


class Backend(QObject): # MARK: Backend
    bricksChanged = Signal()
    lyricsSegmentsChanged = Signal()
    metaMessagesChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.brickModel = BrickModel()
        self._bricks = []
        self._lyricSegments = []
        self._currentLyricLine = ""
        self._pitchValues = {}
        self._velocities = {}
        self._validTracks = []
        self._trackLabels = {}
        self._midiFile = None
        self._midi = None
        self._events = []
        self._eventIndex = 0
        self._startTime = 0.0
        self._running = False
        self._outport = None
        self._timidityProcess = None
        self._midiIndex = 0

        self._audioFilePath = None

        self._isDebug = False
        self._trackMessages = {}
        self._metaMessages = []

        self._timer = QTimer()
        self._timer.setInterval(0)
        self._timer.timeout.connect(self.update)

    @Property("QVariantList", notify=bricksChanged)
    def bricks(self):
        return self._bricks

    @Property("QVariantList", notify=metaMessagesChanged)
    def metaMessages(self):
        return self._metaMessages

    @Property(QObject, constant=True)
    def model(self):
        return self.brickModel

    @Property("QVariantList", notify=lyricsSegmentsChanged)
    def lyricsSegments(self):
        return self._lyricSegments

    @Slot()
    def load_random_midi(self):
        try:
            resourcesDir = Path(__file__).resolve().parent / "Resources"
            midiFiles = list(resourcesDir.glob("*.mid"))

            if not midiFiles:
                return

            self._midiIndex = random.randrange(0, len(midiFiles))
            chosenFile = midiFiles[self._midiIndex]

            fileUrl = QUrl.fromLocalFile(str(chosenFile)).toString()
            self.load_midi(fileUrl, False)
        except Exception as e:
            pass

    @Slot(str)
    def load_midi(self, filepath: str, play = True): # MARK: Load
        try:
            self.stop()

            if filepath.startswith("file://"):
                filepath = QUrl(filepath).toLocalFile()

            self._midi = mido.MidiFile(filepath)
            self.ticksPerBeat = self._midi.ticks_per_beat
            self._midiFile = filepath
            
            self._midiStem = Path(filepath).stem
            print(f"selected: {self._midiStem}")
            self._precompute_events()

            resourcesDir = Path(__file__).resolve().parent / "Resources"
            overridePath = resourcesDir / "overrides.json"
            audioOverridesDir = resourcesDir / "AudioOverrides"
            
            self._audioFilePath = None

            if overridePath.exists():
                try:
                    with open(overridePath, "r", encoding="utf-8") as f:
                        allOverrides = json.load(f)
                        songConfig = allOverrides.get(self._midiStem, {})
                        audioFilename = songConfig.get("audioFile")
                        if audioFilename:
                            potentialAudio = audioOverridesDir / audioFilename
                            if potentialAudio.exists():
                                self._audioFilePath = potentialAudio
                                print(f"[Backend] Found audio override: {potentialAudio}")
                except Exception as e:
                    print(f"[Backend] Failed to parse audio override in overrides.json: {e}")

            self._trackLabels = {}
            for ti, track in enumerate(self._midi.tracks):
                trackName = None
                instramentName = None
                for msg in track:
                    if msg.is_meta:
                        if msg.type == 'track_name' and getattr(msg, 'name', '').strip():
                            trackName = msg.name.strip()
                        elif msg.type in ('instrument_name', 'device_name') and getattr(msg, 'name', '').strip():
                            instramentName = msg.name.strip()
                
                if trackName and instramentName:
                    self._trackLabels[ti] = f"Track {ti} ({trackName} - {instramentName})"
                elif trackName:
                    self._trackLabels[ti] = f"Track {ti} ({trackName})"
                elif instramentName:
                    self._trackLabels[ti] = f"Track {ti} ({instramentName})"
                else:
                    self._trackLabels[ti] = f"Track {ti}"

            self._metaMessages.clear()
            self.metaMessagesChanged.emit()

            self._lyricSegments = []
            self.lyricsSegmentsChanged.emit()

            self._validTracks = [
                trackIndex for trackIndex, track in enumerate(self._midi.tracks)
                if any(not msg.is_meta and msg.type in ["note_on", "note_off"] for msg in track)
            ]

            if not self._validTracks:
                self._validTracks = list(range(len(self._midi.tracks)))

            self._trackMessages = {ti: [] for ti in self._validTracks}
            self._pitchValues = {ti: 0 for ti in self._validTracks}
            self._velocities = {ti: 0 for ti in self._validTracks}

            self._startTime = 0.0
            self._running = False
            self._eventIndex = 0
        except Exception as e:
            print(f"[Backend] Error loading MIDI: {e}")
            return
        
        if play: 
            self.play()

    def _precompute_events(self): # MARK: PrecompEvents
        self._events = []

        defaultTempo = 500000
        firstTempoFound = False
        for trackIndex, track in enumerate(self._midi.tracks):
            for msg in track:
                if msg.type.lower() == "set_tempo":
                    defaultTempo = msg.tempo
                    firstTempoFound = True
                    break
            if firstTempoFound:
                break

        for trackIndex, track in enumerate(self._midi.tracks):
            absTicks = 0
            absSeconds = 0.0
            tempo = defaultTempo

            for msg in track:
                deltaTicks = msg.time
                absTicks += deltaTicks

                deltaSec = mido.tick2second(deltaTicks, self._midi.ticks_per_beat, tempo)
                absSeconds += deltaSec

                if msg.type.lower() == "set_tempo":
                    tempo = msg.tempo
                self._events.append((absSeconds, msg, trackIndex))

        self._events.sort(key=lambda e: e[0])

    def _formatMIDIMessage(self, t, msg): # MARK: FormatMessage
        mtype = msg.type
        if mtype in ("note_on", "note_off"):
            noteStr = str(msg.note).rjust(3)
            velocityStr = str(msg.velocity).rjust(3)
            return f"[{t:5.2f}s] {mtype:<9} ({noteStr}) [{velocityStr}]"
        elif mtype == "pitchwheel":
            pitchStr = str(msg.pitch).rjust(6)
            return f"[{t:5.2f}s] pitchwheel  [{pitchStr}]"
        elif mtype == "control_change":
            controlStr = str(msg.control).rjust(3)
            valueStr = str(msg.value).rjust(3)
            return f"[{t:5.2f}s] cc ({controlStr})      [{valueStr}]"
        elif mtype == "program_change":
            programStr = str(msg.program).rjust(3)
            return f"[{t:5.2f}s] prog_change    [{programStr}]"
        elif mtype == "set_tempo":
            return f"[{t:5.2f}s] tempo       [{msg.tempo}]"
        elif mtype in ("lyrics", "text"):
            textValue = getattr(msg, 'text', '').replace('\x00', '').strip()
            return f"[{t:5.2f}s] {mtype}: \"{textValue}\""
        else:
            return f"[{t:5.2f}s] {msg}"

    @Slot()
    def play(self):
        if self._midiFile is None:
            return

        if self._timidityProcess:
            self._timidityProcess.terminate()
            self._timidityProcess = None

        resourcesDir = Path(__file__).resolve().parent / "Resources"
        soundfontsDir = resourcesDir / "SoundFonts"
        overridePath = resourcesDir / "overrides.json"

        overrideConfig = {}
        if overridePath.exists():
            try:
                with open(overridePath, "r", encoding="utf-8") as f:
                    allOverrides = json.load(f)
                    overrideConfig = allOverrides.get(self._midiStem, {})
            except Exception as e:
                print(f"[Backend] Failed to parse override.json: {e}")

        if self._audioFilePath:
            cmd = ["timidity", "-iA", "-OO", "-A 0"]
        else:
            cmd = ["timidity", "-iA", "-OO", "-A 80"]
            
            configFilename = overrideConfig.get("soundFontConfig")
            soundfontFilename = overrideConfig.get("soundFont")

            configFilePath = None
            if configFilename:
                potentialConfig = soundfontsDir / configFilename
                if potentialConfig.exists():
                    configFilePath = potentialConfig
            elif soundfontFilename:
                potentialConfig = soundfontsDir / Path(soundfontFilename).with_suffix(".cfg")
                if potentialConfig.exists():
                    configFilePath = potentialConfig

            if configFilePath and configFilePath.exists():
                cmd.extend(["-c", str(configFilePath)])
            elif soundfontFilename:
                soundfontPath = soundfontsDir / soundfontFilename
                if soundfontPath.exists():
                    cmd.extend(["--config-string=soundfont " + str(soundfontPath)])

        cmd.append(str(self._midiFile))
        self._timidityProcess = subprocess.Popen(cmd)
        time.sleep(0.5)

        if self._audioFilePath:
            try:
                pygame.mixer.music.load(str(self._audioFilePath))
                pygame.mixer.music.play()
            except Exception as e:
                print(f"[Backend] Failed to play pygame audio override: {e}")

        outputs = mido.get_output_names()
        if len(outputs) > 1:
            self._outport = mido.open_output(outputs[1])
        elif outputs:
            self._outport = mido.open_output(outputs[0])

        self._startTime = time.perf_counter()
        self._running = True
        self._timer.start()

    @Slot()
    def stop(self):
        self._running = False
        self._timer.stop()
        self._audioFilePath = None

        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

        if self._timidityProcess:
            try:
                self._timidityProcess.terminate()
                self._timidityProcess.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                self._timidityProcess.kill()
            except Exception:
                pass
            self._timidityProcess = None

        if self._outport:
            try:
                self._outport.close()
            except Exception:
                pass
            self._outport = None

    @Slot()
    def update(self):
        if not self._running or self._midi is None:
            return

        elapsed = time.perf_counter() - self._startTime
        newBricks = []

        while self._eventIndex < len(self._events):
            t, msg, trackIndex = self._events[self._eventIndex]

            if t > elapsed:
                break

            if not msg.is_meta:
                try:
                    if self._outport:
                        self._outport.send(msg)
                except Exception:
                    pass
            
            if self._isDebug:
                formattedMsg = self._formatMIDIMessage(t, msg)
                if trackIndex in self._trackMessages:
                    self._trackMessages[trackIndex].append(formattedMsg)
                    if len(self._trackMessages[trackIndex]) > 120:
                        self._trackMessages[trackIndex].pop(0)
                else:
                    self._metaMessages.append(f"T{trackIndex}|{formattedMsg}")
                    if len(self._metaMessages) > 120:
                        self._metaMessages.pop(0)

            if msg.type == "pitchwheel":
                if trackIndex in self._pitchValues:
                    self._pitchValues[trackIndex] = msg.pitch

            elif msg.type == "note_on":
                if trackIndex in self._velocities:
                    self._velocities[trackIndex] = msg.velocity if msg.velocity > 0 else 0

            elif msg.type == "end_of_track":
                if trackIndex in self._validTracks:
                    self._validTracks.remove(trackIndex)
                print(f"track {trackIndex+1} finished")

            elif msg.type == "note_off":
                if trackIndex in self._velocities:
                    self._velocities[trackIndex] = 0

            if msg.type in ("lyrics", "text"):
                raw = msg.text.replace("\x00", "")

                if raw.startswith("@"):
                    self._eventIndex += 1
                    continue

                raw = raw.replace("\r", "").replace("\n", " ").strip()
                if not raw:
                    self._eventIndex += 1
                    continue

                if raw.startswith("/") or raw.startswith("\\"):
                    self._lyricSegments = [raw[1:].strip()]
                else:
                    self._lyricSegments.append(raw)
                    if len(self._lyricSegments) > 12:
                        self._lyricSegments.pop(0)

                self.lyricsSegmentsChanged.emit()

            self._eventIndex += 1

        numValid = len(self._validTracks)
        totalCols = (numValid + 1) if self._isDebug else numValid

        if self._isDebug:
            newBricks.append({
                "trackIndex": "Meta",
                "trackLabel": "META / LYRICS",
                "active": False,
                "width": 50,
                "height": 20,
                "scaleY": 1.0,
                "velocity": 0.0,
                "trackCount": totalCols,
                "messages": list(self._metaMessages)
            })

        for trackIndex in self._validTracks:
            active = any(
                0 <= elapsed - e[0] < 0.1 and e[2] == trackIndex and e[1].type in ["note_on", "note_off"]
                for e in self._events
            )

            stretch = 1.0 + (self._pitchValues.get(trackIndex, 0) / 8192.0 * 0.5)
            vel = self._velocities.get(trackIndex, 0) / 127.0
            newBricks.append({
                "trackIndex": trackIndex,
                "trackLabel": self._trackLabels.get(trackIndex, f"Track {trackIndex}"),
                "active": active,
                "width": 50,
                "height": 20,
                "scaleY": stretch,
                "velocity": vel,
                "trackCount": totalCols,
                "messages": list(self._trackMessages.get(trackIndex, []))
            })

        self.brickModel.updateBricks(newBricks)

        if self._events and elapsed > self._events[-1][0]:
            self.stop()

    @Slot()
    def next(self):
        try:
            resourcesDir = Path(__file__).resolve().parent / "Resources"
            midiFiles = list(resourcesDir.glob("*.mid"))

            if not midiFiles:
                return

            self._midiIndex = (self._midiIndex + 1) % len(midiFiles)
            chosenFile = midiFiles[self._midiIndex]
            fileUrl = QUrl.fromLocalFile(str(chosenFile)).toString()
            self.load_midi(fileUrl, False)
        except Exception as e:
            pass
    
    @Slot()
    def previous(self):
        try:
            resourcesDir = Path(__file__).resolve().parent / "Resources"
            midiFiles = list(resourcesDir.glob("*.mid"))

            if not midiFiles:
                return

            self._midiIndex = (self._midiIndex - 1) % len(midiFiles)
            chosenFile = midiFiles[self._midiIndex]
            fileUrl = QUrl.fromLocalFile(str(chosenFile)).toString()
            self.load_midi(fileUrl, False)
        except Exception as e:
            pass
        

# MARK: Metadata & Init
WIDGET_INFO = {"name": "midi", "slot": "bottom"}
def init(context=None): return Backend()

if __name__ == "__main__": # MARK: Unit Test
    import sys, os
    from PySide6.QtCore import Qt, QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQuick import QQuickView
    
    parentDir = Path(__file__).resolve().parent.parent
    if str(parentDir) not in sys.path:
        sys.path.insert(0, str(parentDir))
    from ColorUtils import ColorPallete

    app = QGuiApplication(sys.argv)
    backend = init()
    backend._isDebug = True

    pallete = ColorPallete()
    
    view = QQuickView()
    view.setColor(Qt.transparent)
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.rootContext().setContextProperty("backend", backend)
    view.rootContext().setContextProperty("isDebugMode", backend._isDebug)
    view.rootContext().setContextProperty("sysColorPallete", pallete)

    qmlFile = os.path.join(os.path.dirname(__file__), "Midi.qml")
    view.setSource(QUrl.fromLocalFile(qmlFile))

    rootItem = view.rootObject()
    if not rootItem:
        sys.exit("Failed to load QML frontend")

    rootItem.setProperty("backend", backend)
    rootItem.setProperty("isDebugMode", backend._isDebug)

    view.setWidth(1280)
    view.setHeight(720)
    view.show()

    def cleanup():
        backend.stop()

    app.aboutToQuit.connect(cleanup)
    sys.exit(app.exec())