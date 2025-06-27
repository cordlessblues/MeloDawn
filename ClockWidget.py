from pygame.font import Font
import threading
import datetime
import pygame
import time
import textwrap
from pathlib import Path

#Carls Imports
from pygameUtils import *
from CalendarManager import *
from ColorUtils import *
from AlarmManager import *
from MidiManager import *
from TouchManager import *
from WidgetManager import *
pygame.init()

BASE_DIR = Path(__file__).resolve().parent


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
ORANGE = (255, 165, 0)
GREEN = (25,255,100)
TEAL = (255/(8*1.5),255/1.5,255/1.5)

class ClockWidget(Widget):
    def __init__(self,baseRes=1024):
        super().__init__(baseRes)
        # Clock parameters
        self.renderSurface = pygame.surface.Surface((baseRes,baseRes),pygame.SRCALPHA)
        self.scale = 915  * self.scaleFactor   
        self.radius = 30  * self.scaleFactor
        self.offset = 100 * self.scaleFactor 
        self.center_x, self.center_y = (baseRes // 2), (baseRes // 2)
        self.points_per_corner = 0
        self.points_per_side = 15-self.points_per_corner
        self.lineWidth = 10 * self.scaleFactor
        self.lineRadius = 5 * self.scaleFactor
        self.StartPoints = []
        self.EndPoints=[]
        self.LineColors = []
        for i in range(60):
            self.LineColors.append(ColorUtils.DynamicColor(-abs(i/60),-abs(i/60),(0,0,0),(0,0,0),(0,0,0)))
        self.getTicksLastFrame=0
        self.running = True
        self.debug = False
        self.NextIndex = 0
        self.NextIndexColor = 1
        
        # Text Settings
        self.ClockColor = ColorUtils.DynamicColor(0.0,0.0,(0,0,0),(0,0,0),(0,0,0))
        self.ClockColor.setTargetColor(WHITE)
        self.TextPosX,self.TextPosY = self.center_x ,self.center_y 
        
        self.LowLightActive=False
        
        self.StartPoints = get_points_on_edge(
            self.center_x - self.scale//2, 
            self.center_y - self.scale//2, 
            self.scale, 
            self.radius, 
            self.points_per_side, 
            self.points_per_corner
        )
        self.EndPoints   = get_points_on_edge(
            (self.center_x - self.scale//2)-(self.offset/2), 
            (self.center_y - self.scale//2)-(self.offset/2), 
            self.scale+self.offset, 
            self.radius, 
            self.points_per_side, 
            self.points_per_corner
        )
        
        self.FontPath = BASE_DIR / "JetBrainsMonoNerdFont-Regular.ttf"
        self.clockLargeFont = Font(self.FontPath, 12 * round(12 * self.scaleFactor))
        self.clockSmallFont = Font(self.FontPath, 12 * round(6  * self.scaleFactor) )
    
    def update(self,deltaTime):
        self.renderSurface.fill((0, 0, 0, 0))
        current_time = datetime.now()
        currentDate = current_time.date()
        if self.LowLightActive:
            self.ClockColor.setTargetColor(blendColors(TEAL,WHITE,50/100),True)
        else:
            self.ClockColor.setTargetColor(WHITE,True)
            
            
            
        self.ClockColor.Update(0.8,deltaTime)
        Time  = self.clockLargeFont.render( str(current_time.strftime("%I:%M")),   True, self.ClockColor.getColor())
        Date  = self.clockSmallFont.render( str(currentDate.strftime("%m-%d-%Y")), True, self.ClockColor.getColor())

        TimeRect = Time.get_rect()
        DateRect = Date.get_rect()

        TimeRect.center = (self.TextPosX, self.baseRes//2 - (DateRect.height)/2)
        DateRect.center = (self.TextPosX, TimeRect.bottom+60)
        self.renderSurface.blit(Time, TimeRect)
        self.renderSurface.blit(Date, DateRect)
        
        for i in range(len(self.StartPoints)):
            Seconds = (datetime.now().second + 7 )% len(self.StartPoints)
            i = i + Seconds + 7
            i = i % len(self.StartPoints)
            if self.LowLightActive:
                self.LineColors[i].setTargetColor((CalculateLineThickness(Seconds)[i]/8,CalculateLineThickness(Seconds)[i]/2,CalculateLineThickness(Seconds)[i]/2),True)
            else:
                self.LineColors[i].setTargetColor(interpolateColor(CalculateLineThickness(Seconds)[i],255,ORANGE,BLUE),False)

            if self.NextIndex-1 != Seconds:
                for b in range(len(self.LineColors)):
                    #self.LineColors[b].setBlendFactor(0.0)
                    pass
            self.NextIndex = Seconds + 1

            if i == Seconds:
                if self.LowLightActive: 
                    self.LineColors[i].setTargetColor(blendColors(TEAL,WHITE,50/100) ,True)
                else: 
                    self.LineColors[i].setTargetColor(WHITE,True)
                self.LineColors[i].Update(1.5,deltaTime)
            elif i == Seconds-1:
                self.LineColors[i].Update(1.0,deltaTime)
            else:    
                self.LineColors[i].setBlendFactor(self.LineColors[i].getBlendFactor() + (1/2) * deltaTime)
            self.LineColors[i].Update( 1/((i+1)/5),deltaTime)
            draw_rounded_rect_line(
                self.renderSurface,
                self.LineColors[i].getColor(),
                self.StartPoints[i],
                self.EndPoints[i],
                self.lineRadius,
                self.lineWidth,
                )


if __name__ == "__main__":
    getTicksLastFrame=0
    clock = ClockWidget(1024)
    screen = pygame.display.set_mode((1024, 1024))
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
        screen.fill((0, 0, 0, 255))  # Fill the screen with black
        
        clock.update(deltaTime)
        ClockRect =pygame.Rect(0.0,0.0,1024,1024)
        clock.render(screen,ClockRect)
        pygame.draw.ellipse(screen,(255,255,0),pygame.Rect(ClockRect.left,ClockRect.top,10,10))
        
        getTicksLastFrame = pygame.time.get_ticks()
        pygame.time.Clock().tick(15)
        pygame.display.flip() 