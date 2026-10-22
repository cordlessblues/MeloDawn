import QtQuick

Item {
    id: clock
    anchors.fill: parent

    property var backend: null
    // Fallback safely to empty object or fallback object structure
    property var backendSafe: backend ? backend : { ampm: "AM", seconds: 0, time: "%H:%M:%S", date: "%A, %B %d" }

    property real tickHeight: 24
    property real tickWidth: tickHeight / 4
    property real cornerRadius: 60
    property int count: 60
    property int animDuration: 200

    property int paddingH: 20
    property int paddingV: 20
    property int effectivePaddingH: paddingH + tickWidth / 2
    property int effectivePaddingV: paddingV + tickHeight / 2

    // Safe fallback check for ampm
    property color highlightColor: (backendSafe && backendSafe.ampm === "AM") ? "white" : '#f9f4bd'

    Repeater {
        model: 60
        Rectangle {
            // Safe fallback check for seconds
            property int currentSecond: (backendSafe && backendSafe.seconds !== undefined) ? backendSafe.seconds : 0
            property int distanceFromSeconds: (index - currentSecond + 60) % 60
            property real gradientFactor: 1 - distanceFromSeconds / 60

            property real px: 0
            property real py: 0
            property real tickAngle: 0

            function updatePosition() {
                var perimeterStraightH = clock.width - 2*clock.cornerRadius - 2*clock.effectivePaddingH
                var perimeterStraightV = clock.height - 2*clock.cornerRadius - 2*clock.effectivePaddingV
                var perimeterCorner = Math.PI * clock.cornerRadius / 2
                var totalPerimeter = 2*perimeterStraightH + 2*perimeterStraightV + 4*perimeterCorner

                var seg = index / 60 * totalPerimeter
                var s = seg

                if (s < perimeterStraightH) {
                    px = clock.effectivePaddingH + clock.cornerRadius + s
                    py = clock.effectivePaddingV
                    tickAngle = 0
                } else if (s < perimeterStraightH + perimeterCorner) {
                    var a = (s - perimeterStraightH) / clock.cornerRadius
                    px = clock.width - clock.effectivePaddingH - clock.cornerRadius + clock.cornerRadius * Math.sin(a)
                    py = clock.effectivePaddingV + clock.cornerRadius - clock.cornerRadius * Math.cos(a)
                    tickAngle = a * 180 / Math.PI
                } else if (s < perimeterStraightH + perimeterCorner + perimeterStraightV) {
                    px = clock.width - clock.effectivePaddingH
                    py = clock.effectivePaddingV + clock.cornerRadius + (s - perimeterStraightH - perimeterCorner)
                    tickAngle = 90
                } else if (s < perimeterStraightH + 2*perimeterCorner + perimeterStraightV) {
                    var a = (s - perimeterStraightH - perimeterCorner - perimeterStraightV) / clock.cornerRadius
                    px = clock.width - clock.effectivePaddingH - clock.cornerRadius + clock.cornerRadius * Math.cos(a)
                    py = clock.height - clock.effectivePaddingV - clock.cornerRadius + clock.cornerRadius * Math.sin(a)
                    tickAngle = 90 + a*180/Math.PI
                } else if (s < perimeterStraightH + 2*perimeterCorner + perimeterStraightV + perimeterStraightH) {
                    px = clock.width - clock.effectivePaddingH - clock.cornerRadius - (s - (perimeterStraightH + 2*perimeterCorner + perimeterStraightV))
                    py = clock.height - clock.effectivePaddingV
                    tickAngle = 180
                } else if (s < perimeterStraightH + 3*perimeterCorner + perimeterStraightV + perimeterStraightH) {
                    var a = (s - (perimeterStraightH + 2*perimeterCorner + perimeterStraightV + perimeterStraightH)) / clock.cornerRadius
                    px = clock.effectivePaddingH + clock.cornerRadius - clock.cornerRadius * Math.sin(a)
                    py = clock.height - clock.effectivePaddingV - clock.cornerRadius + clock.cornerRadius * Math.cos(a)
                    tickAngle = 180 + a*180/Math.PI
                } else if (s < 2*perimeterStraightH + 3*perimeterCorner + 2*perimeterStraightV) {
                    px = clock.effectivePaddingH
                    py = clock.height - clock.effectivePaddingV - clock.cornerRadius - (s - (perimeterStraightH + 3*perimeterCorner + perimeterStraightV + perimeterStraightH))
                    tickAngle = 270
                } else {
                    var a = (s - (2*perimeterStraightH + 3*perimeterCorner + 2*perimeterStraightV)) / clock.cornerRadius
                    px = clock.effectivePaddingH + clock.cornerRadius - clock.cornerRadius * Math.cos(a)
                    py = clock.effectivePaddingV + clock.cornerRadius - clock.cornerRadius * Math.sin(a)
                    tickAngle = 270 + a*180/Math.PI
                }

                x = px - clock.effectivePaddingH/8
                y = py - clock.effectivePaddingV/4
            }

            width: clock.tickWidth
            height: clock.tickHeight
            radius: 4
            color: index === currentSecond ? clock.highlightColor : Qt.rgba(gradientFactor, 0.5, 1 - gradientFactor, 1)
            scale: index === currentSecond ? 1.5 : 1
            
            Component.onCompleted: updatePosition()
            
            Connections {
                target: clock
                function onWidthChanged() { updatePosition() }
                function onHeightChanged() { updatePosition() }
            }

            transform: Rotation {
                origin.x: width/2
                origin.y: height/2
                angle: tickAngle
            }

            Behavior on scale {
                NumberAnimation { duration: clock.animDuration; easing.type: Easing.InOutQuad }
            }
            Behavior on color {
                ColorAnimation { duration: clock.animDuration; easing.type: Easing.InOutQuad }
            }
        }
    }

    Text {
        id: timeText
        text: (backendSafe && backendSafe.time !== undefined) ? backendSafe.time : "%H:%M:%S"
        anchors.centerIn: parent
        font.family: "Jetbrains Mono NF"
        font.pointSize: 48
        color: clock.highlightColor
    }

    Text {
        id: dateText
        text: (backendSafe && backendSafe.date !== undefined) ? backendSafe.date : "%A, %B %d"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: timeText.bottom
        anchors.topMargin: 8
        font.family: "Jetbrains Mono NF"
        font.pointSize: 20
        color: clock.highlightColor
    }

    Behavior on highlightColor {
        ColorAnimation { duration: clock.animDuration; easing.type: Easing.InOutQuad }
    }
}