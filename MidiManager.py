import mido
import time
import pygame
import json
from pygame import gfxdraw
from typing import List, Dict, Any
import math
from ColorUtils import *
import threading
from MidiPlayer import *


class Ringtone:
    def __init__(self,data):
        self.data = data
        self.Title = data["Name"]
        self.Artist = data["Artist"]
        self.filepath = data["FilePath"]
        self.MidiPlayer = None
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
            self.colorPallete["Red"],
            self.colorPallete["Peach"],
            self.colorPallete["Yellow"],
            self.colorPallete["Green"],
            self.colorPallete["Teal"],
            self.colorPallete["Sky"],
            self.colorPallete["Sapphire"],
            self.colorPallete["Blue"],
            self.colorPallete["Lavender"],
            self.colorPallete["Mauve"],
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
    
        

    
    def play_side_track(self,side_track, volume,delay):
        """Plays the side track on a separate channel."""
        if delay < 0.0: delay=0.0
        SideChannel = self.mixer.Channel(0)
        Track = self.mixer.Sound(side_track)
        SideChannel.set_volume(volume)
        time.sleep(delay)
        SideChannel.play(Track)
    
    def Stop(self):
        self.IsPlaying = False

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

    def play(self):
        self.startTime = time.time()
        self.MidiPlayer = MidiPlayer(self.filepath)
        self.MidiPlayer.play()
        self.IsPlaying=True
    
    
    def Update(self, Screen,deltaTime):
        #print("yes we are here")
        if self.IsPlaying:
            updateRate = 1/10
            self.bricks = []  # Clear bricks each frame
            brickAmount = len(self.MidiPlayer.getTrackState())
            #print(brickAmount)
            brickWidth = Screen.get_width() / brickAmount if brickAmount != 0 else 0

            if len(self.brickColors) == 0:
                for _ in range(brickAmount): # fix: itterate with blank assignment
                    # if color list is zero allocate the dynamic color instance
                    colorvalue=self.TextColor[_ % len(self.TextColor)] #assign all colors in an instance
                    self.brickColors.append(DynamicColor(colorvalue, blendColors(colorvalue,(0,0,0),25/100)))

            for i, trackActive in enumerate(self.MidiPlayer.getTrackState()):  
                #print(len(self.brickColors))
                brickHeight = 20 
                x = i * brickWidth  
                y = Screen.get_height() - brickHeight

                Currentcolor = self.brickColors[i] # access color using incrementer
                #print(self.brickColors[i].getColor())

                if trackActive: #change is using the active state instead of before
                    Currentcolor.setTargetColor(self.TextColor[i % len(self.TextColor)], True) 
                    Currentcolor.Update(updateRate=updateRate, deltaTime=deltaTime)
                else:
                    Currentcolor.setTargetColor(blendColors((0, 0, 0),self.TextColor[i % len(self.TextColor)],20/100), True)
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
        
        Seconds = int(self.MidiPlayer.getDuration() % 60)
        Minutes = int((self.MidiPlayer.getDuration() // 60) % 60)
        return(f"{Minutes}:{"{:02d}".format(Seconds)}") 
    
    def getArtist(self):
        return self.Artist
    
    def getTtitle(self):
        return self.Title
    
    def getBricks(self):
        return self.bricks
    
    def getBrickState(self, index):
        return self.MidiPlayer.getTrackState()[index]

    def getBrickColor(self, index):
        return self.brickColors[index]
    
    def getBrickRect(self, index):
        return self.bricks[index][1]
    
    def GetLyric(self):
        return self.MidiPlayer.getCurrentLyric()