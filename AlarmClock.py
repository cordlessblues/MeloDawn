from pygame.font import Font
import threading
import datetime
import pygame
import time
import textwrap

#Carls Imports
from pygameUtils import *
from CalendarManager import *
from ColorUtils import *
from AlarmManager import *
from MidiManager import *

pygame.init()


# Screen size
WIDTH = 1280
widthScale = WIDTH / 1920
print(f"widthScale: {widthScale}")
HEIGHT = 720
heightScale = HEIGHT / 1080
print(f"heightScale: {heightScale}")
ScaleOffset = min(widthScale, heightScale) 
print(f"ScaleOffset: {heightScale}")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AlarmClock")

pygame.mixer.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
ORANGE = (255, 165, 0)
GREEN = (25,255,100)
TEAL = (255/(8*1.5),255/1.5,255/1.5)

# Clock parameters
scale = 700  * ScaleOffset 
radius = 30  * ScaleOffset
offset = 100 * ScaleOffset
center_x, center_y = (WIDTH // 2), (HEIGHT // 2)
offset_x, offset_y = (WIDTH // 4.2), 0 
points_per_corner = 0
points_per_side = 15 - points_per_corner
lineWidth = round(10 * ScaleOffset)
lineRadius = 5 

StartPoints = []
EndPoints=[]
LineColors = []
for i in range(60):
    LineColors.append(ColorUtils.DynamicColor(-abs(i/60),-abs(i/60),(0,0,0),(0,0,0),(0,0,0)))
getTicksLastFrame=0
running = True
debug = False
NextIndex = 0
NextIndexColor = 1

# Text Settings
ClockColor = ColorUtils.DynamicColor(0.0,0.0,(0,0,0),(0,0,0),(0,0,0))
ClockColor.setTargetColor(WHITE)
TextPosX,TextPosY = center_x - offset_x ,center_y - offset_y 

# Alarm settings
alarms = FetchAlarms("python/AlarmClock/Alarms.json","python/AlarmClock/RingTones.json")
AlarmEvent = threading.Event()


def TriggerAlarm():
    global AlarmActive, AlarmQuieted
    AlarmQuieted=False
    AlarmActive=True

#Calendar Settings
Calevents = None
currentDate = datetime.now().date()
data_ready_event = threading.Event()
CalReset=False
calWidth=0



calData = None
def GetData():
    global calData
    calData = fetchCalData()
    data_ready_event.set()

def periodic_fetch():
    while True:
        GetData()    # Fetch the data
        time.sleep(10800)  # Wait for 3 hours

periodic_thread = threading.Thread(target=periodic_fetch, daemon=True)
periodic_thread.start()
#LowLightLevel Mode
LowLightActive = False
wasLowLightActive = False

#GenerateLines
StartPoints = get_points_on_edge(
    center_x - scale//2 - offset_x, 
    center_y - scale//2 - offset_y, 
    scale, 
    radius, 
    points_per_side, 
    points_per_corner
)
EndPoints   = get_points_on_edge(
    (center_x - scale//2)-(offset/2) - offset_x, 
    (center_y - scale//2)-(offset/2) - offset_y, 
    scale+offset, 
    radius, 
    points_per_side, 
    points_per_corner
)



FontPath = "python/AlarmClock/JetBrainsMonoNerdFont-Regular.ttf"
clockLargeFont     =  Font(FontPath, ( round((12 * 12) * ScaleOffset)  ))
clockSmallFont     =  Font(FontPath, ( round((12 * 3 ) * ScaleOffset)   ))
CalLargeFont       =  Font(FontPath, ( round((12 * 2 ) * ScaleOffset*2)   ))
CalSmallFont       =  Font(FontPath, ( round((12 * 1 ) * ScaleOffset*2)   ))
MessageFont        =  Font(FontPath, ( round((12 * 5 ) * ScaleOffset)   ))
iconFont           =  Font(FontPath, ( round((12 * 2 ) * ScaleOffset)   ))

vibratorColor = DynamicColor( 0.0, 0.0, ClockColor.getColor(), ClockColor.getColor())
speakerColor  = DynamicColor( 0.0, 0.0, ClockColor.getColor(), ClockColor.getColor())
lightColor    = DynamicColor( 0.0, 0.0, ClockColor.getColor(), ClockColor.getColor())

#MARK: mainLoop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    
    
    t = pygame.time.get_ticks()
    # deltaTime in seconds.
    deltaTime = (t - getTicksLastFrame) / 1000.0
    screen.fill((0, 0, 0, 0))  # Fill the screen with black
    
    left, middle, right = pygame.mouse.get_pressed()
    
    if left and wasLeft!=left:
        LowLightActive=not LowLightActive
    if right and wasRight!=right:
        for a in alarms:
            if a.IsActive():
                a.Snooze()
    
    current_time = datetime.now()
    
    if LowLightActive != wasLowLightActive:
        if LowLightActive:
            ClockColor.setTargetColor(blendColors(TEAL,WHITE,50/100),True)
        else:
            ClockColor.setTargetColor(WHITE,True)
    
    #CalendarDrawing stuff
    TextSubjectNames = []
    TextAssignmentNames = []
    TextDueDate = []
    
    TextRectSubjectNames = []
    TextRectAssignmentNames = []
    TextRectDueDate = []
    
    TextLaunchSubjectNames = []
    TextLaunchAssignmentNames = []
    TextLaunchDueDate = []
    
    TextRectLaunchSubjectNames = []
    TextRectLaunchAssignmentNames = []
    TextRectLaunchDueDate = []
    
    
    textSpacing = 10 * ScaleOffset * 2
    objectSpacing = 60 * ScaleOffset * 2
    NextItemoffset = 0
    if data_ready_event.is_set():
        for i in range(len(calData)):
            
            if LowLightActive != wasLowLightActive:
                CalReset=False
            
            #setOrginalTargetColor
            #MARK:Cal Reset
            if LowLightActive:
                if CalReset == False:
                    CalReset = True
                    for c in calData[i].getSubjectColors():
                        c.setTargetColor(blendColors(c.getOrginalTargetColor(),blendColors(TEAL,(0,0,0),80/100),50/100),True)
            else:
                if CalReset == False:
                    CalReset = True
                    for c in calData[i].getSubjectColors():
                        c.setTargetColor(c.getOrginalTargetColor(),True) 


            #MARK: CalText
            
            TextSubjectNames.append(    CalLargeFont.render( str( calData[i].subject ), True, calData[i].getSubjectColors()[0].getColor() ) )
            TextAssignmentNames.append( CalLargeFont.render( str( calData[i].name    ), True, calData[i].getSubjectColors()[1].getColor() ) )
            TextDueDate.append(         CalSmallFont.render( str( calData[i].dueDate ), True, calData[i].getSubjectColors()[2].getColor() ))
            
            TextRectSubjectNames.append(TextSubjectNames[i].get_rect())
            TextRectAssignmentNames.append(TextAssignmentNames[i].get_rect())
            TextRectDueDate.append(TextDueDate[i].get_rect())
            
            #MARK: CalPos
            
            
            calWidth = max(calWidth,TextRectSubjectNames[i].width,TextRectAssignmentNames[i].width,TextRectDueDate[i].width)
            if i-1 >= 0: TextRectSubjectNames[i].center = (WIDTH/2 + WIDTH/16 + TextRectSubjectNames[i].width/2 ,(TextRectDueDate[i-1].bottom + objectSpacing))
            else: TextRectSubjectNames[i].center = (WIDTH/2 + WIDTH/16 + TextRectSubjectNames[i].width/2 ,((150*ScaleOffset) + textSpacing))
            TextRectAssignmentNames[i].center = (WIDTH/2 + WIDTH/16 + TextRectAssignmentNames[i].width/2 , (TextRectSubjectNames[i].bottom+textSpacing))
            Background = pygame.draw.rect(screen, calData[i].getSubjectColors()[3].getColor(), (TextRectSubjectNames[i].left - 10, TextRectSubjectNames[i].top,  calWidth+25,  TextRectAssignmentNames[i].bottom - TextRectSubjectNames[i].top), border_radius=round(5* ScaleOffset*2))
            TextRectDueDate[i].topleft = (Background.right - TextRectDueDate[i].width-5,(Background.top))
            
            #MARK: CalBlit
            
            if calData[i].getSubjectColors()[1].getColor() != (0,0,0):
                screen.blit(TextSubjectNames[i],TextRectSubjectNames[i])
            if calData[i].getSubjectColors()[2].getColor() != (0,0,0):
                screen.blit(TextAssignmentNames[i],TextRectAssignmentNames[i])
            if calData[i].getSubjectColors()[3].getColor() != (0,0,0):
                screen.blit(TextDueDate[i],TextRectDueDate[i])
            

            Bar = pygame.draw.rect(
                screen,
                calData[i].getSubjectColors()[4].getColor(),
                (
                    Background.left,
                    Background.top, 
                    round(5*ScaleOffset*2),
                    Background.height  
                    ), 
                border_radius=round(10*ScaleOffset*2)
                )
            for c in calData[i].getSubjectColors():
                c.Update(1/((i+1)/5),deltaTime)

    text  = clockLargeFont.render( str(current_time.strftime("%I:%M")),   True, ClockColor.getColor())
    text2 = clockSmallFont.render( str(currentDate.strftime("%m-%d-%Y")), True, ClockColor.getColor())
    
    textRect = text.get_rect()
    textRect2 = text2.get_rect()
    
    textRect.center = (TextPosX, HEIGHT//2 - (textRect2.height)/2)
    textRect2.center = (TextPosX, textRect.bottom+textSpacing)
    
    screen.blit(text, textRect)
    screen.blit(text2, textRect2)
    
    #MARK: clock tick marks
    
    for i in range(len(StartPoints)):
        
        Seconds = datetime.now().second
        i = i + Seconds
        i = i % len(StartPoints)
        if LowLightActive:
            LineColors[i].setTargetColor((CalculateLineThickness(Seconds)[i]/8,CalculateLineThickness(Seconds)[i]/2,CalculateLineThickness(Seconds)[i]/2),True)
        else:
            LineColors[i].setTargetColor(interpolateColor(CalculateLineThickness(Seconds)[i],255,ORANGE,BLUE),True)
        
        if NextIndex-1 != Seconds:
            for b in range(len(LineColors)):
                LineColors[b].setBlendFactor(0.0)
        NextIndex = Seconds + 1
        
        if i == Seconds:
            if LowLightActive: 
                LineColors[i].setTargetColor(blendColors(TEAL,WHITE,50/100) ,True)
            else: 
                LineColors[i].setTargetColor(WHITE,True)
            LineColors[i].Update(1.5,deltaTime)
        elif i == Seconds-1:
            LineColors[i].Update(1.0,deltaTime)
        else:    
            LineColors[i].setBlendFactor(LineColors[i].getBlendFactor() + (1/2) * deltaTime)
        LineColors[i].Update( 1/((i+1)/5),deltaTime)
        draw_rounded_rect_line(screen, LineColors[i].getColor(),StartPoints[i],  EndPoints[i], lineRadius,lineWidth)
    
    
    
    for a in alarms:
        a.Update(screen,deltaTime)
        
        if a.IsActive():
            for color, rect in a.getAlarmTone().getTone().getBricks():
                pygame.draw.rect(screen, color, rect)
        
        
            message = a.getTitle()
            Artist = a.getArtist()
            Duration = a.getDuration()
            Lyrics = a.getLyrics()
            #print(Lyrics)
            MessageText = MessageFont.render(message,True,ClockColor.getColor())
            ArtistText = clockSmallFont.render(Artist,True,blendColors(ClockColor.getColor(),(0,0,0),30/100))
            DurationText = CalLargeFont.render(Duration,True,blendColors(ClockColor.getColor(),(0,0,0),60/100))
            LyricsText = MessageFont.render(Lyrics,True,ClockColor.getColor())
            
            MessageRect = MessageText.get_rect()
            ArtistRect = ArtistText.get_rect()
            DurationRect = DurationText.get_rect() 
            LyricsRect = LyricsText.get_rect() 
            
            MessageRect.left = 0
            ArtistRect.left = 0
            DurationRect.left = ArtistRect.right + (10*ScaleOffset)
            LyricsRect.left = WIDTH - LyricsRect.width
            
            MessageRect.top = HEIGHT - (MessageRect.height + DurationRect.height)
            ArtistRect.top = MessageRect.bottom - (ArtistRect.height-ArtistRect.height/2-(10 * ScaleOffset))
            DurationRect.top = ArtistRect.top + (ArtistRect.height/2) - (DurationRect.height/2)
            LyricsRect.top = HEIGHT - LyricsRect.height - (20 * ScaleOffset)
            
            screen.blit(MessageText  ,  MessageRect)
            screen.blit(ArtistText   ,  ArtistRect)
            screen.blit(DurationText ,  DurationRect)
            screen.blit(LyricsText   ,  LyricsRect)
    
    
    
    
    #MARK: ColorUpdates
    ClockColor.Update(    1/10, deltaTime)
    #vibratorColor.Update( 5,    deltaTime)
    #speakerColor.Update(  5,    deltaTime)
    #lightColor.Update(    5,    deltaTime)
    
    getTicksLastFrame = t
    wasLeft, wasMiddle, wasRight, = left, middle, right
    wasLowLightActive = LowLightActive
    
    pygame.time.Clock().tick(30)
    # Update displa
    pygame.display.flip() 
    
    # Handle events
    

# Quit pygame
pygame.quit()
