import mido
import pygame as pg
import pygame.midi as midi
import time
import threading
from ColorUtils import *  # Assuming this is the correct import for the DynamicColor class

# Constants
WIDTH, HEIGHT = 800, 600
TEXT_COLOR = (255, 255, 255)
BG_COLOR = (0, 0, 0)
FONT_SIZE = 16
SCROLL_SPEED = 1
MAX_MESSAGES = 15

class MidiPlayer:
    def __init__(self, midi_file):
        self.midi_file = midi_file
        self.midi = mido.MidiFile(midi_file)
        self.ticks_per_beat = self.midi.ticks_per_beat
        self.default_tempo = 500000  # microseconds per quarter note
        self.tempo = self.default_tempo
        self.time_signature = (4, 4)
        self.track_states = [False] * len(self.midi.tracks)
        self.messages_to_display = []
        self.currentLyric =""
        self.font = None
        self.running = False
        self.events = []  # Precomputed events

        # Color Palette
        self.colorPallete = {
            "Mauve": (203, 166, 247),
            "Red": (243, 139, 168),
            "Peach": (250, 179, 135),
            "Yellow": (249, 226, 175),
            "Green": (166, 227, 161),
            "Teal": (148, 226, 213),
            "Sky": (137, 220, 235),
            "Sapphire": (116, 199, 236),
            "Blue": (137, 180, 250),
            "Lavender": (180, 190, 254),
        }

        self.TextColor = [
            self.colorPallete["Mauve"],
            self.colorPallete["Red"],
            self.colorPallete["Peach"],
            self.colorPallete["Yellow"],
            self.colorPallete["Green"],
            self.colorPallete["Teal"],
            self.colorPallete["Sky"],
            self.colorPallete["Sapphire"],
            self.colorPallete["Blue"],
            self.colorPallete["Lavender"],
        ]
        
        pg.init()
        midi.init()

        for i in range(1,midi.get_count()):
            print(f"i:{i} | deviceinfo: {midi.get_device_info(i)[3]}")
            if midi.get_device_info(i)[3] == 1:
                device_id=i
                print(midi.get_device_info(i))
                try:
                    # Replace if needed
                    self.midi_out = midi.Output(device_id)
                except midi.MidiException as e:
                    self.midi_out = None
                    print("No MIDI output device found. Playback will be silent.")
                    print(f"device_id: {device_id}")
                    print(e)
                except Exception as e:
                    print("Midi error assigning device")
                    print(f"device_id: {device_id}")
                    print(e)
                    continue
                finally:
                    break

        self.precompute_events()

    def precompute_events(self):
        self.events = []
        tempo = self.default_tempo
        for track_index, track in enumerate(self.midi.tracks):
            abs_time = 0
            ticks = 0

            for msg in track:
                ticks += msg.time
                seconds = mido.tick2second(ticks, self.ticks_per_beat, tempo)
                abs_time = seconds

                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                elif msg.type == 'time_signature':
                    self.time_signature = (msg.numerator, msg.denominator)

                self.events.append((abs_time, msg, track_index))

        self.events.sort(key=lambda e: e[0])  # Sort by absolute time

    def add_message_to_display(self, message):
        self.messages_to_display.append(message)
        if len(self.messages_to_display) > MAX_MESSAGES:
            self.messages_to_display.pop(0)

    def getTrackState(self):
        return self.track_states
    
    def play(self):
        def _play():
            self.running = True
            start_time = time.perf_counter()
            for abs_time, msg, track_index in self.events:
                if not self.running:
                    break
                # Wait until the appropriate time to play the next event
                wait_time = abs_time - (time.perf_counter() - start_time)
                if wait_time > 0:
                    time.sleep(wait_time)
                if msg.type == 'set_tempo':
                    self.tempo = msg.tempo
                    continue
                if msg.type == 'text':
                    lyric_text = msg.text

                    # Check if this is a new section (e.g., verse, chorus)
                    if lyric_text.startswith("@"):
                        self.currentLyric = ""  # Clear previous lyrics

                    # Clean up the lyric text
                    lyric_text = lyric_text.replace("@T ", "TITLE: ").replace("@L", "LANG: ").replace("\\", "")

                    # Append the cleaned-up lyric text to the current lyric
                    self.currentLyric += lyric_text

                    # Split lyric if / in string
                    if "/" in self.currentLyric:
                        self.currentLyric = self.currentLyric.split("/")[1]

                    #print(f"Current Lyric: {self.currentLyric}")  # Debugging
                    continue
                if msg.type in {'note_on', 'note_off'}:
                    # Update the track state based on whether the note is on or off
                    if msg.type == 'note_on' and msg.velocity > 0:
                        self.track_states[track_index] = True  # Note is on
                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        self.track_states[track_index] = False  # Note is off
                    # Add the message to display for debugging or info
                    self.add_message_to_display(f"Track {track_index}: {msg}")
                if self.midi_out:
                    try:
                        if msg.type in {'note_on', 'note_off'}:
                            status_byte = 0x90 if msg.type == 'note_on' else 0x80
                            if msg.velocity == 0 and msg.type == 'note_on':
                                status_byte = 0x80
                            self.midi_out.write_short(status_byte | msg.channel, msg.note, msg.velocity)
                        elif msg.type == 'control_change':
                            self.midi_out.write_short(0xB0 | msg.channel, msg.control, msg.value)
                        elif msg.type == 'program_change':
                            self.midi_out.write_short(0xC0 | msg.channel, msg.program)
                    except Exception as e:
                        print(f"Error sending MIDI: {e}")
            self.running = False
            if self.midi_out:
                del self.midi_out
            midi.quit()

        threading.Thread(target=_play, daemon=True).start()

    def draw_bricks(self):
        self.bricks = []  # Clear bricks each frame
        track_count = len(self.track_states)  # Total number of tracks
        if track_count == 0:
            return  # No tracks, no bricks

        brick_width = self.screen.get_width() / track_count
        brick_height = 20  # Fixed height for the bar
        screen_height = self.screen.get_height()

        # Loop through all tracks and draw their corresponding brick
        for i, track_active in enumerate(self.track_states):
            track_color = self.TextColor[i % len(self.TextColor)]

            # Create a DynamicColor object to handle the color fading
            dynamic_color = DynamicColor(C=track_color)

            if track_active:  # Track is active (note playing)
                # If the track is active, keep the original color
                dynamic_color.setTargetColor(track_color)
            else:  # Track is inactive (note off)
                # Fade to black (darken the color) when the track is inactive
                darkened_color = blendColors(track_color, (0, 0, 0), 0.8)  # Blend towards black
                dynamic_color.setTargetColor(darkened_color)

            # Update the dynamic color based on the update rate and delta time
            dynamic_color.Update(updateRate=1.0, deltaTime=1.0)
            current_color = dynamic_color.getColor()

            # Calculate the x position and draw the rectangle (brick)
            x = i * brick_width
            y = screen_height - brick_height

            # Append the brick (a filled rectangle with current color)
            self.bricks.append(
                (current_color, (x, y, brick_width, brick_height))
            )

    def stop(self):
        self.running = False

    def getDuration(self): return self.events[len(self.events)-1][0]
    
    def getCurrentLyric(self): return self.currentLyric
    def run(self):
        self.play()
        clock = pg.time.Clock()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
            self.draw_bricks()  # Update bricks based on track states
            self.draw()  # Draw everything
            clock.tick(60)  # FPS

if __name__ == '__main__':
    midi_file = 'python/MidiToAlarm/MidiFiles/TheFinalCountdown.mid'  # Replace with your file path
    player = MidiPlayer(midi_file)
    player.run()
