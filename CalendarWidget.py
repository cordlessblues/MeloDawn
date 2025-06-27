

from pygame.font import Font
import threading
import datetime
import pygame
import time

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


class CalenderWidget(Widget):
    def __init__(self,baseRes):
        super().__init__(baseRes)
        self.LowLightActive = False
        self.wasLowLightActive = False
        self.renderSurface = pygame.surface.Surface((baseRes,baseRes),pygame.SRCALPHA)
        #copyed and pasted from old main script
        FontPath = "python/AlarmClock/JetBrainsMonoNerdFont-Regular.ttf"
        self.CalLargeFont       =  Font(FontPath, ( round((12 * 2 ) * self.scaleFactor*2) ))
        self.CalSmallFont       =  Font(FontPath, ( round((12 * 1 ) * self.scaleFactor*2) ))
        
        Calevents = None
        self.currentDate = datetime.now().date()
        self.data_ready_event = threading.Event()
        self.CalReset=False
        self.calWidth=0
        self.calData = None
        self.periodic_thread = threading.Thread(target=self.periodic_fetch, daemon=True)
        self.periodic_thread.start()
        

    def GetData(self):
        global calData
        calData = fetchCalData()
        self.data_ready_event.set()

    def periodic_fetch(self):
        while True:
            self.GetData()    # Fetch the data
            time.sleep((1*60)*60)  # Wait 1 hour
    
    def update(self,deltaTime):
        if self.isVisible:
            
            self.renderSurface.fill((0,0,0,0))
            TextSubjectNames = []
            TextAssignmentNames = []
            TextDueDate = []

            TextRectSubjectNames = []
            TextRectAssignmentNames = []
            TextRectDueDate = []


            textSpacing = 10 * self.scaleFactor * 2
            objectSpacing = 60 * self.scaleFactor * 2
            if self.data_ready_event.is_set():
                for i in range(len(calData)):

                    if self.LowLightActive != self.wasLowLightActive:
                        self.CalReset=False
                    
                    #setOrginalTargetColor
                    #MARK:Cal Reset
                    if self.LowLightActive:
                        if self.CalReset == False:
                            self.CalReset = True
                            for c in calData[i].getSubjectColors():
                                c.setTargetColor(blendColors(c.getOrginalTargetColor(),(0,0,0),40/100),True)
                            calData[i].getSubjectColors()[3].setTargetColor(BLACK,True)
                            #calData[i].getSubjectColors()[2].setTargetColor(blendColors(BLACK,WHITE,50/100),True)
                    else:
                        if self.CalReset == False:
                            self.CalReset = True
                            for c in calData[i].getSubjectColors():
                                c.setTargetColor(c.getOrginalTargetColor(),True) 


                    #MARK: CalText

                    TextSubjectNames.append(    self.CalLargeFont.render( str( calData[i].subject ), True, calData[i].getSubjectColors()[0].getColor() ) )
                    TextAssignmentNames.append( self.CalLargeFont.render( str( calData[i].name    ), True, calData[i].getSubjectColors()[1].getColor() ) )
                    TextDueDate.append(         self.CalSmallFont.render( str( calData[i].dueDate ), True, calData[i].getSubjectColors()[2].getColor() ))

                    TextRectSubjectNames.append(TextSubjectNames[i].get_rect())
                    TextRectAssignmentNames.append(TextAssignmentNames[i].get_rect())
                    TextRectDueDate.append(TextDueDate[i].get_rect())

                    #MARK: CalPos


                    self.calWidth = max(self.calWidth,TextRectSubjectNames[i].width,TextRectAssignmentNames[i].width,TextRectDueDate[i].width)
                    if self.calWidth <(TextRectDueDate[i].width+TextRectSubjectNames[i].width):
                        self.calWidth = TextRectDueDate[i].width+TextRectSubjectNames[i].width
                    if i-1 >= 0: TextRectSubjectNames[i].center = (20+TextRectSubjectNames[i].width/2 ,(TextRectDueDate[i-1].bottom + objectSpacing))
                    else: TextRectSubjectNames[i].center = (20+TextRectSubjectNames[i].width/2 ,((15*self.scaleFactor) + textSpacing))
                    TextRectAssignmentNames[i].center = (20+TextRectAssignmentNames[i].width/2 , (TextRectSubjectNames[i].bottom+textSpacing))
                    Background = pygame.Rect(TextRectSubjectNames[i].left - 20, TextRectSubjectNames[i].top,  self.calWidth+25,  TextRectAssignmentNames[i].bottom - TextRectSubjectNames[i].top)
                    TextRectDueDate[i].topleft = (Background.right - TextRectDueDate[i].width-5,(Background.top))

                    #MARK: CalBlit

                    if calData[i].getSubjectColors()[0].getColor() != (0,0,0):
                        self.renderSurface.blit(TextSubjectNames[i],TextRectSubjectNames[i])
                    if calData[i].getSubjectColors()[1].getColor() != (0,0,0):
                        self.renderSurface.blit(TextAssignmentNames[i],TextRectAssignmentNames[i])
                    if calData[i].getSubjectColors()[2].getColor() != (0,0,0):
                        self.renderSurface.blit(TextDueDate[i],TextRectDueDate[i])

                    #draw Bar
                    gfxdraw.box(
                        self.renderSurface,
                        
                        (
                            Background.left,
                            Background.top, 
                            round(5*self.scaleFactor*2),
                            Background.height  
                            ),
                        calData[i].getSubjectColors()[4].getColor(), 
                        #border_radius=round(10*self.scaleFactor*2)
                        )
                    for c in calData[i].getSubjectColors():
                        c.Update(1/((i+1)/5),deltaTime)


if __name__ == "__main__":
    getTicksLastFrame=0
    cal = CalenderWidget(1024)
    screen = pygame.display.set_mode((1024, 1024))
    pygame.display.set_caption("ClockWidget")
    running = True
    while running:
        PygameEvents = pygame.event.get()
        for event in PygameEvents:
            if event.type == pygame.QUIT:
                running = False
            if event == pygame.KEYUP:
                print(f"toggled:{cal.LowLightActive}")
        
        t = pygame.time.get_ticks()
        # deltaTime in seconds.
        deltaTime = (t - getTicksLastFrame) / 1000.0
        screen.fill((0, 0, 0, 0))  # Fill the screen with black
        
        cal.update(deltaTime)
        calRect =pygame.Rect(0.0,0.0,512,512)
        cal.render(screen,calRect)
        pygame.draw.ellipse(screen,(255,255,0),pygame.Rect(calRect.left,calRect.top,10,10))
        
        getTicksLastFrame = pygame.time.get_ticks()
        pygame.time.Clock().tick(15)
        pygame.display.flip() 