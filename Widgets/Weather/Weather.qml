import QtQuick
import QtQuick.Controls

Item {
    id: weather
    anchors.fill: parent
    property int animDuration: 200
    property var backend: null
    property string fontFamily: "JetBrainsMono Nerd Font"

    property var bSafe: backend || {}
    property var currentData: bSafe.current || {}
    property var hourlyData: bSafe.hourly || []
    property var dailyData: bSafe.daily || []

    // Helper function to map weather condition text to Nerd Font glyphs
    function getWeatherIcon(conditionText) {
        if (!conditionText)
            return "󰖔"; // Default weather icon
        let cond = conditionText.toLowerCase();
        if (cond.includes("sun") || cond.includes("clear"))
            return "";
        if (cond.includes("partly") || cond.includes("cloud"))
            return "󰅟";
        if (cond.includes("thunder") || cond.includes("storm"))
            return "󰙾";
        if (cond.includes("rain") || cond.includes("drizzle") || cond.includes("shower"))
            return "󰖗";
        if (cond.includes("snow") || cond.includes("ice") || cond.includes("sleet"))
            return "󰼶";
        if (cond.includes("fog") || cond.includes("mist"))
            return "󰖑";
        if (cond.includes("wind"))
            return "󰖝";
        return "󰖔";
    }

    Flickable {
        id: flick
        anchors.fill: parent
        anchors.topMargin: 8
        contentHeight: mainColumn.implicitHeight + 32
        flickableDirection: Flickable.VerticalFlick
        boundsBehavior: Flickable.StopAtBounds
        clip: true

        Column {
            id: mainColumn
            width: parent.width
            spacing: 12

            // MARK: Current Weather Banner
            Item {
                width: parent.width
                height: 80

                Rectangle {
                    id: tempBar
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    width: 8
                    radius: 4
                    color: sysColorPallete.colors.primaryAccent
                }

                Text {
                    id: iconText
                    text: getWeatherIcon(currentData.condition)
                    font.family: fontFamily
                    font.pixelSize: 46
                    color: sysColorPallete.colors.primaryAccent
                    anchors.left: tempBar.right
                    anchors.leftMargin: 12
                    anchors.verticalCenter: parent.verticalCenter
                }

                Text {
                    id: tempText
                    text: currentData.temp !== undefined ? Math.round(currentData.temp) + "°F" : "--°F"
                    font.family: fontFamily
                    font.pixelSize: 42
                    font.bold: true
                    color: sysColorPallete.colors.primaryAccent
                    anchors.left: iconText.right
                    anchors.leftMargin: 12
                    anchors.top: parent.top
                }

                Text {
                    id: conditionText
                    text: currentData.condition || "Loading..."
                    font.family: fontFamily
                    font.pixelSize: 20
                    color: sysColorPallete.colors.text
                    anchors.left: tempText.left
                    anchors.top: tempText.bottom
                    anchors.topMargin: -4
                }

                Column {
                    anchors.right: parent.right
                    anchors.rightMargin: 12
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 4

                    Text {
                        text: "Feels: " + (currentData.feels !== undefined ? Math.round(currentData.feels) + "°F" : "--")
                        font.family: fontFamily
                        font.pixelSize: 18
                        color: sysColorPallete.colors.subtext1 || "#a6adc8"
                        horizontalAlignment: Text.AlignRight
                        anchors.right: parent.right
                    }
                    Text {
                        text: "Wind: " + (currentData.wind_mph !== undefined ? currentData.wind_mph + "mph " + (currentData.wind_dir || "") : "--")
                        font.family: fontFamily
                        font.pixelSize: 18
                        color: sysColorPallete.colors.subtext1 || "#a6adc8"
                        horizontalAlignment: Text.AlignRight
                        anchors.right: parent.right
                    }
                    Text {
                        text: "Humidity: " + (currentData.humidity !== undefined ? currentData.humidity + "%" : "--")
                        font.family: fontFamily
                        font.pixelSize: 18
                        color: sysColorPallete.colors.subtext1 || "#a6adc8"
                        horizontalAlignment: Text.AlignRight
                        anchors.right: parent.right
                    }
                }
            }

            // MARK: Hourly Timeline
            Item {
                width: parent.width
                height: hourlyCol.implicitHeight

                Column {
                    id: hourlyCol
                    width: parent.width
                    spacing: 8

                    Text {
                        text: "HOURLY FORECAST"
                        font.family: fontFamily
                        font.pixelSize: 18
                        font.bold: true
                        color: sysColorPallete.colors.subtext0
                        leftPadding: 20
                    }

                    Flickable {
                        id: hourRowFlick
                        width: parent.width
                        height: 75
                        contentWidth: hourlyRow.implicitWidth + 32
                        flickableDirection: Flickable.HorizontalFlick
                        boundsBehavior: Flickable.StopAtBounds
                        clip: true

                        Row {
                            id: hourlyRow
                            anchors.left: parent.left
                            anchors.leftMargin: 20
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 16

                            Repeater {
                                model: hourlyData

                                Item {
                                    width: 80
                                    height: hourRowFlick.height

                                    Column {
                                        anchors.centerIn: parent
                                        spacing: 0

                                        Text {
                                            text: modelData.time
                                            font.family: fontFamily
                                            font.pixelSize: 16
                                            color: sysColorPallete.colors.subtext1
                                            anchors.horizontalCenter: parent.horizontalCenter
                                        }

                                        Text {
                                            text: getWeatherIcon(modelData.condition)
                                            font.family: fontFamily
                                            font.pixelSize: 24
                                            color: sysColorPallete.colors.primaryAccent
                                            anchors.horizontalCenter: parent.horizontalCenter
                                        }

                                        Text {
                                            text: Math.round(modelData.temp) + "°"
                                            font.family: fontFamily
                                            font.pixelSize: 18
                                            font.bold: true
                                            color: sysColorPallete.colors.text
                                            anchors.horizontalCenter: parent.horizontalCenter
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // MARK: 3-Day Forecast List
            Item {
                width: parent.width
                height: dailyCol.implicitHeight

                Column {
                    id: dailyCol
                    width: parent.width
                    spacing: 8

                    Text {
                        text: "3-DAY FORECAST"
                        font.family: fontFamily
                        font.pixelSize: 18
                        font.bold: true
                        color: sysColorPallete.colors.subtext0
                        leftPadding: 20
                    }

                    Repeater {
                        model: dailyData

                        Item {
                            width: parent.width
                            height: 60

                            Rectangle {
                                id: dayBar
                                anchors.left: parent.left
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                width: 4
                                radius: 4
                                color: sysColorPallete.colors.green
                            }

                            Text {
                                id: dayIcon
                                text: getWeatherIcon(modelData.condition)
                                font.family: fontFamily
                                font.pixelSize: 26
                                color: sysColorPallete.colors.green
                                anchors.left: dayBar.right
                                anchors.leftMargin: 12
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                id: dayDate
                                text: modelData.date
                                font.family: fontFamily
                                font.pixelSize: 22
                                font.bold: true
                                color: sysColorPallete.colors.text
                                anchors.left: dayIcon.right
                                anchors.leftMargin: 12
                                anchors.top: parent.top
                                anchors.topMargin: 4
                            }

                            Text {
                                text: modelData.condition
                                font.family: fontFamily
                                font.pixelSize: 18
                                color: sysColorPallete.colors.subtext1
                                anchors.left: dayDate.left
                                anchors.top: dayDate.bottom
                            }

                            Text {
                                text: Math.round(modelData.maxtemp) + "° / " + Math.round(modelData.mintemp) + "°"
                                font.family: fontFamily
                                font.pixelSize: 22
                                color: sysColorPallete.colors.primaryAccent
                                anchors.right: parent.right
                                anchors.rightMargin: 12
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }
                }
            }
        }
    }
}
