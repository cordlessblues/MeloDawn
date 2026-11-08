from pathlib import Path
import sys

parentDir = Path(__file__).resolve().parent.parent
if str(parentDir) not in sys.path:
    sys.path.insert(0, str(parentDir))

from datetime import datetime
from json import load
from MeloDawnWidget import BaseWidget
from PySide6.QtCore import Property, QObject, QTimer, Signal
import requests


class WeatherBackend(BaseWidget):
    WIDGET_INFO = {"name": "Weather", "slot": "wide"}

    dataChanged = Signal()

    def __init__(self, use12hour=True, parent=None):
        super().__init__(parent)
        self._data = {"current": {}, "hourly": [], "daily": []}
        self.use12Hour = use12hour

        self.apiKey = load(open(".ENV.json"))["WeatherAPI"]["Key"]
        self.location = load(open(".ENV.json"))["WeatherAPI"]["Location"]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateWeather)
        self.timer.start(30 * 60 * 1000)  # 30 min

        self.updateWeather()

    def updateWeather(self):  # MARK: Update Weather
        try:
            print("[WEATHER] Updating weather...")
            url = f"http://api.weatherapi.com/v1/forecast.json?key={self.apiKey}&q={self.location}&days=3&hours=8"
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
                "icon": "http:" + current.get("condition", {}).get("icon", ""),
            }

            hourlyData = (
                data.get("forecast", {}).get("forecastday", [{}])[0].get("hour", [])
            )
            hourly = []
            for h in hourlyData:
                dt = datetime.strptime(h["time"], "%Y-%m-%d %H:%M")
                if dt >= now:
                    if self.use12Hour:
                        timeSTR = dt.strftime("%I %p").lstrip("0")
                    else:
                        timeSTR = dt.strftime("%H:%M")

                    hourly.append(
                        {
                            "time": timeSTR,
                            "temp": h.get("temp_f", "--"),
                            "feels": h.get("feelslike_f", "--"),
                            "humidity": h.get("humidity", "--"),
                            "wind_mph": h.get("wind_mph", "--"),
                            "chance_of_rain": h.get("chance_of_rain", 0),
                            "uv": h.get("uv", "--"),
                            "condition": h.get("condition", {}).get("text", ""),
                            "icon": "http:" + h.get("condition", {}).get("icon", ""),
                        }
                    )
                if len(hourly) >= 8:
                    break
            self._data["hourly"] = hourly

            dailyData = data.get("forecast", {}).get("forecastday", [])
            daily = []
            for day in dailyData:
                d = day.get("day", {})
                daily.append(
                    {
                        "date": day.get("date", "--"),
                        "maxtemp": d.get("maxtemp_f", "--"),
                        "mintemp": d.get("mintemp_f", "--"),
                        "condition": d.get("condition", {}).get("text", ""),
                        "icon": "http:" + d.get("condition", {}).get("icon", ""),
                        "chance_of_rain": d.get("daily_chance_of_rain", 0),
                        "uv": d.get("uv", "--"),
                        "sunrise": day.get("astro", {}).get("sunrise", ""),
                        "sunset": day.get("astro", {}).get("sunset", ""),
                        "maxwind_mph": d.get("maxwind_mph", "--"),
                    }
                )
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


def init(context=None):
    return WeatherBackend(use12hour=True)


if __name__ == "__main__":
    WeatherBackend.standalone()
