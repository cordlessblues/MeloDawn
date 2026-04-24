cmake_minimum_required(VERSION 3.16)
project(QuickDawnTest LANGUAGES CXX)
set(QT_QML_GENERATE_QMLLS_INI ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 COMPONENTS Core Gui Qml Quick REQUIRED)

add_executable(QuickDawnTest
    Main.qml
)

target_link_libraries(QuickDawnTest
    Qt6::Core
    Qt6::Gui
    Qt6::Qml
    Qt6::Quick
)

set_target_properties(QuickDawnTest PROPERTIES
    QT_QML_MODULE_VERSION 1.0
    QT_QML_MODULE_URI QuickDawnTest
)