import threading
import time
import pygame
from pygame.font import Font
from datetime import datetime
import weatherapi
from weatherapi.rest import ApiException
from pprint import pprint
import json
from WidgetManager import *
from pygameUtils import *

class WeatherWidget(Widget):
    def __init__(self, baseRes, locat):
        super().__init__(baseRes)
        pygame.init()
        self.renderSurface = pygame.surface.Surface((baseRes, baseRes), pygame.SRCALPHA)
        self.data = None  # Initial data is None
        self.oldData = None
        self.locat = locat
        self.FontPath = "python/AlarmClock/JetBrainsMonoNerdFont-Regular.ttf"
        self.IconFont = Font(self.FontPath, 6 * 60)
        self.LocationFont = Font(self.FontPath, 6 * 3)
        self.HumidityFont = Font(self.FontPath, 6 * 2)
        self.TempFont = Font(self.FontPath, 6 * 20)
        self.F = True
        self.IconDict = {
            1000: "",  # Sunny / Clear
            1003: "",  # Partly cloudy
            1006: "",  # Cloudy
            1009: "",  # Overcast
            1030: "",  # Mist
            1063: "",  # Patchy rain possible
            1066: "",  # Patchy snow possible
            1069: "",  # Patchy sleet possible
            1072: "",  # Patchy freezing drizzle possible
            1087: "",  # Thundery outbreaks possible
            1114: "",  # Blowing snow
            1117: "",  # Blizzard
            1135: "",  # Fog
            1147: "",  # Freezing fog
            1150: "",  # Patchy light drizzle
            1153: "",  # Light drizzle
            1168: "",  # Freezing drizzle
            1171: "",  # Heavy freezing drizzle
            1180: "",  # Patchy light rain
            1183: "",  # Light rain
            1186: "",  # Moderate rain at times
            1189: "",  # Moderate rain
            1192: "",  # Heavy rain at times
            1195: "",  # Heavy rain
            1198: "",  # Light freezing rain
            1201: "",  # Moderate or heavy freezing rain
            1204: "",  # Light sleet
            1207: "",  # Moderate or heavy sleet
            1210: "",  # Patchy light snow
            1213: "",  # Light snow
            1216: "",  # Patchy moderate snow
            1219: "",  # Moderate snow
            1222: "",  # Patchy heavy snow
            1225: "",  # Heavy snow
            1237: "",  # Ice pellets
            1240: "",  # Light rain shower
            1243: "",  # Moderate or heavy rain shower
            1246: "",  # Torrential rain shower
            1249: "",  # Light sleet showers
            1252: "",  # Moderate or heavy sleet showers
            1255: "",  # Light snow showers
            1258: "",  # Moderate or heavy snow showers
            1261: "",  # Light showers of ice pellets
            1264: "",  # Moderate or heavy showers of ice pellets
            1273: "",  # Patchy light rain with thunder
            1276: "",  # Moderate or heavy rain with thunder
            1279: "",  # Patchy light snow with thunder
            1282: ""   # Moderate or heavy snow with thunder
        }
        self.ColorDict = {
            "": (255, 204, 0, 255),     # Sunny / Clear - Bright Yellow
            "": (255, 204, 0, 255),     # Clear Night - Bright Yellow
            "": (255, 204, 0, 255),     # Partly Cloudy - Bright Yellow
            "": (128, 128, 128, 255),   # Cloudy - Gray
            "": (105, 105, 105, 255),   # Overcast - Dim Gray
            "": (169, 169, 169, 255),   # Mist / Fog - Dark Gray
            "": (30, 144, 255, 255),    # Rain - Dodger Blue
            "": (135, 206, 250, 255),   # Snow - Light Sky Blue
            "": (176, 224, 230, 255),   # Sleet / Ice - Powder Blue
            "": (176, 224, 230, 255),   # Drizzle - Powder Blue
            "": (255, 69, 0, 255),      # Thunderstorm - Orange Red
            "": (255, 250, 250, 255),   # Blowing Snow / Blizzard - Snow
            "": (255, 165, 0, 255),     # Windy - Orange
            "": (128, 0, 128, 255),     # Tornado - Purple
            "": (255, 69, 0, 255),      # Hot - Orange Red
            "": (0, 191, 255, 255),     # Cold - Deep Sky Blue
            "": (210, 180, 140, 255),   # Sandstorm / Smoke - Tan
            # Add more mappings as needed
        }
        self.updateFlag = 30  # Track how many frames need to be updated
        self.data_ready_event = threading.Event()  # Event to signal when data is ready
        self.dataLock = threading.Lock()  # Lock to safely update data
        self.calData = None
        self.periodic_thread = threading.Thread(target=self.periodic_fetch, daemon=True)
        self.periodic_thread.start()  # Start the data fetching thread

    def fetchWeatherData(self, location):
        # This method will fetch the weather data and set the event when done
        configuration = weatherapi.Configuration()
        configuration.api_key['key'] = json.load(open("/home/carl/.CodeProjects/python/AlarmClock/ENV.json"))["WeatherAPI"]["Key"]
        api_instance = weatherapi.APIsApi(weatherapi.ApiClient(configuration))

        while True:  # Keep fetching data periodically
            try:
                dT = str(datetime.now().date())  # date format
                data = api_instance.realtime_weather(location)
                with self.dataLock:
                    self.data = data  # Update the data safely using the lock
                    self.updateFlag = 30  # Mark next 5 frames as needing an update
                self.data_ready_event.set()  # Signal that the data is ready
                pprint(data)
                time.sleep(10 * 60)  # Sleep for 10 minutes before the next update
            except ApiException as e:
                print(f"Error fetching weather data: {e}")
                time.sleep(5 * 60)  # Sleep before retrying in case of an error

    def periodic_fetch(self):
        # Periodic fetching in the background thread
        self.fetchWeatherData(self.locat)  # Example location
    
    def NeedsUpdate(self) -> bool:
        # Check if the widget needs an update and if the update flag is active
        with self.dataLock:
            if self.data != self.oldData or self.updateFlag > 0:
                return True
        return False

    def update(self, delta_time: float):
        self.dirtyRects = []  # Clear dirty list at the start of update

        if self.isVisible:
            # Ensure the data is ready before updating
            if self.data_ready_event.is_set():
                # Draw icon
                with self.dataLock:
                    icon = self.IconFont.render(f"{self.IconDict[self.data['current']['condition']['code']]}", True,
                                                self.ColorDict[self.IconDict[self.data['current']['condition']['code']]])
                iconRect = icon.get_rect()
                iconRect.top = (iconRect.height // 13) * -1
                iconRect.left = self.rect.width // 2
                self.renderSurface.blit(icon, iconRect)
                self.dirtyRects.append(iconRect)

                # Draw temperature
                outlineThickness = 70
                tempSurf = render_outline_text(
                    f"{round(self.data['current']['temp_f' if self.F else 'temp_c'])}°{'F' if self.F else 'C'}",
                    self.TempFont, (255, 255, 255, 255), (0, 0, 0), outlineThickness)
                tempRect = tempSurf.get_rect()
                tempRect.top = iconRect.bottom - (iconRect.height // 2)
                tempRect.left = iconRect.right - (iconRect.width // 4) - tempRect.width // 2
                self.renderSurface.blit(tempSurf, tempRect)
                self.dirtyRects.append(tempRect)

                # Update oldData
                self.oldData = self.data

                # Decrease the update flag after one frame
                if self.updateFlag > 0:
                    self.updateFlag -= 1

if __name__ == "__main__":
    pygame.init()
    weather = WeatherWidget(1024, 63025)
    screen = pygame.display.set_mode((1024, 1024))
    pygame.display.set_caption("Weather Icon Display")
    c = pygame.time.Clock()
    running = True
    weatherRect = pygame.Rect(1024 / 4, 1024 / 4, 1024 / 2, 1024 / 2)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        print(c.get_fps())
        # Check if the weather widget needs an update
        if weather.NeedsUpdate():
            dr = weather.getDirtyRects(weatherRect)
            weather.update(c.get_time())  # Update weather data and the widget
            for r in dr:
                screen.fill((0,0,0),r)
            weather.render(screen, weatherRect)  # Render the widget on screen
            
            # Ensure dirty rects are rendered
            pygame.display.update(dr)
        
        c.tick(60.0)  # Limit to 60 FPS

    pygame.quit()
