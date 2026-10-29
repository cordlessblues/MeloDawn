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
                property var trackMessages: (typeof model !== "undefined" && model.messages) ? model.messages : []
                property var trackIdx: (typeof model !== "undefined" && model.trackIndex !== undefined) ? model.trackIndex : 0
                property string trackLabel: (typeof model !== "undefined" && model.trackLabel) ? model.trackLabel : ("Track " + trackIdx)

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
                        text: trackItem.trackLabel !== undefined ? trackItem.trackLabel : "Track"
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
        width: parent.width
        anchors.bottom: parent.bottom
        height: 50
        spacing: 0

        Repeater {
            model: (backend && backend.model) ? backend.model : null

            Rectangle {
                property color baseColor: {
                    if (model.trackIndex === "Meta")
                        return sysColorPallete.colors.subtext0;
                    return getRainbowColor(typeof model.trackIndex === "number" ? model.trackIndex : index);
                }

                width: midi.width / (model.trackCount || 1)
                height: 20
                anchors.bottom: parent.bottom

                color: Qt.lighter(model.active ? baseColor : Qt.darker(baseColor, 2.0), 0.8 + (model.velocity))

                Behavior on color {
                    ColorAnimation {
                        duration: 175
                        easing.type: Easing.OutCubic
                    }
                }

                transform: Scale {
                    yScale: model.scaleY || 1
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
