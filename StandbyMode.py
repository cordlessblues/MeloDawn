from icalevents.icalevents import events
from datetime import timedelta
from pygame.font import Font
import threading
import textwrap
import schedule
import datetime
import pygame
import copy
import time
import math
import json

pygame.init()

def get_points_on_edge(x, y, s, r, points_per_side, points_per_corner):
    Output = []

    # Top edge
    for i in range(points_per_side):
        x_top = x + r + (i / (points_per_side - 1)) * (s - 2 * r)
        y_top = y
        Output.append((int(x_top), int(y_top)))

    # Top-right corner 
    for i in range(1, points_per_corner - 1):
        angle = 1.5 * math.pi + (i / (points_per_corner - 1)) * (0.5 * math.pi)
        x_corner = x + s - r + r * math.cos(angle)
        y_corner = y + r + r * math.sin(angle)
        Output.append((int(x_corner), int(y_corner)))

    # Right edge
    for i in range(points_per_side):
        x_right = x + s
        y_right = y + r + (i / (points_per_side - 1)) * (s - 2 * r)
        Output.append((int(x_right), int(y_right)))

    # Bottom-right corner 
    for i in range(1, points_per_corner - 1):
        angle = 0 * math.pi + (i / (points_per_corner - 1)) * (0.5 * math.pi)
        x_corner = x + s - r + r * math.cos(angle)
        y_corner = y + s - r + r * math.sin(angle)
        Output.append((int(x_corner), int(y_corner)))

    # Bottom edge 
    for i in range(points_per_side):
        x_bottom = x + s - r - (i / (points_per_side - 1)) * (s - 2 * r)
        y_bottom = y + s
        Output.append((int(x_bottom), int(y_bottom)))

    # Bottom-left corner 
    for i in range(1, points_per_corner - 1):
        angle = 0.5 * math.pi + (i / (points_per_corner - 1)) * (0.5 * math.pi)
        x_corner = x + r + r * math.cos(angle)
        y_corner = y + s - r + r * math.sin(angle)
        Output.append((int(x_corner), int(y_corner)))

    # Left edge 
    for i in range(points_per_side):
        x_left = x
        y_left = y + s - r - (i / (points_per_side - 1)) * (s - 2 * r)
        Output.append((int(x_left), int(y_left)))

    # Top-left corner 
    for i in range(1, points_per_corner - 1):
        angle = math.pi + (i / (points_per_corner - 1)) * (0.5 * math.pi)
        x_corner = x + r + r * math.cos(angle)
        y_corner = y + r + r * math.sin(angle)
        Output.append((int(x_corner), int(y_corner)))

    # Remove duplicates

    return Output

