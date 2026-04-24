import QtQuick
import QtQuick.Controls

Window {
    id: root
    width: 1280
    height: 720
    title: "AlarmClock"
    visible: true
    color: "#000000"

    property real topRatio: 0.65   // Top area (square + wide)
    property real bottomRatio: 1-topRatio // Bottom area

    property var squareModel: widgetManager.get_by_slot("square")
    property var wideModel: widgetManager.get_by_slot("wide")
    property var bottomWidget: null

    Column {
        anchors.fill: parent

        Row {
            width: parent.width
            height: parent.height * topRatio

            // be there and be square
            Item {
                id: squareSlot
                width: parent.height
                height: parent.height
                clip: true

                Flickable {
                    id: squareFlick
                    anchors.fill: parent
                    contentHeight: squareSlot.height * Math.max(1, squareModel.length)
                    flickableDirection: Flickable.VerticalFlick
                    boundsBehavior: Flickable.StopAtBounds

                    Column {
                        width: parent.width
                        height: parent.height * Math.max(1, squareModel.length)

                        Repeater {
                            model: squareModel
                            delegate: Item {
                                width: squareSlot.width
                                height: squareSlot.height

                                Loader {
                                    anchors.fill: parent
                                    source: modelData.qml
                                    onLoaded: {
                                        if (item && item.hasOwnProperty("backend"))
                                            item.backend = modelData.backend
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // WIDE BOI
            Item {
                id: wideSlot
                width: parent.width - squareSlot.width
                height: parent.height
                clip: true

                Flickable {
                    id: wideFlick
                    anchors.fill: parent
                    contentWidth: wideSlot.width * Math.max(1, wideModel.length)
                    flickableDirection: Flickable.HorizontalFlick
                    boundsBehavior: Flickable.StopAtBounds

                    Row {
                        width: wideSlot.width * Math.max(1, wideModel.length)
                        height: parent.height

                        Repeater {
                            model: wideModel
                            delegate: Item {
                                width: wideSlot.width
                                height: wideSlot.height

                                Loader {
                                    anchors.fill: parent
                                    source: modelData.qml
                                    onLoaded: {
                                        if (item && item.hasOwnProperty("backend"))
                                            item.backend = modelData.backend
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // heh bottom
        Item {
            id: bottomSlot
            width: parent.width
            height: parent.height * bottomRatio
            clip: true
            visible: bottomWidget !== null

            Loader {
                id: bottomLoader
                anchors.fill: parent
                source: bottomWidget ? bottomWidget.qml : ""
                onLoaded: {
                    if (bottomWidget && item.hasOwnProperty("backend"))
                        item.backend = bottomWidget.backend
                }
            }
        }
    }

    function snapVertical() {
        let index = Math.round(squareFlick.contentY / squareSlot.height)
        squareFlick.contentY = index * squareSlot.height
    }

    function snapHorizontal() {
        let index = Math.round(wideFlick.contentX / wideSlot.width)
        wideFlick.contentX = index * wideSlot.width
    }

    Connections { target: squareFlick; function onMovementEnded() { snapVertical() } }
    Connections { target: wideFlick; function onMovementEnded() { snapHorizontal() } }
}