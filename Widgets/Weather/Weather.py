from PySide6.QtCore import QObject, Signal, Property, QTimer
import requests
from datetime import datetime
from json import load

class Backend(QObject):
    dataChanged = Signal()

    def __init__(self, use_12_hour=True):
        super().__init__()
        self._data = {"current": {}, "hourly": [], "daily": []}
        self.use_12_hour = use_12_hour  # Boolean flag to toggle 12-hour time format

        self.api_key = load(open(".ENV.json"))["WeatherAPI"]["Key"]
        self.location = "Eureka, MO"

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateWeather)
        self.timer.start(30 * 60 * 1000)  # 30 min

        self.updateWeather()

    def updateWeather(self): # MARK: Update Weather
        try:
            print("[WEATHER] Updating weather...")
            url = f"http://api.weatherapi.com/v1/forecast.json?key={self.api_key}&q={self.location}&days=3&hours=8"
            data = requests.get(url).json()

            now = datetime.now()

            current = data.get("current", {})
            self._data["current"] = {
                "temp": current.get("temp_f", "--"),
                "feels": current.get("feelslike_f", "--"),
                "humidity": current.get("humidity", "--"),
                "wind_mph": current.get("wind_mph", "--"),
                "wind_dir": current.get("wind_dir", "--"),
                "pressure": current.get("pressure_in", "--"),
                "uv": current.get("uv", "--"),
                "cloud": current.get("cloud", "--"),
                "condition": current.get("condition", {}).get("text", ""),
                "icon": "http:" + current.get("condition", {}).get("icon", "")
            }

            hourly_data = data.get("forecast", {}).get("forecastday", [{}])[0].get("hour", [])
            hourly = []
            for h in hourly_data:
                dt = datetime.strptime(h["time"], "%Y-%m-%d %H:%M")
                if dt >= now:
                    # Format time based on the boolean flag
                    if self.use_12_hour:
                        time_str = dt.strftime("%I %p").lstrip("0")  # e.g., "3 PM"
                    else:
                        time_str = dt.strftime("%H:%M")             # e.g., "15:00"

                    hourly.append({
                        "time": time_str,
                        "temp": h.get("temp_f", "--"),
                        "feels": h.get("feelslike_f", "--"),
                        "humidity": h.get("humidity", "--"),
                        "wind_mph": h.get("wind_mph", "--"),
                        "chance_of_rain": h.get("chance_of_rain", 0),
                        "uv": h.get("uv", "--"),
                        "condition": h.get("condition", {}).get("text", ""),
                        "icon": "http:" + h.get("condition", {}).get("icon", "")
                    })
                if len(hourly) >= 8:
                    break
            self._data["hourly"] = hourly

            daily_data = data.get("forecast", {}).get("forecastday", [])
            daily = []
            for day in daily_data:
                d = day.get("day", {})
                daily.append({
                    "date": day.get("date", "--"),
                    "maxtemp": d.get("maxtemp_f", "--"),
                    "mintemp": d.get("mintemp_f", "--"),
                    "condition": d.get("condition", {}).get("text", ""),
                    "icon": "http:" + d.get("condition", {}).get("icon", ""),
                    "chance_of_rain": d.get("daily_chance_of_rain", 0),
                    "uv": d.get("uv", "--"),
                    "sunrise": day.get("astro", {}).get("sunrise", ""),
                    "sunset": day.get("astro", {}).get("sunset", ""),
                    "maxwind_mph": d.get("maxwind_mph", "--")
                })
            self._data["daily"] = daily

            self.dataChanged.emit()
            print("[WEATHER] Weather updated successfully.")

        except Exception as e:
            print(f"[WEATHER] Failed to update: {e}")

    def getCurrent(self):
        return self._data.get("current", {})

    def getHourly(self):
        return self._data.get("hourly", [])

    def getDaily(self):
        return self._data.get("daily", [])

    current = Property("QVariantMap", getCurrent, notify=dataChanged)
    hourly = Property("QVariantList", getHourly, notify=dataChanged)
    daily = Property("QVariantList", getDaily, notify=dataChanged)

# MARK: Metadata & Init
WIDGET_INFO = {"name": "Weather", "slot": "wide"}
def init(context=None): return Backend(use_12_hour=True)

if __name__ == "__main__": # MARK: Unit Test
    import sys
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQuick import QQuickView
    from PySide6.QtCore import QUrl, Qt

    app = QGuiApplication(sys.argv)

    backend = Backend(use_12_hour=True)

    view = QQuickView()
    view.rootContext().setContextProperty("backend", backend)
    view.setSource(QUrl.fromLocalFile("Widgets/Weather/Weather.qml"))
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setFlags(Qt.FramelessWindowHint)
    view.setColor("transparent")
    view.setWidth(400)
    view.setHeight(300)
    view.show()

    sys.exit(app.exec())