import json
from datetime import datetime, timedelta
from random import *
import time
import os

from MidiManager import *

class Alarm():
    def __init__(self, triggerTime, AlarmEnabled: bool, RandSnooze: bool, Message: str, Tone: Ringtone):
        self.Message = Message
        self.triggerTime = triggerTime
        self.RandSnooze = RandSnooze
        self.Enabled = AlarmEnabled
        self.Snoozed = False
        self.Quieted = False
        self.Active = False
        self.beeper = None
        self.Tone = AlarmTone(Tone)
        
    def getAlarmTone(self):
        return self.Tone
    
    def setScaleOffset(self,s):
        self.Tone.getTone().setScaleOffset(s)
    
    def setAlarmTone(self, lightTiming = None , vibratorTiming = None, SpeakerTiming = None):
        if lightTiming != None:
            self.Tone.setLightTiming(lightTiming)
        if SpeakerTiming != None:
            self.Tone.setSpeakerTiming(SpeakerTiming)
        if vibratorTiming != None:
            self.Tone.setVibratorTiming(vibratorTiming)
    
    def getTriggerTime(self):
        return(self.triggerTime.time())
    
    def setTriggerTime(self,time):
        self.triggerTime = time
    
    def getMessage(self):
        if self.getMessage == None:
            return(str(self.getTriggerTime()))
        else:
            msg = self.Message.replace(
                "@Name",
                self.getAlarmTone().getTone().getName()
                ).replace(
                    "@Artist",
                    self.getAlarmTone().getTone().getArtist()
                    ).replace(
                        "@SongDuration",
                        f"{self.getAlarmTone().getTone().GetSongDuration()}/{self.getAlarmTone().getTone().GetCurrentSongPos()}"
                        )
            return(f"{msg}")

    def getDuration(self):
        return f"{self.getAlarmTone().getTone().GetSongDuration()}/{self.getAlarmTone().getTone().GetCurrentSongPos()}"
    
    def getArtist(self):
        return self.getAlarmTone().getTone().getArtist()
    
    def getTitle(self):
        return self.getAlarmTone().getTone().getTtitle()   
    
    def getLyrics(self):
        return self.getAlarmTone().getTone().GetLyric()
    
    def Quiet(self):
        self.Quieted=True
        self.Deactivate()

    def Deactivate(self):
        if self.Active:
            self.Active = False
            self.getAlarmTone().getTone().Stop()

    def IsActive(self):
        return self.Active

    def Snooze(self):
        if self.RandSnooze:
            random = randint(0,7)
            self.triggerTime = self.triggerTime.combine(datetime.now().date(),self.triggerTime.time()) + timedelta(minutes=random)
        else:
            self.triggerTime = self.triggerTime.combine(datetime.now().date(),self.triggerTime.time()) + timedelta(minutes=5)
            
    def Activate(self,Screen,deltaTime):
        if self.Active == False:
            print("activated")
            self.Active=True
        if self.Enabled and not self.Quieted:
                self.Active = True
                self.getAlarmTone().activate()
                #print("updating")
                self.getAlarmTone().Update(Screen,deltaTime)
        
    
    def Update(self,Screen,deltaTime):
        deltaZero = timedelta(weeks = 0 ,days = 0 ,hours = 0 ,minutes = 0 ,seconds = 0 ,milliseconds = 0 ,microseconds = 0)
        TriggerTime = self.triggerTime.combine(datetime.now().date(),self.triggerTime.time())
        if TriggerTime - datetime.now() + timedelta(minutes=5)  <= deltaZero:
            if not self.getAlarmTone().getTone().IsPlaying:
                self.Quiet()
            else:
                self.getAlarmTone().Update(Screen,deltaTime)
        elif TriggerTime - datetime.now() <= deltaZero:
            self.Activate(Screen,deltaTime)
        else:
            self.Deactivate()
        
    def getInfo(self,p=""):
        print(f"{p}Message              |  {self.Message}"            )
        print(f"{p}triggerTime          |  {self.triggerTime}"        )
        print(f"{p}RandSnooze           |  {self.RandSnooze}"         )
        print(f"{p}Enabled              |  {self.Enabled}"            )
        print(f"{p}Quieted              |  {self.Quieted}"            )
        print(f"{p}Active               |  {self.Active}"             )
        self.getAlarmTone().getInfo(f"    {p}")

class AlarmTone():
    def __init__(self, Tone: Ringtone):
        self.active = False
        self.tone = Tone

    def getTone(self):
        return self.tone
    
    def getInfo(self,p=""):
        os.system('cls' if os.name == 'nt' else 'clear'             )
        print(f"{p}Volume:              |  {self.vol}"                )
        print(f"{p}lightTrackIndex:     |  {self.lightTrackIndex}"    )
        print(f"{p}vibratorTrackIndex:  |  {self.vibratorTrackIndex}" )
        print(f"{p}RingTone:            |  {self.tone.getInfo(f"    {p}",True)}"               )
        
        

    def getVibratorState(self):
        return(self.getTone().getBrickState(self.getTone().getData()["VibratorTrack"]))

    def getVibratorRect(self):
        return(self.getTone().getBrickRect(self.getTone().getData()["VibratorTrack"]))
    
    def getVibratorColor(self):
        return(self.getTone().getBrickColor(self.getTone().getData()["VibratorTrack"]))

    def getVibratorIndex(self):
        return self.getTone().getData()["VibratorTrack"]
    
    def getSpeakerState(self):
        for i in range(len(self.tone.getBricks())):
            if self.getTone().getBrickState(i):
                return True
        return False

    def getLightState(self):
        return(self.getTone().getBrickState(self.getTone().getData()["LightTrack"]))

    def getLightIndex(self):
        return self.getTone().getData()["LightTrack"]
    
    def getLightColor(self):
        return(self.getTone().getBrickColor(self.getTone().getData()["LightTrack"]))
    
    def Update(self,Screen:pygame.surface,deltaTime):
        if self.active:
            if not self.getTone().IsPlaying:
                self.getTone().play()
            else:
                #print("Tone Updating")
                self.getTone().Update(Screen,deltaTime)

    def activate(self):
        self.active=True
        
    def deactivate(self):
        self.active = False

def FetchAlarms (FilePath,RingPath):
    """Fetches Alarms from given filepath

    Args:
        FilePath (Str): the path to alarms.json
    Returns:
        Arr Alarms:
            an array with 12 hour datetime codes for the alarms
    """    
    Alarms=[]
    with open(FilePath, 'r') as a:
        with open(RingPath, 'r') as r:
            AlarmData = json.load(a)
            RingData = json.load(r)
            for i in AlarmData:
                currentAlarm = AlarmData[str(i)]
                #print(currentAlarm)
                TimeCode = datetime.strptime(currentAlarm["triggerTime"], "%I:%M %p")
                if str(currentAlarm["AlarmTone"]) == "-1":
                    CurrentRingTone= RingData[str( randint( 0, ( len( RingData ) - 1 ) ) ) ]
                else: CurrentRingTone= RingData[str(currentAlarm["AlarmTone"])]
                Alarms.append(
                    Alarm(
                        TimeCode, 
                        currentAlarm["Enabled"], 
                        currentAlarm["RandSnooze"], 
                        currentAlarm["Message"],
                        #ringtone Stuff
                        Ringtone(CurrentRingTone)
                    )
                )
    return(Alarms)




if __name__ =="__main__":
    alarms = FetchAlarms("python/AlarmClock/Alarms.json")
    while True:
        alarms[0].Update()
        pygame.time.tick(30)