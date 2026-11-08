import json
from pathlib import Path
import random
import subprocess
import time

import mido
import pygame

mido.set_backend("mido.backends.rtmidi")
pygame.mixer.init()


class MidiPlayer:

    def __init__(self, updateCallback=None):
        self.updateCallback = updateCallback
        self._midiFile = None
        self._midi = None
        self._events = []
        self._eventIndex = 0
        self._startTime = 0.0
        self._running = False
        self._outport = None
        self._timidityProcess = None
        self._audioFilePath = None
        self._pitchValues = {}
        self._velocities = {}
        self._validTracks = []
        self._trackMessages = {}
        self._trackLabels = {}
        self._midiStem = ""

    def loadMedia(self, filepath: str, play=True):
        try:
            self.stop()
            self._midi = mido.MidiFile(filepath)
            self.ticksPerBeat = self._midi.ticks_per_beat
            self._midiFile = filepath
            self._midiStem = Path(filepath).stem

            self._precomputeEvents()

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
                except Exception as e:
                    print(f"[MidiPlayer] Failed to parse overrides: {e}")

            self._validTracks = [
                ti
                for ti, track in enumerate(self._midi.tracks)
                if any(
                    not msg.is_meta and msg.type in ["note_on", "note_off"]
                    for msg in track
                )
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
            print(f"[MidiPlayer] Error loading MIDI: {e}")
            return

        if play:
            self.play()

    def _precomputeEvents(self):
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
                deltaSec = mido.tick2second(
                    deltaTicks, self._midi.ticks_per_beat, tempo
                )
                absSeconds += deltaSec
                if msg.type.lower() == "set_tempo":
                    tempo = msg.tempo
                self._events.append((absSeconds, msg, trackIndex))

        self._events.sort(key=lambda e: e[0])

    def play(self):
        if self._midiFile is None:
            return

        if self._timidityProcess:
            self._timidityProcess.terminate()
            self._timidityProcess = None

        cmd = ["timidity", "-iA", "-OO", "-A 80"]
        cmd.append(str(self._midiFile))
        self._timidityProcess = subprocess.Popen(cmd)
        time.sleep(0.5)

        if self._audioFilePath:
            try:
                pygame.mixer.music.load(str(self._audioFilePath))
                pygame.mixer.music.play()
            except Exception as e:
                print(f"[MidiPlayer] Failed to play pygame audio: {e}")

        outputs = mido.get_output_names()
        if len(outputs) > 1:
            self._outport = mido.open_output(outputs[1])
        elif outputs:
            self._outport = mido.open_output(outputs[0])

        self._startTime = time.perf_counter()
        self._running = True

    def stop(self):
        self._running = False
        self._audioFilePath = None

        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

        if self._timidityProcess:
            try:
                self._timidityProcess.terminate()
                self._timidityProcess.wait(timeout=0.5)
            except Exception:
                subprocess.call(["killall", "timidity"])
                pass
            self._timidityProcess = None

        if self._outport:
            try:
                self._outport.close()
            except Exception:
                pass
            self._outport = None

    def updateFrame(self):
        if not self._running or self._midi is None:
            return

        elapsed = time.perf_counter() - self._startTime
        newBricks = []

        while self._eventIndex < len(self._events):
            t, msg, trackIndex = self._events[self._eventIndex]
            if t > elapsed:
                break

            if not msg.is_meta and self._outport:
                try:
                    self._outport.send(msg)
                except Exception:
                    pass

            if msg.type == "pitchwheel":
                if trackIndex in self._pitchValues:
                    self._pitchValues[trackIndex] = msg.pitch
            elif msg.type == "note_on":
                if trackIndex in self._velocities:
                    self._velocities[trackIndex] = int(
                        msg.velocity if msg.velocity > 0 else 0
                    )
            elif msg.type == "note_off":
                if trackIndex in self._velocities:
                    self._velocities[trackIndex] = 0

            self._eventIndex += 1

        for trackIndex in self._validTracks:
            active = any(
                0 <= elapsed - e[0] < 0.1
                and e[2] == trackIndex
                and e[1].type in ["note_on", "note_off"]
                for e in self._events
            )

            vel = self._velocities.get(trackIndex, 0)

            # pitchwheel (-8192 to 8192)
            pitch = self._pitchValues.get(trackIndex, 0)
            stretch = pitch / 8192.0

            newBricks.append(
                {
                    "trackIndex": trackIndex,
                    "active": active,
                    "velocity": vel,
                    "scaleY": stretch,
                    "messages": list(self._trackMessages.get(trackIndex, [])),
                    "type": "midi",
                }
            )

        if self.updateCallback:
            self.updateCallback(newBricks)

        if self._events and elapsed > self._events[-1][0]:
            self.stop()
