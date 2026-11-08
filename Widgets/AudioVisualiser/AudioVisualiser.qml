import QtQuick
import QtQuick.Controls
import QtMultimedia

Item {
    id: midi
    width: 1280
    height: 400

    property var backend: null
    property var backendSafe: backend || {}
    property bool isDebugMode: false

    property var rainbowPalette: {
        var p = (typeof sysColorPallete !== "undefined" && sysColorPallete.colors) ? sysColorPallete.colors : {};
        return [p.red, p.peach, p.yellow, p.green, p.sky, p.blue, p.mauve, p.pink, p.teal];
    }

    function getRainbowColor(index) {
        return rainbowPalette[index % rainbowPalette.length];
    }

    MediaPlayer {
        id: bgMediaPlayer
        source: backend ? backend.audioSource : ""
        audioOutput: AudioOutput {
            id: audioOut
            volume: 1.0
        }
    }

    Connections {
        target: backend
        function onAudioPlaybackTriggered(play) {
            if (play) {
                bgMediaPlayer.stop();
                bgMediaPlayer.play();
            } else {
                bgMediaPlayer.stop();
            }
        }
    }

    // MARK: DEBUG VIEW
    Row {
        id: debugContainer
        visible: isDebugMode
        anchors.top: parent.top
        anchors.bottom: visualizerRow.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 4
        spacing: 2

        Repeater {
            model: (backend && backend.model) ? backend.model : null

            Item {
                id: trackItem
                // Access roles via model.<rolename>
                property var trackMessages: model.messages || []
                property var trackIdx: model.trackIndex !== undefined ? model.trackIndex : 0
                property string trackLabel: "Track " + trackIdx

                property color trackColor: {
                    if (trackIdx === "Meta")
                        return sysColorPallete.colors.subtext0 || "#6f767d";
                    return getRainbowColor(typeof trackIdx === "number" ? trackIdx : index);
                }

                width: (parent.width / ((backend && backend.model && backend.model.rowCount() > 0) ? backend.model.rowCount() : 1)) - 2
                height: parent.height

                Column {
                    anchors.fill: parent
                    spacing: 2

                    Text {
                        text: trackItem.trackLabel
                        color: trackItem.trackColor
                        font.family: "JetBrainsMono Nerd Font"
                        font.pixelSize: 11
                        font.bold: true
                    }

                    ListView {
                        id: trackDebugView
                        width: parent.width
                        height: parent.height - 15
                        clip: true
                        model: trackItem.trackMessages

                        onCountChanged: {
                            if (count > 0)
                                positionViewAtEnd();
                        }

                        delegate: Text {
                            text: modelData
                            font.family: "JetBrainsMono Nerd Font"
                            font.pixelSize: 10
                            color: trackItem.trackColor
                            width: trackDebugView.width
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }
    }

    // MARK: MIDI Visualizer Row
    Row {
        id: visualizerRow
        anchors.right: parent.right
        anchors.rightMargin: 8
        anchors.left: parent.left
        anchors.leftMargin: 8
        anchors.bottom: parent.bottom
        height: parent.height
        spacing: 4

        Repeater {
            model: (backend && backend.model) ? backend.model : null

            Rectangle {
                property bool isMidi: model.audioType === "midi"

                property color baseColor: {
                    if (model.trackIndex === "Meta")
                        return sysColorPallete.colors.subtext0;
                    return getRainbowColor(typeof model.trackIndex === "number" ? model.trackIndex : index);
                }

                width: (visualizerRow.width - (visualizerRow.spacing * ((backend.model.rowCount() > 0 ? backend.model.rowCount() : 8) - 1))) / (backend.model.rowCount() > 0 ? backend.model.rowCount() : 8)

                height: isMidi ? 8 : 8 + (model.scaleY * parent.height)

                radius: isMidi ? (height / 2) : (width / 2)

                anchors.bottom: parent.bottom

                anchors.bottomMargin: isMidi ? 8 + (model.scaleY * (parent.height - 30)) : 8

                color: Qt.lighter(model.active ? baseColor : Qt.darker(baseColor, 2.0), 0.8 + (model.velocity / 127.0))

                Behavior on color {
                    ColorAnimation {
                        duration: 175
                        easing.type: Easing.OutCubic
                    }
                }

                Behavior on height {
                    NumberAnimation {
                        duration: 175
                        easing.type: Easing.OutCubic
                    }
                }

                Behavior on anchors.bottomMargin {
                    NumberAnimation {
                        duration: 120
                        easing.type: Easing.OutCubic
                    }
                }
            }
        }
    }

    MouseArea { // MARK: input
        anchors.fill: parent
        onClicked: {
            if (backendSafe) {
                backendSafe.play();
            }
        }
        onWheel: wheel => {
            if (wheel.angleDelta.y > 0) {
                backendSafe.previous();
            } else {
                backendSafe.next();
            }
            wheel.accepted = true;
        }
    }

    // MARK: Lyrics Container
    Item {
        id: lyricsContainer
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 15
        width: parent.width - 40
        height: 40
        clip: true

        Row {
            id: lyricRow
            spacing: 6
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter

            Repeater {
                id: lyricRepeater
                model: backendSafe.lyricsSegments

                delegate: Text {
                    text: modelData
                    font.family: "JetBrainsMono Nerd Font"
                    font.pixelSize: 18
                    font.bold: true
                    color: sysColorPallete.colors.text || "white"

                    Behavior on x {
                        NumberAnimation {
                            duration: 150
                        }
                    }
                }
            }
        }
    }
}
