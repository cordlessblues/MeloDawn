from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer, QAbstractListModel, Qt, QModelIndex, QUrl
import mido
import time
import subprocess
import random
import colorsys
from pathlib import Path

mido.set_backend('mido.backends.rtmidi')


class BrickModel(QAbstractListModel): # MARK: Bricks
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

class Backend(QObject): # MARK: Backend
    bricksChanged = Signal()
    lyricsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.brickModel = BrickModel()
        self._bricks = []
        self._lyric_segments = []
        self._current_lyric_line = ""
        self._pitch_values = {}
        self._velocities = {}
        self._valid_tracks = []
        self._track_colors = {}
        self._midi_file = None
        self._midi = None
        self._events = []
        self._event_index = 0
        self._start_time = 0.0
        self._running = False
        self._outport = None
        self._timidity_process = None

        self._timer = QTimer()
        self._timer.setInterval(0)
        self._timer.timeout.connect(self.update)

        self._sent_event_indices = set()

    @Property("QVariantList", notify=bricksChanged)
    def bricks(self):
        return self._bricks

    lyricsSegmentsChanged = Signal()

    @Property("QVariantList", notify=lyricsSegmentsChanged)
    def lyricsSegments(self):
        return self._lyric_segments

    @Property(QObject, constant=True)
    def model(self):
        return self.brickModel

    @Slot()
    def load_random_midi(self):
        """Scan the Resources directory and load a random .mid file."""
        try:
            # Locate the Resources directory relative to this script
            resources_dir = Path(__file__).resolve().parent / "Resources"
            midi_files = list(resources_dir.glob("*.mid"))

            if not midi_files:
                print("[DEBUG] No .mid files found in Resources/")
                return

            # Pick a random file
            chosen_file = random.choice(midi_files)
            print(f"[DEBUG] Randomly selected MIDI: {chosen_file.name}")

            # Load it using the existing load_midi slot
            file_url = QUrl.fromLocalFile(str(chosen_file)).toString()
            self.load_midi(file_url)

        except Exception as e:
            print(f"[DEBUG] Failed to load random MIDI: {e}")

    @Slot(str)
    def load_midi(self, filepath: str): # MARK: Load
        try:
            if filepath.startswith("file://"):
                filepath = QUrl(filepath).toLocalFile()

            print(f"[DEBUG] Loading MIDI from: {filepath}")
            self._midi = mido.MidiFile(filepath)
            self.ticks_per_beat = self._midi.ticks_per_beat
            self._midi_file = filepath
            self._precompute_events()

            # Filter out tracks that contain no note events
            self._valid_tracks = [
                track_index for track_index, track in enumerate(self._midi.tracks)
                if any(not msg.is_meta and msg.type in ["note_on", "note_off"] for msg in track)
            ]

            if not self._valid_tracks:
                self._valid_tracks = list(range(len(self._midi.tracks)))

            self._pitch_values = {ti: 0 for ti in self._valid_tracks}
            self._velocities = {ti: 0 for ti in self._valid_tracks}

            self._track_colors = {}
            for track_index in self._valid_tracks:
                hue = random.random()
                r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.5)
                self._track_colors[track_index] = [int(r*255), int(g*255), int(b*255)]

            self._start_time = 0.0
            self._running = False
            self._event_index = 0
        except Exception as e:
            print(f"[DEBUG] Failed to load MIDI: {e}")
            return

        self.play()

    def _precompute_events(self): # MARK: PrecompEvents
        self._events = []

        default_tempo = 500000
        first_tempoFound = False
        for track_index, track in enumerate(self._midi.tracks):
            for msg in track:
                if msg.type.lower() == "set_tempo":
                    default_tempo = msg.tempo
                    first_tempoFound = True
                    break
            if first_tempoFound:
                break

        for track_index, track in enumerate(self._midi.tracks):
            abs_ticks = 0
            abs_seconds = 0.0
            tempo = default_tempo

            for msg in track:
                delta_ticks = msg.time
                abs_ticks += delta_ticks

                delta_sec = mido.tick2second(delta_ticks, self._midi.ticks_per_beat, tempo)
                abs_seconds += delta_sec

                if msg.type.lower() == "set_tempo":
                    tempo = msg.tempo
                self._events.append((abs_seconds, msg, track_index))

        self._events.sort(key=lambda e: e[0])

    @Slot()
    def play(self): # MARK: Play
        print("[DEBUG] play start")

        if self._midi_file is None:
            print("[DEBUG] No MIDI file assigned, play skipped")
            return

        if self._timidity_process:
            print("[DEBUG] Killing previous Timidity process")
            self._timidity_process.terminate()
            self._timidity_process = None

        print(f"[DEBUG] Launching TiMidity++ for {self._midi_file}")
        self._timidity_process = subprocess.Popen(
            ["timidity", "-iA", str(self._midi_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(0.5)
        self._outport = mido.open_output(mido.get_output_names()[1])

        self._start_time = time.perf_counter()
        self._running = True
        self._timer.start()
        print("[DEBUG] play done")

    @Slot()
    def stop(self): # MARK: Stop
        self._running = False
        self._timer.stop()
        if self._timidity_process:
            self._timidity_process.terminate()
        print("[DEBUG] Playback stopped")

    @Slot()
    def update(self): # MARK: Update
        if not self._running or self._midi is None:
            return

        elapsed = time.perf_counter() - self._start_time
        new_bricks = []

        while self._event_index < len(self._events):
            t, msg, track_index = self._events[self._event_index]

            if t > elapsed:
                break

            if not msg.is_meta:
                try:
                    self._outport.send(msg)
                except Exception:
                    pass

            if msg.type == "pitchwheel":
                if track_index in self._pitch_values:
                    self._pitch_values[track_index] = msg.pitch

            elif msg.type == "note_on":
                if track_index in self._velocities:
                    self._velocities[track_index] = msg.velocity if msg.velocity > 0 else 0

            elif msg.type == "note_off":
                if track_index in self._velocities:
                    self._velocities[track_index] = 0

            if msg.type in ("lyrics", "text"):
                raw = msg.text.replace("\x00", "")

                if raw.startswith("@"):
                    self._event_index += 1
                    continue

                raw = raw.strip()
                if not raw:
                    self._event_index += 1
                    continue

                if raw.startswith("/") or raw.startswith("\\"):
                    self._lyric_segments = [raw[1:].strip()]
                else:
                    self._lyric_segments = self._lyric_segments + [raw]

                self.lyricsSegmentsChanged.emit()

            self._event_index += 1

        num_valid = len(self._valid_tracks)
        for track_index in self._valid_tracks:
            active = any(
                0 <= elapsed - e[0] < 0.1 and e[2] == track_index and e[1].type in ["note_on", "note_off"]
                for e in self._events
            )

            stretch = 1.0 + (self._pitch_values.get(track_index, 0) / 8192.0 * 0.5)
            vel = self._velocities.get(track_index, 0) / 127.0
            new_bricks.append({
                "color": self._track_colors[track_index],
                "trackIndex": track_index,
                "active": active,
                "width": 50,
                "height": 20,
                "scaleY": stretch,
                "velocity": vel,
                "trackCount": num_valid
            })

        self.brickModel.updateBricks(new_bricks)

        if self._events and elapsed > self._events[-1][0]:
            self.stop()

# MARK: Metadata & Init
WIDGET_INFO = {"name": "midi", "slot": "bottom"}
def init(context=None): return Backend()

if __name__ == "__main__": # MARK: Unit Test
    import sys, os
    from PySide6.QtCore import Qt, QUrl, QTimer
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQuick import QQuickView

    print("[DEBUG] __main__ start")
    app = QGuiApplication(sys.argv)

    print("[DEBUG] Creating backend")
    backend = Backend()

    view = QQuickView()
    view.setColor(Qt.transparent)
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.rootContext().setContextProperty("brickModel", backend.brickModel)
    view.rootContext().setContextProperty("backend", backend)
    qml_file = os.path.join(os.path.dirname(__file__), "midi.qml")
    print(f"[DEBUG] Loading QML frontend: {qml_file}")
    view.setSource(QUrl.fromLocalFile(qml_file))

    if not view.rootObject():
        sys.exit("[DEBUG] Failed to load QML frontend")

    view.show()

    test_file = os.path.join(
        os.path.dirname(__file__), "Resources", "SongOfStorms.mid"
    )
    print(f"[DEBUG] Test MIDI path: {test_file}")
    if os.path.exists(test_file):
        backend.load_midi(QUrl.fromLocalFile(test_file).toString())
    else:
        print(f"[DEBUG] Test MIDI not found: {test_file}")

    def cleanup():
        print("[DEBUG] App closing: cleaning up")
        backend.stop()

    app.aboutToQuit.connect(cleanup)
    print("[DEBUG] Entering Qt event loop")
    sys.exit(app.exec())