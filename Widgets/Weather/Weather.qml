import QtQuick
import QtQuick.Controls

Item {
    id: weather
    width: 400
    height: 600
    property var backend: null
    property string fontFamily: "Jetbrains Mono NF"

    Flickable {
        id: flick
        anchors.fill: parent
        boundsBehavior: Flickable.StopAtBounds
        flickableDirection: Flickable.VerticalFlick
        contentHeight: currentSection.height + hourlySection.height + dailySection.height
        clip: true

        Column {
            width: parent.width
            id: contentColumn
            spacing: 0

            // MARK: Current Weather
            Item {
                id: currentSection
                width: parent.width
                height: parent.height

                Column {
                    anchors.centerIn: parent
                    spacing: 16

                    Text {
                        text: backend && backend.current ? backend.current.temp + "°F" : ""
                        font.pixelSize: 48
                        font.bold: true
                        font.family: fontFamily
                        color: "#89b4fa"
                        horizontalAlignment: Text.AlignHCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: backend && backend.current ? backend.current.condition : ""
                        font.pixelSize: 32
                        font.family: fontFamily
                        color: "#cdd6f4"
                        horizontalAlignment: Text.AlignHCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: backend && backend.current ? "Feels like: " + backend.current.feels + "°F" : ""
                        font.pixelSize: 24
                        font.family: fontFamily
                        color: "#cdd6f4"
                        horizontalAlignment: Text.AlignHCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: backend && backend.current ? "Humidity: " + backend.current.humidity + "%" : ""
                        font.pixelSize: 24
                        font.family: fontFamily
                        color: "#cdd6f4"
                        horizontalAlignment: Text.AlignHCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: backend && backend.current ? "Wind: " + backend.current.wind_mph + " mph" : ""
                        font.pixelSize: 24
                        font.family: fontFamily
                        color: "#cdd6f4"
                        horizontalAlignment: Text.AlignHCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Image {
                        source: backend && backend.current ? backend.current.icon : ""
                        width: 128
                        height: 128
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }

            // MARK: Next 8 Hours
            Item {
                id: hourlySection
                width: parent.width
                height: parent.height

                Column {
                    anchors.centerIn: parent
                    spacing: 16

                    Text {
                        text: "Next 8 Hours"
                        font.pixelSize: 36
                        font.family: fontFamily
                        color: "#ffffff"
                        horizontalAlignment: Text.AlignHCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Flickable {
                        id: hourlyFlick
                        contentWidth: hourlyRow.width
                        contentHeight: 200
                        anchors.horizontalCenter: parent.horizontalCenter
                        clip: true
                        interactive: true

                        Row {
                            id: hourlyRow
                            spacing: 24

                            Repeater {
                                model: backend && backend.hourly ? backend.hourly : []

                                Column {
                                    spacing: 12
                                    width: 100

                                    Text {
                                        text: modelData.time
                                        font.pixelSize: 22
                                        font.family: fontFamily
                                        color: "#cdd6f4"
                                        horizontalAlignment: Text.AlignHCenter
                                        wrapMode: Text.Wrap
                                    }

                                    Image {
                                        source: modelData.icon
                                        width: 64
                                        height: 64
                                        anchors.horizontalCenter: parent.horizontalCenter
                                    }

                                    Text {
                                        text: modelData.temp + "°F"
                                        font.pixelSize: 24
                                        font.family: fontFamily
                                        color: "#89b4fa"
                                        horizontalAlignment: Text.AlignHCenter
                                    }

                                    Text {
                                        text: modelData.condition
                                        font.pixelSize: 18
                                        font.family: fontFamily
                                        color: "#cdd6f4"
                                        horizontalAlignment: Text.AlignHCenter
                                        wrapMode: Text.Wrap
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // MARK: Next 3 Days
            Item {
                id: dailySection
                width: parent.width
                height: parent.height

                Column {
                    anchors.centerIn: parent
                    spacing: 16

                    Text {
                        text: "Next 3 Days"
                        font.pixelSize: 36
                        font.family: fontFamily
                        color: "#ffffff"
                        horizontalAlignment: Text.AlignHCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Repeater {
                        model: backend && backend.daily ? backend.daily : []

                        Column {
                            spacing: 12
                            width: parent.width
                            anchors.horizontalCenter: parent.horizontalCenter

                            Row {
                                spacing: 24
                                anchors.horizontalCenter: parent.horizontalCenter

                                Image {
                                    source: modelData.icon
                                    width: 64
                                    height: 64
                                }

                                Column {
                                    spacing: 6

                                    Text {
                                        text: modelData.date
                                        font.pixelSize: 24
                                        font.family: fontFamily
                                        color: "#cdd6f4"
                                    }

                                    Text {
                                        text: "High: " + modelData.maxtemp + "°F"
                                        font.pixelSize: 22
                                        font.family: fontFamily
                                        color: "#89b4fa"
                                    }

                                    Text {
                                        text: "Low: " + modelData.mintemp + "°F"
                                        font.pixelSize: 22
                                        font.family: fontFamily
                                        color: "#89b4fa"
                                    }

                                    Text {
                                        text: "Condition: " + modelData.condition
                                        font.pixelSize: 20
                                        font.family: fontFamily
                                        color: "#cdd6f4"
                                        wrapMode: Text.Wrap
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}