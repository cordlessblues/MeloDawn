import mido
import time
import pygame
import json
from pygame import gfxdraw
from typing import List, Dict, Any
import math
from ColorUtils import *
import threading



class Ringtone:
    def __init__(self,data):
        self.data = data
        self.Title = data["Name"]
        self.Artist = data["Artist"]
        self.filepath = data["FilePath"]
        
        self.SideTrackEnabled = False
        self.LyricsEnabled = False
        self.lyricsTrack = 0
        self.mixer = pygame.mixer
        self.SideTrackDelay = self.SideTrackDelay = data["SideTrackDelay"]
        match data["VocalTrackType"]:
            case "MuteMidi":
                self.MidiMute = True
                self.SideTrackEnabled = True
            case "SideCar":
                self.MidiMute = False
                self.SideTrackEnabled = True
                self.SideTrackDelay = data["SideTrackDelay"]
            case "Lyrics":
                self.MidiMute = False
                self.SideTrackEnabled = False
                self.LyricsEnabled = True
            case _:
                self.MidiMute = False
                self.SideTrackEnabled = False
        self.SideTrack = data["VocalsFilePath"]
        self.soundFontPath = "/usr/share/soundfonts/"+data["Soundfont"]
        self.Volume = data["Volume"]
        self.midi = mido.MidiFile(self.filepath, clip=True)
        self.tempo_microseconds_per_beat = 0
        self.CurremtTimeInTrack = 0
        self.seconds_per_beat = 0
        self.seconds_per_tick = 0
        self.CurrentLyric = ""
        self.SongTimer = None
        self.TrackDuration = []
        self.absolute_time_seconds = 0
        self.current_time_ticks = 0
        self.absolute_times: List[List[float]] = []  # List of lists!
        self.trackNames = []
        self.activeTracks = []
        self.brickColors = []  # Initialized here
        self.bricks = []
        self.IsPlaying = False
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

    def getInfo(self,p="",Child=False):
        import os
        if not Child: os.system('cls' if os.name == 'nt' else 'clear'             )
        print(f"{p}filepath:           {self.filepath}")
        print(f"{p}soundFontPath:      {self.soundFontPath}")
        print(f"{p}trackNames:         {self.trackNames}")
        print(f"{p}activeTracks:       {self.activeTracks}")
        print(f"{p}ColorPallete: "+"{")
        for color in self.colorPallete:
            print(f"{p}    {color}")
        print(f"{p}"+"}")

        
        
    def getData(self):
        return self.data
    
    def getTrackNames(self):
        if self.LyricsEnabled:
            index = 0
        for track in self.midi.tracks:
            for msg in track:
                if msg.type == "track_name":
                    if self.LyricsEnabled:
                        if msg.name == self.SideTrack:
                            self.lyricsTrack = index
                    self.trackNames.append(msg.name)
            if self.LyricsEnabled:
                index+=1
    def calculateCurrentTime(
        self
    ):  # Pass track_index
        if self.IsPlaying:
            currentTime = time.time() - self.startTime
            output = 0.0
            for trackIndex in range(self.numTracks):
                    if self.isTrackFinished[trackIndex] or trackIndex in self.ignore_tracks:
                        continue
                    
                    msgIndex = self.messageIndices[trackIndex]
                    if msgIndex < len(self.absolute_times[trackIndex]):  
                        if (currentTime>= self.absolute_times[trackIndex][msgIndex]):
                            output = currentTime
            return(currentTime)
        else:
            return(0.00)

    def calculateAbsoluteTime(
        self, ticks_per_beat: int, track: mido.MidiTrack, track_index: int
    ):  # Pass track_index
        absolute_times_for_track: List[float] = []  # Create a new list for this track
        current_time_ticks = 0  # Reset for each track
        
        for message in track:
            current_time_ticks += message.time
            if message.type == "set_tempo":
                self.tempo_microseconds_per_beat = message.tempo
            delay = 0
            if self.SideTrackDelay<0: delay = abs(self.SideTrackDelay) 
            self.seconds_per_beat = self.tempo_microseconds_per_beat / 1000000.0
            self.seconds_per_tick = self.seconds_per_beat / ticks_per_beat
            self.absolute_time_seconds = current_time_ticks * self.seconds_per_tick
            absolute_times_for_track.append(self.absolute_time_seconds + delay)

        self.absolute_times.append(
            absolute_times_for_track
        )  # Append the list for the track
        

    
    def play_side_track(self,side_track, volume,delay):
        """Plays the side track on a separate channel."""
        if delay < 0.0: delay=0.0
        SideChannel = self.mixer.Channel(0)
        Track = self.mixer.Sound(side_track)
        SideChannel.set_volume(volume)
        time.sleep(delay)
        SideChannel.play(Track)
    
    def Stop(self):
        self.mixer.stop()
        self.IsPlaying = False
    
    def play(self, volume=1.0):
        self.SongTimer 
        import os
        os.environ["SDL_SOUNDFONTS"] = self.soundFontPath
        filename = self.filepath.split("/")[len(self.filepath.split("/")) - 1]
        print(f"loaded {filename}")

        self.numTracks = len(self.midi.tracks)
        self.isTrackFinished = [False] * self.numTracks
        self.trackMessages = [[] for _ in range(self.numTracks)]
        self.startTime = time.time()
        self.clock = pygame.time.Clock()
        self.IsPlaying = True
        self.brickState = [False] * self.numTracks
        self.messageIndices = [0] * self.numTracks
        self.brickColors = []
        self.get_ignore_tracks()
        for i in range(len(self.midi.tracks)):  # Initialize brickColors
            self.brickColors.append(
                DynamicColor(
                    0.5,
                    0.5,
                    self.TextColor[i % len(self.TextColor)],
                    (0, 0, 0),
                    (0, 0, 0),
                )
            )
            self.brickColors[i].Update()

        try:
            
            self.mixer.music.load(self.filepath)
            if self.MidiMute:
                self.mixer.music.set_volume(0)
            else:
                self.mixer.music.set_volume(volume)
            print(f"Attempting to play: {filename}")
            if self.SideTrackEnabled:
                side_track_thread = threading.Thread(target=self.play_side_track, args=(self.SideTrack, volume, self.SideTrackDelay))
                side_track_thread.start()
                if self.SideTrackDelay <0: time.sleep(abs(self.SideTrackDelay))
                self.mixer.music.play()
            else:
                self.mixer.music.play()
        except pygame.error as e:
            print(f"Pygame error during playback: {e}")

    def extractLyrics(self, MessageType: str = "text") -> List[str]:
        lyrics: List[str] = []
        currentTrack = 0
        for track in self.midi.tracks:
            for msg in track:
                if msg.type == MessageType:
                    self.lyricsTrack = currentTrack 
                    lyrics.append(
                        str(msg.text)
                        .replace("@T ", "TITLE: ")
                        .replace("@L", "LANG: ")
                        .replace("\\", "")
                    )
            currentTrack+=1
        return lyrics

    def drawIndicatorBrick(self, screen, x, y, width, height, color):
        pygame.draw.rect(screen, color, (x, y, width, height))

    def get_valid_tracks(self, screen):
        """Filters the non-ignored tracks for rendering bricks"""
        return [i for i, finished in enumerate(self.isTrackFinished) if not finished and i not in self.ignore_tracks]

    def get_total_duration(self, ticks_per_beat:int) -> float:
        """Calculates the total duration of the MIDI file in seconds."""
        max_time = 0.0
        
        for track in self.midi.tracks:
            
            curr_time=0
            for msg in track:

                curr_time+=msg.time# update time
                if msg.type=="set_tempo":
                    self.tempo_microseconds_per_beat = msg.tempo
                seconds_per_beat = self.tempo_microseconds_per_beat / 1000000.0
                seconds_per_tick = seconds_per_beat / ticks_per_beat
                seconds= seconds_per_tick * curr_time
            max_time = max(max_time, seconds) # get if this happened
        return max_time
    
    def get_ignore_tracks(self):
        """Retrieves all the current tracks to be ignored by brick management"""
        self.ignore_tracks = {0}
        return self.ignore_tracks

    def Update(self, Screen):
        if self.IsPlaying:
            
            self.absolute_times = []  # Clear old absolute times

            for trackIndex, track in enumerate(self.midi.tracks):
                self.calculateAbsoluteTime(
                    self.midi.ticks_per_beat, track, trackIndex
                )  # Pass the trackIndex

            deltaTime = 0.0
            currentTime = time.time() - self.startTime
            activeTracks = self.get_valid_tracks(Screen)
            if len(activeTracks) == 0:
                self.IsPlaying=False


            #print(self.lyricsTrack)
            trackIndex = self.lyricsTrack
            msgIndex = self.messageIndices[trackIndex]
            if msgIndex < len(self.absolute_times[trackIndex]):  
                if (currentTime>= self.absolute_times[trackIndex][msgIndex]):
                    msg = self.midi.tracks[trackIndex][msgIndex]
                    if trackIndex == self.lyricsTrack:
                        if msg.type == "text":
                            #print(str(msg.text))
                            if str(msg.text).find("@L") > -1 or str(msg.text).find("@T") > -1 or str(msg.text).find("/") > -1:
                                self.CurrentLyric = (
                                    str(msg.text)
                                    .replace("@T ", "TITLE: ")
                                    .replace("@L", "LANG: ")
                                    .replace("\\", "")
                                    .replace("/", "")
                                )
                            elif  str(msg.text).find("\\") > -1:
                                self.CurrentLyric = ""
                            else: 
                                self.CurrentLyric += (
                                    str(msg.text)
                                    .replace("@T ", "TITLE: ")
                                    .replace("@L", "LANG: ")
                                    .replace("\\", "")
                                    .replace("/", "")
                                )
            
            
            
            
            for trackIndex in range(self.numTracks):
                if self.isTrackFinished[trackIndex] or trackIndex in self.ignore_tracks:
                    continue
                
                msgIndex = self.messageIndices[trackIndex]
                if msgIndex < len(self.absolute_times[trackIndex]):  
                    if (currentTime>= self.absolute_times[trackIndex][msgIndex]):
                        self.CurremtTimeInTrack = self.absolute_times[trackIndex][msgIndex]
                        
                        msg = self.midi.tracks[trackIndex][msgIndex]
                        
                        if msg.type == "end_of_track":
                            self.isTrackFinished[trackIndex] = True
                            continue
                        if msg.type == "note_on":
                            self.brickState[trackIndex] = True
                        if msg.type == "note_off":
                            self.brickState[trackIndex] = False
                        self.messageIndices[trackIndex] += 1  # Increment message index after processing


            
            updateRate = 1
            self.bricks = []  # Clear bricks each frame
            trackAmount = len(activeTracks) # Count remaining valid tracks that are updating the blocks and are on screen

            brickWidth = Screen.get_width() / trackAmount if trackAmount !=0 else 0
            for i, trackIndex in enumerate(activeTracks):  
                
                brickHeight = 20 
                x = i * brickWidth  
                y = Screen.get_height() - brickHeight
                
                
                Currentcolor = self.brickColors[trackIndex]  

                if self.brickState[trackIndex]:
                    Currentcolor.setTargetColor(
                        self.TextColor[trackIndex % len(self.TextColor)], True
                    )
                    Currentcolor.Update(updateRate=updateRate, deltaTime=deltaTime)
                else:
                    Currentcolor.setTargetColor(blendColors((0, 0, 0),self.TextColor[trackIndex % len(self.TextColor)],20/100), True)
                    Currentcolor.Update(updateRate=updateRate * 2, deltaTime=deltaTime)

                
                self.bricks.append(
                    (Currentcolor.getColor(), (x, y, brickWidth, brickHeight))
                )
                Currentcolor.Update()
    def getName(self):
        return self.Name
    
    def GetCurrentSongPos(self):
        elapsedTime = time.time() - self.startTime
        Seconds = int(elapsedTime  %  60)
        Minutes = int((elapsedTime // 60) % 60)
        return(f"{Minutes}:{"{:02d}".format(Seconds)}") 
    
    def GetSongDuration(self):
        Seconds = int(self.absolute_time_seconds % 60)
        Minutes = int((self.absolute_time_seconds // 60) % 60)
        return(f"{Minutes}:{"{:02d}".format(Seconds)}") 
    
    def getArtist(self):
        return self.Artist
    
    def getTtitle(self):
        return self.Title
    
    def getBricks(self):
        return self.bricks
    
    def getBrickState(self, index):
        return self.brickState[index]

    def getBrickColor(self, index):
        return self.brickColors[index]
    
    def getBrickRect(self, index):
        return self.bricks[index][1]
    
    def GetLyric(self):
        return(self.CurrentLyric)


