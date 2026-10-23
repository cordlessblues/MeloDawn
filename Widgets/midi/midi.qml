import QtQuick
import QtQuick.Controls

Item {
    id: midi
    width: 400
    height: 200

    property var backend: null
    property var backendSafe: backend || {}

    // MARK: MIDI Visualizer Row
    Row {
        width: parent.width
        anchors.bottom: parent.bottom
        height: 50
        spacing: 0

        Repeater {
            model: (midi.backend && midi.backend.model) ? midi.backend.model : null

            Rectangle {
                property var baseColor: Qt.rgba(
                    model.color[0] / 255,
                    model.color[1] / 255,
                    model.color[2] / 255,
                    1
                )

                width: midi.width / (model.trackCount || 1)
                height: 20
                anchors.bottom: parent.bottom

                color: Qt.lighter(
                    model.active ? baseColor : Qt.darker(baseColor, 1.5),
                    1 + (model.velocity || 0) * 1.5
                )

                Behavior on color {
                    ColorAnimation {
                        duration: 175
                        easing.type: Easing.OutCubic
                    }
                }

                transform: Scale {
                    //xScale: 1
                    yScale: model.scaleY || 1

                    //origin.x: width / 2
                    origin.y: height

                    Behavior on yScale {
                        NumberAnimation {
                            duration: 175
                            easing.type: Easing.OutCubic
                        }
                    }
                }
            }
        }
    }
    MouseArea {
        anchors.fill: parent
        onClicked: {
            if (backendSafe) {
                backendSafe.load_random_midi();
            }
        }
    }
    // MARK: Lyrics Container
    Item {
        id: lyricsContainer
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        height: 50
        clip: true

        /*
        Row {
            id: lyricRow
            spacing: 6
            anchors.verticalCenter: parent.verticalCenter

            Behavior on x {
                NumberAnimation { duration: 250; easing.type: Easing.OutCubic }
            }

            Repeater {
                id: lyricRepeater
                model: midi.backendSafe.lyricsSegments

                delegate: Item {
                    width: textItem.width
                    height: textItem.height

                    Text {
                        id: textItem
                        text: modelData
                        font.family: "JetBrainsMono Nerd Font"
                        font.pixelSize: 24
                        font.bold: true
                        color: "white"

                        x: 40
                        opacity: 0

                        Behavior on x { NumberAnimation { duration: 250; easing.type: Easing.OutCubic } }
                        Behavior on opacity { NumberAnimation { duration: 150 } }

                        Component.onCompleted: {
                            x = 0
                            opacity = 1
                        }
                    }
                }
            }
        }
        */
    }
}