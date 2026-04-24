import QtQuick
import QtQuick.Window

Item {
    id: calendar

    property var backend

    anchors.fill: parent

    ListView {
        id: eventList

        anchors.fill: parent
        spacing: 8
        clip: true
        model: null // calendar backend is slow.
        reuseItems: true

        delegate: Item {
            width: ListView.view.width
            height: 70

            Rectangle {
                id: colorBar

                height: parent.height
                width: 8
                radius: 4
                x: 0
                y: 0
                color: model.overdue ? "#ff0000" : Qt.darker(model.color, 1.4)
            }

            Text {
                id: title

                text: model.title
                font.family: "Jetbrains Mono NF"
                font.pixelSize: 28
                color: Qt.lighter(model.color, 1.8)
                x: colorBar.width + 8
                y: 0
            }

            Text {
                id: subject

                text: model.subject
                font.family: "Jetbrains Mono NF"
                font.pixelSize: 24
                color: Qt.lighter(model.color, 1.4)
                x: title.x
                y: title.y + title.height
            }

            Text {
                id: dueDate

                text: model.dueDate
                font.family: "Jetbrains Mono NF"
                font.pixelSize: 24
                color: "#ccc"
                anchors.right: parent.right
                anchors.rightMargin: 8
                y: 0
            }

        }
        Connections {
            target: calendar

            function onBackendChanged() {
                if (calendar.backend && calendar.backend.model) {
                    eventList.model = calendar.backend.model
                } else {
                    console.warn("[Calendar] backend missing model")
                }
            }
        }
        Connections {
            target: backend ? backend.model : null

            function onModelReset() {
                eventList.model = backend.model
            }
        }

    }

}
