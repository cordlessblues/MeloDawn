from pygame.font import Font
import pygame
from pygame import gfxdraw
#Carls Imports
from pygameUtils import *
from CalendarManager import *
from ColorUtils import *
from AlarmManager import *
from MidiManager import *
from TouchManager import *
from WidgetManager import *

pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
ORANGE = (255, 165, 0)
GREEN = (25,255,100)
TEAL = (255/(8*1.5),255/1.5,255/1.5)

class MidiWidget(Widget):
    def __init__(self,BaseRes):
        super().__init__(BaseRes)
        #midi specific vars
        self.renderSurface = pygame.surface.Surface((BaseRes,(BaseRes//8)),pygame.SRCALPHA)
        self.alarms = FetchAlarms("python/AlarmClock/Alarms.json","python/AlarmClock/RingTones.json")
        self.FontPath = "python/AlarmClock/JetBrainsMonoNerdFont-Regular.ttf"
        #fonts
        self.TitleFont        =  Font(self.FontPath, (12 * 3 ))
        self.ArtistFont       =  Font(self.FontPath, (12 * 3 ))
        self.DurationFont     =  Font(self.FontPath, (12 * 2 ))
        self.LyricsLargeFont  =  Font(self.FontPath, (12 * 3 ))
        self.LyricsSmallFont  =  Font(self.FontPath, (12 * 2 ))
        self.LowLightActive = False
        self.active = False
        self.wasActive = self.active
        self.MusicTextColor = DynamicColor(0.0,0.0,(255,255,255),(255,255,255),(0,0,0))
        self.MusicTextColor.setTargetColor((255,255,255),False)
        self.TitleDirty=True
        self.ArtistDirty=True
        self.DurationDir=True
        self.LyricsDirty=True
        self.TitleRect = pygame.Rect(0.0,0.0,0.0,0.0)
        self.ArtistRect = pygame.Rect(0.0,0.0,0.0,0.0)
        self.DurationRect = pygame.Rect(0.0,0.0,0.0,0.0)
        self.LyricsRect = pygame.Rect(0.0,0.0,0.0,0.0)
        self.Title = ""
        self.Artist = ""
        self.Duration = ""
        self.Lyrics = ""
    
    def update(self,deltaTime):
        self.dirtyRects=[]
        if self.isVisible:
            #self.renderSurface.fill((0,0,0,0))
            self.active=False
            for a in self.alarms:
                a.Update(self.renderSurface,deltaTime)
                if a.IsActive():
                    a.setScaleOffset(self.scaleFactor)
                    if self.LowLightActive:
                        self.MusicTextColor.setTargetColor(blendColors(TEAL,WHITE,50/100),True)
                    else:
                        self.MusicTextColor.setTargetColor(WHITE,True)
                    self.active = True
                    self.MusicTextColor.Update(0.5,deltaTime)
                    if self.Title != a.getTitle() or self.MusicTextColor.isDirty():
                        self.TitleDirty=True
                    else:
                        self.TitleDirty=False
                    self.Title = a.getTitle()
                    if self.Artist != a.getArtist() or self.MusicTextColor.isDirty():
                        self.ArtistDirty=True
                    else:
                        self.ArtistDirty=False
                    self.Artist = a.getArtist()
                    if self.Duration != a.getDuration() or self.MusicTextColor.isDirty():
                        self.DurationDirty=True
                    else:
                        self.DurationDirty=False
                    self.Duration = a.getDuration()
                    if self.Lyrics != a.getLyrics() or self.MusicTextColor.isDirty():
                        self.LyricsDirty=True
                    else:
                        self.LyricsDirty=False
                    self.Lyrics = a.getLyrics()
                    #print(self.Lyrics)
                    TitleText = self.TitleFont.render(self.Title,True,self.MusicTextColor.getColor())
                    ArtistText = self.ArtistFont.render(self.Artist,True,blendColors(self.MusicTextColor.getColor(),(0,0,0),(1/4)))
                    DurationText = self.DurationFont.render(self.Duration,True,blendColors(self.MusicTextColor.getColor(),(0,0,0),(2/4)))
                    if len(self.Lyrics)>=36:
                        LyricsText = self.LyricsSmallFont.render(self.Lyrics,True,(blendColors(self.MusicTextColor.getColor(),(0,0,0),(0/4))))
                    else:
                        LyricsText = self.LyricsLargeFont.render(self.Lyrics,True,(blendColors(self.MusicTextColor.getColor(),(0,0,0),(0/4))))

                    
                    
                    if self.TitleDirty:
                        self.renderSurface.fill((0, 0, 0, 255), rect=self.TitleRect)
                        self.dirtyRects.append(self.TitleRect)
                    if self.ArtistDirty:
                        self.renderSurface.blit(ArtistText   , self.ArtistRect)
                        self.renderSurface.fill((0, 0, 0, 255), rect=self.ArtistRect)
                        self.dirtyRects.append(self.ArtistRect)
                    if self.DurationDirty:
                        self.renderSurface.blit(DurationText , self.DurationRect)
                        self.renderSurface.fill((0, 0, 0, 255), rect=self.DurationRect)
                        self.dirtyRects.append(self.DurationRect)
                    if self.LyricsDirty:
                        self.renderSurface.blit(LyricsText   , self.LyricsRect)
                        self.renderSurface.fill((0, 0, 0, 255), rect=self.LyricsRect)
                        self.dirtyRects.append(self.LyricsRect)
                    
                    
                    self.TitleRect = TitleText.get_rect()
                    self.ArtistRect = ArtistText.get_rect()
                    self.DurationRect = DurationText.get_rect() 
                    self.LyricsRect = LyricsText.get_rect() 

                    self.TitleRect.left = 0
                    self.ArtistRect.left = 0
                    self.DurationRect.left = self.ArtistRect.right + (10*self.scaleFactor)
                    self.LyricsRect.left = self.baseRes - self.LyricsRect.width

                    self.TitleRect.top = self.baseRes//8 - 0 - self.TitleRect.height - max(self.ArtistRect.height,self.DurationRect.height) 
                    self.ArtistRect.top = self.TitleRect.bottom-10
                    self.DurationRect.top = self.ArtistRect.top + (self.ArtistRect.height/2) - (self.DurationRect.height/2)
                    self.LyricsRect.top = self.ArtistRect.bottom - self.LyricsRect.height 

                    if self.TitleDirty:
                        self.renderSurface.blit(TitleText    , self.TitleRect)
                        self.dirtyRects.append(self.TitleRect)
                    if self.ArtistDirty:
                        self.renderSurface.blit(ArtistText   , self.ArtistRect)
                        self.dirtyRects.append(self.ArtistRect)
                    if self.DurationDirty:
                        self.renderSurface.blit(DurationText , self.DurationRect)
                        self.dirtyRects.append(self.DurationRect)
                    if self.LyricsDirty:
                        self.renderSurface.blit(LyricsText   , self.LyricsRect)
                        self.dirtyRects.append(self.LyricsRect)

                    for color, rect in a.getAlarmTone().getTone().getBricks():
                        #print(rect)
                        if color.isDirty():
                            self.renderSurface.fill((0, 0, 0, 255), rect=rect)
                            gfxdraw.box(self.renderSurface,rect,color.getColor())
                            self.dirtyRects.append(rect)
if __name__ == "__main__":
    getTicksLastFrame=0
    midi = MidiWidget(1024)
    screen = pygame.display.set_mode(((1024), 1024//8))
    pygame.display.set_caption("ClockWidget")
    running = True
    while running:
        PygameEvents = pygame.event.get()
        for event in PygameEvents:
            if event.type == pygame.QUIT:
                running = False
            if event == pygame.KEYUP:
                clock.LowLightActive = not clock.LowLightActive
                print(f"toggled:{clock.LowLightActive}")
        
        t = pygame.time.get_ticks()
        # deltaTime in seconds.
        deltaTime = (t - getTicksLastFrame) / 1000.0
        screen.fill((255, 255, 255, 255))  # Fill the screen with black
        
        midi.update(deltaTime)
        midiRect =pygame.Rect(0.0,0.0,1024,1024//8)
        midi.render(screen,midiRect)
        pygame.draw.ellipse(screen,(255,255,0),pygame.Rect(midiRect.left,midiRect.top,10,10))
        
        getTicksLastFrame = pygame.time.get_ticks()
        pygame.time.Clock().tick(60)
        if midi.dirtyRects:
            pygame.display.update(midi.dirtyRects) 