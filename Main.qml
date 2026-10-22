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

    // Initialize as empty arrays to prevent undefined/length errors on startup
    property var squareModel: []
    property var wideModel: []
    property var bottomWidget: null

    Component.onCompleted: {
        // Safely fetch models once the context properties are fully bound
        squareModel = widgetManager.getBySlot("square")
        wideModel = widgetManager.getBySlot("wide")

        let bottomWidgets = widgetManager.getBySlot("bottom")
        if (bottomWidgets.length > 0) {
            bottomWidget = bottomWidgets[0]
        }
    }

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
            height: parent.height * root.bottomRatio
            clip: true
            visible: root.bottomWidget !== null

            Loader {
                id: bottomLoader
                anchors.fill: parent
                source: root.bottomWidget ? root.bottomWidget.qml : ""
                onLoaded: {
                    if (root.bottomWidget && item.hasOwnProperty("backend"))
                        item.backend = root.bottomWidget.backend
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