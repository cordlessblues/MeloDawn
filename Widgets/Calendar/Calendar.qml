import QtQuick
import QtQuick.Window

Item {
    id: calendar

    property var backend: null
    property int animDuration: 2000

    anchors.fill: parent

    property var rainbowPalette: {
        var p = (typeof sysColorPallete !== "undefined" && sysColorPallete.colors) ? sysColorPallete.colors : {};
        return [p.red, p.peach, p.yellow, p.green, p.sky, p.blue, p.mauve, p.pink, p.teal];
    }

    function getSubjectColor(subjectStr) {
        if (!subjectStr)
            return sysColorPallete.colors.primaryAccent;
        var hash = 0;
        for (var i = 0; i < subjectStr.length; i++) {
            hash = subjectStr.charCodeAt(i) + ((hash << 5) - hash);
        }
        var index = Math.abs(hash) % rainbowPalette.length;
        return rainbowPalette[index];
    }

    ListView {
        id: eventList

        anchors.fill: parent
        anchors.topMargin: 8
        spacing: 8
        clip: true

        model: (calendar.backend && calendar.backend.model) ? calendar.backend.model : null
        reuseItems: true

        delegate: Item {
            width: ListView.view.width
            height: 70

            property color subjectBaseColor: calendar.getSubjectColor(model.subject)

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
                color: Qt.darker(subjectBaseColor, 1.2)
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
                    color: Qt.lighter(subjectBaseColor, 1.4)
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

                            color: {
                                if (index === 0)
                                    return "transparent";
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
                color: subjectBaseColor
                anchors.top: titleContainer.bottom
                anchors.left: titleContainer.left
            }

            Text {
                id: dueDate
                text: model.dueDate
                font.family: "Jetbrains Mono NF"
                font.pixelSize: 24
                color: sysColorPallete.colors.subtext0
                anchors.right: parent.right
                anchors.rightMargin: 8
                anchors.top: subject.top
                y: 0
            }
            Behavior on subjectBaseColor {
                ColorAnimation {
                    duration: calendar.animDuration
                    easing.type: Easing.InOutQuad
                }
            }
        }
    }
}
