from pathlib import Path
import sys

parentDir = Path(__file__).resolve().parent.parent
if str(parentDir) not in sys.path:
    sys.path.insert(0, str(parentDir))

import asyncio
from MeloDawnWidget import BaseWidget
import json
from PySide6.QtCore import Property, QThread, Signal, Slot
import requests
import websockets


class HomeAssistantSocketWorker(QThread):
    stateChanged = Signal(str, str, dict)
    connectionStatusChanged = Signal(str)

    def __init__(self, host, token):
        super().__init__()
        self.host = host
        self.token = token
        self._running = True

    def run(self):
        asyncio.run(self.WebsocketLoop())

    async def WebsocketLoop(self):
        uri = f"ws://{self.host}/api/websocket"

        while self._running:
            try:
                self.connectionStatusChanged.emit("Connecting...")
                async with websockets.connect(uri) as socket:
                    authRequest = await socket.recv()
                    if json.loads(authRequest).get("type") != "auth_required":
                        break

                    await socket.send(
                        json.dumps({"type": "auth", "access_token": self.token})
                    )

                    authResponse = await socket.recv()
                    if json.loads(authResponse).get("type") != "auth_ok":
                        self.connectionStatusChanged.emit("Auth failed")
                        return

                    self.connectionStatusChanged.emit("Connected")

                    await socket.send(
                        json.dumps(
                            {
                                "id": 1,
                                "type": "subscribe_events",
                                "event_type": "state_changed",
                            }
                        )
                    )

                    async for message in socket:
                        if not self._running:
                            break

                        data = json.loads(message)
                        if data.get("type") == "event":
                            event = data.get("event", {})
                            if event.get("event_type") == "state_changed":
                                eventData = event.get("data", {})
                                entityID = eventData.get("entity_id")
                                newStateObj = eventData.get("new_state")

                                if newStateObj:
                                    stateVal = str(newStateObj.get("state"))
                                    attributes = newStateObj.get("attributes", {})
                                    self.stateChanged.emit(
                                        entityID, stateVal, attributes
                                    )

            except websockets.ConnectionClosed:
                for i in range(5):
                    self.connectionStatusChanged.emit(
                        f"Connection closed. Reconnecting in {5-i}s"
                    )
                    await asyncio.sleep(1)
            except Exception as e:
                self.connectionStatusChanged.emit(
                    "Connection Error. Reconnecting in 5s"
                )
                self.connectionStatusChanged.emit(f"Error: {str(e)}")
                await asyncio.sleep(5)

    def stop(self):
        self._running = False
        self.quit()
        if not self.wait(300):
            print("[Hass] Worker thread did not exit in time, forcing shutdown.")


class HomeAssistantBackend(BaseWidget):
    WIDGET_INFO = {"name": "HomeAssistant", "slot": "wide"}

    dataUpdated = Signal()

    def __init__(self, context=None):
        super().__init__()
        self._status = "initializing..."

        rawIDs = json.load(open("conf.json"))["HomeAssistant"]["trackedEntities"]
        self._trackedEntities = []

        for entityID in rawIDs:
            self._trackedEntities.append(
                {
                    "id": entityID,
                    "name": entityID.split(".")[1].replace("_", " ").title(),
                    "state": "Loading...",
                    "stateText": "Loading...",
                }
            )

        envData = json.load(open(".ENV.json"))["HomeAssistant"]
        self.host = envData["IPAddress"]
        self.token = envData["AccessToken"]

        self.fetchInitialStates()

        self.worker = HomeAssistantSocketWorker(self.host, self.token)
        self.worker.stateChanged.connect(self.onEntityStateChanged)
        self.worker.connectionStatusChanged.connect(self.onStatusChanged)
        self.worker.start()

    @Property(list, notify=dataUpdated)
    def entities(self):
        return self._trackedEntities

    @Property(str, notify=dataUpdated)
    def connectionStatus(self):
        return self._status

    def fetchInitialStates(self):
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            response = requests.get(
                f"http://{self.host}/api/states", headers=headers, timeout=5
            )
            if response.status_code == 200:
                for item in response.json():
                    eID = item.get("entity_id")
                    for entity in self._trackedEntities:
                        if entity["id"] == eID:
                            self.updateEntityData(
                                entity,
                                str(item.get("state")),
                                item.get("attributes", {}),
                            )
                self.dataUpdated.emit()
        except Exception as e:
            print(f"[ERROR][HomeAssistant] Failed to fetch initial REST states: {e}")

    def updateEntityData(self, entityDict, state, attributes):
        entityDict["state"] = state

        if "friendly_name" in attributes:
            entityDict["name"] = attributes["friendly_name"]

        unit = attributes.get("unit_of_measurement", "")
        if unit:
            entityDict["stateText"] = f"{state} {unit}"
        else:
            entityDict["stateText"] = state.capitalize()

    @Slot(str, str, dict)
    def onEntityStateChanged(self, entityID, newState, attributes):
        for entity in self._trackedEntities:
            if entity["id"] == entityID:
                self.updateEntityData(entity, newState, attributes)
                self.dataUpdated.emit()
                break

    @Slot(str)
    def onStatusChanged(self, status):
        self._status = status
        self.dataUpdated.emit()

    def cleanup(self):
        self.worker.stop()


def init(context=None):
    return HomeAssistantBackend()


if __name__ == "__main__":
    HomeAssistantBackend.standalone()
