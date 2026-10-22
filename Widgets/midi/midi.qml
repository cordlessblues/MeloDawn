import QtQuick
Item {
    property var backend: null
    property var backendSafe: backend || {}
    id: midi
    width: 400
    height: 200

    Row {
        anchors.bottom: parent.bottom
        anchors.fill: parent
        spacing: 0

        Repeater {
            // FIX: Point the repeater model to the QAbstractListModel (`model`), not the backend object itself
            model: backend && backend.model ? backend.model : null

            Rectangle {
                property var baseColor: Qt.rgba(
                    model.color[0] / 255,
                    model.color[1] / 255,
                    model.color[2] / 255,
                    1
                )

                width: midi.width / model.trackCount
                height: 20

                color: Qt.lighter(
                    model.active ? baseColor : Qt.darker(baseColor, 1.5),
                    1 + model.velocity * 1.5
                )

                Behavior on color {
                    ColorAnimation {
                        duration: 175
                        easing.type: Easing.OutCubic
                    }
                }

                transform: Scale {
                    xScale: 1
                    yScale: model.scaleY

                    origin.x: width / 2
                    origin.y: height / 2

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
    Item {
        id: lyricsContainer
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        height: 50
        clip: true

        // Row {
        //     id: lyricRow
        //     spacing: 6
        //     anchors.verticalCenter: parent.verticalCenter

        //     Behavior on x {
        //         NumberAnimation { duration: 250; easing.type: Easing.OutCubic }
        //     }

        //     Repeater {
        //         id: lyricRepeater
        //         model: backend.lyricsSegments

        //         delegate: Item {
        //             width: textItem.width
        //             height: textItem.height

        //             Text {
        //                 id: textItem
        //                 text: modelData
        //                 font.pixelSize: 24
        //                 font.bold: true
        //                 color: "white"

        //                 x: 40
        //                 opacity: 0

        //                 // animate the bitch
        //                 Behavior on x { NumberAnimation { duration: 250; easing.type: Easing.OutCubic } }
        //                 Behavior on opacity { NumberAnimation { duration: 150 } }

        //                 Component.onCompleted: {
        //                     // do thing
        //                     x = 0
        //                     opacity = 1
        //                 }
        //             }
        //         }
        //     }
        // }
    }
}