def draw_rounded_rect_line(surface, color, start_pos, end_pos, radius, thickness):
    angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0]) + math.pi / 2
    
    length = math.hypot(end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
    
    rect_width = thickness
    rect_height = length
    rect = pygame.Rect(0, 0, rect_width, rect_height)
    
    rect_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
    rect_surface.fill((0, 0, 0, 0)) 
    pygame.draw.rect(rect_surface, color, (0, 0, rect_width, rect_height),border_radius=5)

    rotated_rect = pygame.transform.rotate(rect_surface, -math.degrees(angle))
    
    new_rect = rotated_rect.get_rect(center=((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2))

    surface.blit(rotated_rect, new_rect.topleft)

def CalculateLineThickness(current_second, max_value=255, num_lines=60):
    Values = []
    
    for i in range(num_lines):
        # Calculate the distance from the current second
        offset_index = (i - current_second) % num_lines  # Offset based on current second
        value = (offset_index / (num_lines - 1)) * max_value  # Scale from 0 to max_value
        Values.append(value)
    
    return Values

def interpolateColor(value, max_Value=255, Color1=(234,51,247), color2=(234,51,247)):

    # Calculate the interpolation factor
    factor = value / max_Value

    # Interpolate between blue and orange
    r = int(Color1[0] * (1 - factor) + color2[0] * factor)
    g = int(Color1[1] * (1 - factor) + color2[1] * factor)
    b = int(Color1[2] * (1 - factor) + color2[2] * factor)

    return (r, g, b)

def blendColors(color1, color2, blend_factor):
    """
    Blend two colors together based on the blend factor.
    
    Parameters:
    color1 (tuple): The first color as an (R, G, B) tuple.
    color2 (tuple): The second color as an (R, G, B) tuple.
    blend_factor (float): A value between 0 (color1) and 1 (color2) representing the blend factor.

    Returns:
    tuple: The blended color as an (R, G, B) tuple.
    """
    # Ensure blend_factor is between 0 and 1
    blend_factor = max(0, min(1, blend_factor))

    # Calculate the blended color
    blended_color = (
        int(color1[0] * (1 - blend_factor) + color2[0] * blend_factor),
        int(color1[1] * (1 - blend_factor) + color2[1] * blend_factor),
        int(color1[2] * (1 - blend_factor) + color2[2] * blend_factor)
    )

    return blended_color

class TextRectException:
    def __init__(self, message=None):
            self.message = message

    def __str__(self):
        return self.message

def multiLineSurface(string: str, font: pygame.font.Font, rect: pygame.rect.Rect, fontColour: tuple, BGColour: tuple, justification=0):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Parameters
    ----------
    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rect style giving the size of the surface requested.
    fontColour - a three-byte tuple of the rgb value of the
    text color. ex (0, 0, 0) = BLACK
    BGColour - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                1 horizontally centered
                2 right-justified

    Returns
    -------
    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    finalLines = []
    requestedLines = string.splitlines()
    # Create a series of lines that will fit on the provided
    # rectangle.
    for requestedLine in requestedLines:
        if font.size(requestedLine)[0] > rect.width:
            words = requestedLine.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException("The word " + word + " is too long to fit in the rect passed.")
            # Start a new line
            accumulatedLine = ""
            for word in words:
                testLine = accumulatedLine + word + " "
                # Build the line while the words fit.
                if font.size(testLine)[0] < rect.width:
                    accumulatedLine = testLine
                else:
                    finalLines.append(accumulatedLine)
                    accumulatedLine = word + " "
            finalLines.append(accumulatedLine)
        else:
            finalLines.append(requestedLine)

    # Let's try to write the text out on the surface.
    surface = pygame.Surface(rect.size)
    surface.fill(BGColour)
    accumulatedHeight = 0
    for line in finalLines:
        if accumulatedHeight + font.size(line)[1] >= rect.height:
            raise TextRectException("Once word-wrapped, the text string was too tall to fit in the rect.")
        if line != "":
            tempSurface = font.render(line, 1, fontColour)
        if justification == 0:
            surface.blit(tempSurface, (0, accumulatedHeight))
        elif justification == 1:
            surface.blit(tempSurface, ((rect.width - tempSurface.get_width()) / 2, accumulatedHeight))
        elif justification == 2:
            surface.blit(tempSurface, (rect.width - tempSurface.get_width(), accumulatedHeight))
        else:
            raise TextRectException("Invalid justification argument: " + str(justification))
        accumulatedHeight += font.size(line)[1]
    return surface

# Screen size
WIDTH = 1920
HEIGHT = 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Points on Rounded Square Edge")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
ORANGE = (255, 165, 0)
GREEN = (25,255,100)
TEAL = (255/(8*1.5),255/1.5,255/1.5)

# Clock parameters
scale = 700
radius = 30
offset = 100
center_x, center_y = WIDTH // 2, HEIGHT // 2 
offset_x, offset_y = WIDTH // 4.2, 0
points_per_corner = 0
points_per_side = 15 - points_per_corner
lineWidth = 10
lineRadius = 5

StartPoints = []
EndPoints=[]
colors = []
targetColors = []
orginalBlendFactors = []
blendFactors = []
init = []
for i in range(60):
    colors.append((0,0,0))
    targetColors.append((0,0,0))
    blendFactors.append(-abs((1/5*(0.5)*i)+(i+1)/50-1))
    init.append(False)

getTicksLastFrame=0
running = True
debug = False
NextIndex = 0
NextIndexColor = 1

# Text Settings
TextTargetColor = (255, )*3
TextColor = (0, )*3
TextBlendFactor = 0
TextPosX,TextPosY = center_x - offset_x ,center_y - offset_y    

# Alarm settings
AlarmQuieted = False
AlarmActive = False
AlarmEvent = threading.Event()
BlinkRate = 3 # Number of times to blink per second
BlinkDuration = 1 + (1/3)  # Duration of blinking in seconds
WaitDuration = 1.2 #Duration to wait after blinking
Blinks = BlinkRate * BlinkDuration  # Total number of blinks
BlinkInterval = 1 / BlinkRate  # Time interval for blinking
LastBlinkTime = time.time()
Visible = True
BlinkCount = 0
Waiting = False
WaitStartTime = 0

def TriggerAlarm():
    global AlarmActive, AlarmQuieted
    AlarmQuieted=False
    AlarmActive=True

#Calendar Settings
Calevents = None
currentDate = datetime.datetime.now().date()
SubjectNames = []
AssignmentNames = []
DueDate = []
CalBlendFactor = []
CalTargetColor = []
originalCalTargetColor = []
CalColor = []
calWidth = 0
data_ready_event = threading.Event()
CalReset = False
LaunchSubjectNames = []
LaunchAssignmentNames = []
LaunchDueDate = []

def fetchCalData():
    global Calevents, SubjectNames, AssignmentNames, DueDate, CalBlendFactor,CalTargetColor,CalColor,orginalBlendFactors,originalCalTargetColor
    # Simulating fetching the data (e.g., rsdmo = events(url="https://google.com", fix_apple=False))
    SubjectNames = []
    AssignmentNames = []
    DueDate = []
    CalBlendFactor = []
    CalTargetColor = []
    originalCalTargetColor = []
    CalColor = []
    
    Calevents = events(url = "https://rsdmo.instructure.com/feeds/calendars/user_dC1d8iBXUF7kxVgTvKzgSzb7urXmu3WqpMuzgvsU.ics", fix_apple= False)
    Calevents += events(url = "https://springfieldpublicschools.instructure.com/feeds/calendars/user_MoXtZLkDCWiutaK7nkoiD2LhnsxSCVPkFWHdPeBS.ics", fix_apple= False)
    # Parse the data
    for r in range(len(Calevents)):
        SubjectNames.append(Calevents[r].summary.split("[")[1].split("-")[0].strip().capitalize())
        AssignmentNames.append(textwrap.shorten(Calevents[r].summary.split("[")[0].strip().capitalize(),40,placeholder=" [...]"))
        DueDate.append(Calevents[r].end.date())
        SubjectColor = (60, 60, 60)
        CalBlendFactor.append([-abs((1/5)+r/50),-abs((1/5*0.5)+r/50),-abs((1/5*1)+r/50),-abs((1/5*1.5)+r/50),0+r/50])
        orginalBlendFactors.append([-abs((1/5)+r/50),-abs((1/5*0.5)+r/50),-abs((1/5*1)+r/50),-abs((1/5*1.5)+r/50),0+r/50])
        CalColor.append([(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)])
        match SubjectNames[r]:
            case "Graphic design 1":
                SubjectColor = (61, 133, 61)
            case "12 career comm & composition b":
                SubjectNames[r] = "Career & Communications"
                SubjectColor = (63, 77, 131)
            case "Digital electronics b":
                SubjectNames[r] = "Digital electronics"
                SubjectColor = (112, 63, 132)
            case "Ap comp sci a (sem 2)":
                SubjectNames[r] = "AP Computer Science"
                SubjectColor = (131, 90, 63)
        CalTargetColor.append([
                blendColors((255, 255, 255), SubjectColor, 70/100  ),
                blendColors((255, 255, 255), SubjectColor, 60/100  ),
                blendColors((255, 255, 255), SubjectColor, 50/100  ),
                blendColors((255, 255, 255), SubjectColor, 40/100  ),
                blendColors((0  , 0  ,0   ), SubjectColor, 75/100 )
        ]
        )
        originalCalTargetColor.append([
                blendColors((255, 255, 255), SubjectColor, 70/100  ),
                blendColors((255, 255, 255), SubjectColor, 60/100  ),
                blendColors((255, 255, 255), SubjectColor, 50/100  ),
                blendColors((255, 255, 255), SubjectColor, 40/100  ),
                blendColors((0  , 0  ,0   ), SubjectColor, 75/100  )
        ]
        )
    data_ready_event.set()

def periodic_fetch():
    while True:
        fetchCalData()    # Fetch the data
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



FontPath = "python/AlarmClock/JetBrainsMono.ttf"
clockMainFont     = Font(FontPath, ((12*12)))
clockSubFont      = Font(FontPath, ((12*3)))
CalMainFont       = Font(FontPath, ((12*2)))
CalSubFont        = Font(FontPath, ((12*1)))

current_time = datetime.datetime.now()
run_at = current_time + timedelta(seconds=10)
delay = (run_at - current_time).total_seconds()
#AlarmThread = threading.Timer(delay, TriggerAlarm()).start()


# Main game loop
while running:
    t = pygame.time.get_ticks()
    # deltaTime in seconds.
    deltaTime = (t - getTicksLastFrame) / 1000.0
    screen.fill((0, 0, 0, 0))  # Fill the screen with black
    
    left, middle, right = pygame.mouse.get_pressed()
    
    if left and wasLeft!=left:
        LowLightActive=not LowLightActive
    if right and wasRight!=right:
        debug = not debug
    if middle and wasMiddle!=middle:
        AlarmActive = not AlarmActive
    
    current_time = datetime.datetime.now()
    
    
    if current_time > datetime.datetime(current_time.year,current_time.month,current_time.day,22):
        LowLightActive=False
    if current_time > datetime.datetime(current_time.year,current_time.month,current_time.day,9):
        if current_time < datetime.datetime(current_time.year,current_time.month,current_time.day,7):
            LowLightActive= True
    if current_time < datetime.datetime(current_time.year,current_time.month,current_time.day,7,30,0):
        if current_time > datetime.datetime(current_time.year,current_time.month,current_time.day,7,0,0):
            if not AlarmQuieted: AlarmActive = True
    else: AlarmActive = False
    if AlarmActive:
        TextBlendFactor = 1
        if not Waiting:
            if BlinkCount < Blinks:
                if time.time() - LastBlinkTime >= BlinkInterval:
                    Visible = not Visible  # Toggle visibility
                    LastBlinkTime = time.time()
                    BlinkCount += 1
            else:
                # Start waiting after blinking
                Waiting = True
                WaitStartTime = time.time()
                Visible = True  # Ensure time is visible during wait

        else:
            # Handle waiting
            if time.time() - WaitStartTime >= WaitDuration:
                # Reset for the next blinking cycle
                Waiting = False
                BlinkCount = 0
                LastBlinkTime = time.time()  # Reset last blink time
    else:
        TextBlendFactor += (1/5) * deltaTime
    if Visible:
        if LowLightActive:
            TextTargetColor = TEAL
        else:
            TextTargetColor = WHITE
    else:
        TextTargetColor = BLACK
    
    
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
    
    
    textSpacing = 10
    objectSpacing = 60
    NextItemoffset = 0
    if data_ready_event.is_set():
        for i in range(len(SubjectNames)):
            
            if CalBlendFactor[i][0] <= 1: 
                CalColor[i][0] = blendColors(CalColor[i][0],CalTargetColor[i][0],CalBlendFactor[i][0])
                CalBlendFactor[i][0] = min(CalBlendFactor[i][0] + (1/5) * deltaTime,1)
            if CalBlendFactor[i][1] <= 1: 
                CalColor[i][1] = blendColors(CalColor[i][1],CalTargetColor[i][1],CalBlendFactor[i][1])
                CalBlendFactor[i][1] = min(CalBlendFactor[i][1] + (1/5) * deltaTime,1)
            if CalBlendFactor[i][2] <= 1: 
                CalColor[i][2] = blendColors(CalColor[i][2],CalTargetColor[i][2],CalBlendFactor[i][2])
                CalBlendFactor[i][2] = min(CalBlendFactor[i][2] + (1/5) * deltaTime,1)
            if CalBlendFactor[i][3] <= 1: 
                CalColor[i][3] = blendColors(CalColor[i][3],CalTargetColor[i][3],CalBlendFactor[i][3])
                CalBlendFactor[i][3] = min(CalBlendFactor[i][3] + (1/5) * deltaTime,1)
            if CalBlendFactor[i][4] <= 1: 
                CalColor[i][4] = blendColors(CalColor[i][4],CalTargetColor[i][4],CalBlendFactor[i][4])
                CalBlendFactor[i][4] = min(CalBlendFactor[i][4] + (1/5) * deltaTime,1)
            
            if LowLightActive != wasLowLightActive:
                CalReset=False
            
            
            
            if LowLightActive:
                if CalReset == False:
                    CalReset = True
                    CalBlendFactor = copy.deepcopy(orginalBlendFactors)
                    CalTargetColor[i][0] = blendColors(CalTargetColor[i][0],blendColors(TEAL,(0,0,0),80/100),50/100)
                    CalTargetColor[i][1] = blendColors(CalTargetColor[i][1],blendColors(TEAL,(0,0,0),80/100),50/100)
                    CalTargetColor[i][2] = blendColors(CalTargetColor[i][2],blendColors(TEAL,(0,0,0),80/100),50/100)
                    CalTargetColor[i][3] = blendColors(CalTargetColor[i][3],blendColors(TEAL,(0,0,0),80/100),50/100)
                    CalTargetColor[i][4] = blendColors(CalTargetColor[i][4],blendColors(TEAL,(0,0,0),80/100),50/100)
            else:
                if CalReset == False:
                    CalReset = True
                    CalBlendFactor = copy.deepcopy(orginalBlendFactors) 
                    CalTargetColor = copy.deepcopy(originalCalTargetColor)
            
            TextSubjectNames.append(CalMainFont.render(str(SubjectNames[i]),True,CalColor[i][1]))
            TextAssignmentNames.append(CalMainFont.render(str(AssignmentNames[i]),True,CalColor[i][2]))
            TextDueDate.append(CalSubFont.render(str(DueDate[i]),True,CalColor[i][3]))
            
            TextRectSubjectNames.append(TextSubjectNames[i].get_rect())
            TextRectAssignmentNames.append(TextAssignmentNames[i].get_rect())
            TextRectDueDate.append(TextDueDate[i].get_rect())
            
            calWidth = max(calWidth,TextRectSubjectNames[i].width,TextRectAssignmentNames[i].width,TextRectDueDate[i].width)
            if i-1 >= 0: TextRectSubjectNames[i].center = (WIDTH/2 + WIDTH/16 + TextRectSubjectNames[i].width/2 ,(TextRectDueDate[i-1].bottom + objectSpacing))
            else: TextRectSubjectNames[i].center = (WIDTH/2 + WIDTH/16 + TextRectSubjectNames[i].width/2 ,(150 + textSpacing))
            TextRectAssignmentNames[i].center = (WIDTH/2 + WIDTH/16 + TextRectAssignmentNames[i].width/2 , (TextRectSubjectNames[i].bottom+textSpacing))
            Background = pygame.draw.rect(screen, CalColor[i][4], (TextRectSubjectNames[i].left - 10, TextRectSubjectNames[i].top,  calWidth+25,  TextRectAssignmentNames[i].bottom - TextRectSubjectNames[i].top), border_radius=5)
            TextRectDueDate[i].topleft = (Background.right - TextRectDueDate[i].width-5,(Background.top))
            
            if CalColor[i][1] != (0,0,0):
                screen.blit(TextSubjectNames[i],TextRectSubjectNames[i])
            if CalColor[i][2] != (0,0,0):
                screen.blit(TextAssignmentNames[i],TextRectAssignmentNames[i])
            if CalColor[i][3] != (0,0,0):
                screen.blit(TextDueDate[i],TextRectDueDate[i])
            # pygame.draw.rect(Surface, color, Rect, width=0).topleft
            Bar = pygame.draw.rect(
                screen,
                CalColor[i][0],
                (
                    Background.left,
                    Background.top, 
                    5, 
                    Background.height  
                    ), 
                border_radius=10
                )

    TextColor = blendColors(TextColor,TextTargetColor,TextBlendFactor)
    text = clockMainFont.render(str(current_time.strftime("%I:%M")), True, TextColor)
    text2 = clockSubFont.render(str(currentDate.strftime("%m-%d-%Y")),True, TextColor)
    
    if debug: text = clockMainFont.render(str(deltaTime), True, TextColor)
    textRect = text.get_rect()
    textRect2 = text2.get_rect()
    
    textRect.center = (TextPosX, HEIGHT//2 - (textRect2.height)/2)
    textRect2.center = (TextPosX, textRect.bottom+textSpacing)
    
    screen.blit(text, textRect)
    screen.blit(text2, textRect2)
    
    for i in range(len(StartPoints)):
        
        Seconds = datetime.datetime.now().second
        i = i + Seconds
        i = i % len(StartPoints)  # Wrap around if i exceeds len(StartPoints)
        if LowLightActive:
            targetColors[i] = (CalculateLineThickness(Seconds)[i]/8,CalculateLineThickness(Seconds)[i]/2,CalculateLineThickness(Seconds)[i]/2)
        else:
            targetColors[i] = interpolateColor(CalculateLineThickness(Seconds)[i],255,ORANGE,BLUE)
        if init[i] == False:
            colors[i] = (0,)*3
            init[i] = True
        
        if NextIndex-1 != Seconds:
            for b in range(len(blendFactors)):
                blendFactors[b] = 0.0
            TextBlendFactor = 0.0
        NextIndex = Seconds + 1
        
        if i == Seconds:
            if LowLightActive: 
                TargetColor = (255/(8*1.5),255/1.5,255/1.5)
            else: 
                TargetColor = (255, )*3
            TextTargetColor = TargetColor
        else: TargetColor = targetColors[i]
        blendFactors[i] += (1/10) * deltaTime
        colors[i] = blendColors(colors[i],TargetColor,blendFactors[i])
        draw_rounded_rect_line(screen, colors[i],StartPoints[i],  EndPoints[i], lineRadius,lineWidth)
    getTicksLastFrame = t
    wasLeft, wasMiddle, wasRight, = left, middle, right
    wasLowLightActive = LowLightActive
    
    pygame.time.Clock().tick(60)
    # Update display
    pygame.display.flip() 
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Quit pygame
pygame.quit()
