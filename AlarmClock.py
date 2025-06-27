from pygame.font import Font
import pygame
import moderngl
import sys
from pygameUtils import *
from CalendarManager import *
from ColorUtils import *
from AlarmManager import *
from MidiManager import *
from TouchManager import *
from bloomShader import *
from ClockWidget import *
from CalendarWidget import *
from MidiWidget import *
from WeatherWidget import *

pygame.init()

# Screen size
WIDTH = 800
HEIGHT = 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AlarmClock")

pygame.mixer.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
ORANGE = (255, 165, 0)
GREEN = (25, 255, 100)
TEAL = (255 / (8 * 1.5), 255 / 1.5, 255 / 1.5)

# LowLightLevel Mode
LowLightActive = False
wasLowLightActive = False

touch = TouchInput(screen)

FontPath = "python/AlarmClock/JetBrainsMonoNerdFont-Regular.ttf"

widget_heights = {
    'clock': 512 - 128,
    'calendar': 512 - 128,
    'weather': 512 - 128,
    'mid': 128 / 1.28,
}


clock = ClockWidget(1024 - 256)
clock.rect = pygame.Rect(0.0, 0.0, 512 - 128, 512 - 128)
cal = CalenderWidget(1024 - 256)
cal.rect = pygame.Rect(WIDTH / 2, 0.0, 512 - 128, 512 - 128)
mid = MidiWidget(1024 - 256)
mid.rect = pygame.Rect(0.0, HEIGHT - widget_heights['mid'], 1024 / 1.28, widget_heights['mid'])
weather = WeatherWidget(1024-256, 63025)
weather.rect = pygame.Rect(WIDTH / 2, 0.0, 512 - 128, 512 - 128)
LeftTop = InterpolatedValue(0, 0, 1)
RightTop = InterpolatedValue(0, 0, 1)

Widgets = []

WidgetsLeft = []
WidgetsRight  = []

WidgetsLeft.append(clock)

WidgetsRight.append(weather)
WidgetsRight.append(cal)


Widgets.append(WidgetsLeft)
Widgets.append(WidgetsRight)

WidgetScale = 512 - 128

rightIndex = 0
leftIndex = 0

LeftTop.set_target(0 if mid.active else (HEIGHT // 2) - ((512 - 128) // 2))
RightTop.set_target(0 if mid.active else (HEIGHT // 2) - ((512 - 128) // 2))
LeftTop.currentValue = LeftTop.targetValue
RightTop.currentValue = LeftTop.targetValue

bloom = True
bloomRadius = 2
getTicksLastFrame = 0
running = True
GameClock = pygame.time.Clock()

scroll_position = 0
scroll_speed = 10 


# Main Loop
while running:
    PygameEvents = pygame.event.get()
    for event in PygameEvents:
        if event.type == pygame.QUIT:
            running = False
    
    t = GameClock.get_time()
    widthScale = screen.get_rect().width / 1920
    heightScale = screen.get_rect().height / 1080
    ScaleOffset = min(widthScale, heightScale)

    touch.update(PygameEvents)
    # deltaTime in seconds.
    deltaTime = GameClock.get_time() / 1000
    screen.fill((0, 0, 0), screen.get_rect())
    for w in range(len(Widgets)):
        for i in range(len(Widgets[w])):
            currentWidget = Widgets[w][i]
            pos = RightTop.currentValue if w == 0 else RightTop.currentValue
            currentWidget.rect.top = pos if i == 0 else (pos + Widgets[w][0].rect.height)
            currentWidget.LowLightActive = LowLightActive
            currentWidget.update(deltaTime)
            if currentWidget.NeedsUpdate():
                currentWidget.render(screen, currentWidget.rect)
            pygame.display.update(currentWidget.rect)
    
    mid.update(deltaTime)
    print(weather.rect)
    LeftTop.update(deltaTime)
    RightTop.update(deltaTime)

    mid.rect = pygame.Rect(0.0, HEIGHT - widget_heights['mid'], 1024 / 1.28, widget_heights['mid'])

    mid.rect.top = clock.rect.bottom

    
    if mid.active != mid.wasActive and mid.active:
        LeftTop.set_target(0 if mid.active else HEIGHT // 2 - clock.rect.height // 2)
        RightTop.set_target(0 if mid.active else HEIGHT // 2 - clock.rect.height // 2)
    
    if mid.active: 
        mid.render(screen,mid.rect)
        pygame.display.update(mid.rect)

    getTicksLastFrame = t
    wasLowLightActive = LowLightActive
    cal.wasLowLightActive = wasLowLightActive

    # Update display
    GameClock.tick(24)

# Quit pygame
pygame.quit()