import os
from pathlib import Path
import subprocess
import tempfile
import threading


class CavaPlayer:

    def __init__(self, updateCallback=None):
        self.updateCallback = updateCallback
        self._running = False
        self._process = None
        self._thread = None
        self._audioFilePath = None
        self._latestBricks = []

        # MARK: cava Config Vars
        self.numBars = 64
        self.stereo = False
        self.reversed = True
        self._configPath = self._create_cava_config()

    def _create_cava_config(self):
        configContent = f"""
[general]
bars = {self.numBars}
framerate = 60
autosens = 1
mono_option = average


[input]
method = pipewire
source = auto

[smoothing]
monstercat = 0
waves = 1
noise_reduction = 50

[output]
channels = {"stereo" if self.stereo else "mono" }
reverse = {1 if self.reversed else 0}
method = raw
data_format = ascii
bar_delimiter = 59
frame_delimiter = 10
"""
        fd, path = tempfile.mkstemp(prefix="cavaConfig", suffix=".conf")
        with os.fdopen(fd, "w") as f:
            f.write(configContent)
        return path

    def loadMedia(self, filepath: str, play=False):
        self._audioFilePath = filepath
        self._latestBricks = []
        if play:
            self.play()

    def play(self):
        if self._running:
            return
        self._running = True

        try:
            # Removed DEVNULL temporarily so you can see if cava outputs any config errors to your console!
            self._process = subprocess.Popen(
                ["cava", "-p", self._configPath],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            self._thread = threading.Thread(target=self._readCavaOutput, daemon=True)
            self._thread.start()
        except Exception as e:
            print(f"[ERROR][CavaPlayer] Failed to start cava (is cava installed?): {e}")

    def stop(self):
        self._running = False
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=0.5)
            except Exception:
                pass
            self._process = None

    def _readCavaOutput(self):
        while self._running and self._process and self._process.stdout:
            line = self._process.stdout.readline()
            if not line:
                if self._process.stderr:
                    err = self._process.stderr.read()
                    if err:
                        print(f"[ERROR][CavaPlayer][CavaSubprocess] {err}")
                break

            line = line.strip()
            if not line:
                continue

            parts = line.split(";")
            trackBricks = []

            for i, valStr in enumerate(parts):
                if not valStr:
                    continue
                try:
                    rawVal = int(valStr)
                except ValueError:
                    rawVal = 0

                velocity = min(8.0, rawVal / 1000.0)
                active = velocity > 0.04

                scaleY = velocity

                trackBricks.append(
                    {
                        "trackIndex": i,
                        "active": active,
                        "velocity": velocity,
                        "scaleY": scaleY,
                        "messages": [f"{rawVal}"],
                        "type": "cava",
                    }
                )

            if trackBricks and self.updateCallback:
                self._latestBricks = trackBricks

    def updateFrame(self):
        if self._running and self._latestBricks and self.updateCallback:
            self.updateCallback(self._latestBricks)
