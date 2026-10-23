import QtQuick
import QtQuick.Window

Item {
    id: calendar

    property var backend: null

    anchors.fill: parent

    ListView {
        id: eventList

        anchors.fill: parent
        spacing: 8
        clip: true

        model: (calendar.backend && calendar.backend.model) ? calendar.backend.model : null
        reuseItems: true

        delegate: Item {
            width: ListView.view.width
            height: 70


            Text { //HACK: This is a hidden text item used to measure the width of a single character in the title font for the fade blocks.
                id: charMeasurer
                visible: false
                font.family: "Jetbrains Mono NF"
                font.pixelSize: title.font.pixelSize
                text: "M"
            }

            Rectangle {
                id: colorBar
                height: parent.height
                width: 8
                radius: 4
                anchors.left: parent.left
                color: Qt.darker(model.color, 1.4)
            }

            Item {
                id: titleContainer
                anchors.top: parent.top
                anchors.left: colorBar.right
                anchors.leftMargin: 8
                anchors.right: parent.right
                anchors.rightMargin: 8
                height: 35

                Text {
                    id: title
                    text: model.title
                    font.family: "Jetbrains Mono NF"
                    font.pixelSize: 28
                    color: Qt.lighter(model.color, 1.8)
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                }

                Row { // fades out the title text character by character
                    id: fadeBlocks
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    height: parent.height
                    z: 5
                    spacing: 0

                    Repeater {
                        model: 10

                        Rectangle {
                            width: charMeasurer.implicitWidth
                            height: parent.height

                            // Each block steps up in darkness/opacity across the 10 character slots
                            color: {
                                if (index === 0) return "transparent";
                                let t = index / 9.0;
                                return Qt.rgba(0, 0, 0, Math.min(1.0, Math.pow(t, 1.3) * 1.15));
                            }
                        }      //  HACK: text would still show past the fade blocks
                    }         //         but moving the fade blocks made them unaligned so
                }            //          i added this rectangle to cover the text that would
                Rectangle { //           show past the fade blocks.
                    width: charMeasurer.implicitWidth
                    height: parent.height
                    color: Qt.rgba(0, 0, 0, 255)
                    anchors.left: fadeBlocks.right
                    anchors.top: fadeBlocks.top

                }
            }

            Text {
                id: subject
                text: model.subject
                font.family: "Jetbrains Mono NF"
                font.pixelSize: 24
                color: Qt.lighter(model.color, 1.4)
                anchors.top: titleContainer.bottom
                anchors.left: titleContainer.left
            }

            Text {
                id: dueDate
                text: model.dueDate
                font.family: "Jetbrains Mono NF"
                font.pixelSize: 24
                color: "#ccc"
                anchors.right: parent.right
                anchors.rightMargin: 8
                anchors.top: subject.top
                y: 0
            }
        }
    }
}