import QtQuick
import QtQuick.Controls

Item {
    id: root
    width: 812
    height: 468
    property var backend: null

    Text {
        text: "Status: " + (root.backend ? root.backend.connectionStatus : "Disconnected")
        color: "#FF9800"
        font.family: "Jetbrains Mono NF"
        font.pixelSize: 20
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.rightMargin: 8
        visible: root.backend && root.backend.connectionStatus === "Connected" ? false : true
    }

    ListView {
        anchors.fill: parent
        anchors.topMargin: 10
        clip: true
        spacing: 10

        model: root.backend ? root.backend.entities : []

        delegate: Item {
            width: parent.width
            height: 70

            Rectangle {
                id: bar
                height: parent.height
                width: 8
                radius: bar.width
                anchors.left: parent.left
                anchors.leftMargin: bar.width
                color: sysColorPallete.colors.primaryAccent
            }

            Text {
                id: nameText
                text: modelData.name
                color: sysColorPallete.colors.primaryAccent
                font.pixelSize: 30
                anchors.top: bar.top
                anchors.left: bar.right
                anchors.leftMargin: 10
                font.family: "Jetbrains Mono NF"
            }

            Text {
                text: modelData.stateText
                color: Qt.darker(sysColorPallete.colors.primaryAccent)
                font.pixelSize: 20
                font.bold: true
                anchors.left: nameText.left
                anchors.top: nameText.bottom
                font.family: "Jetbrains Mono NF"
            }
        }
    }
}
