import QtQuick

Rectangle {
    property alias contents: label.text

    id: message
    width: label.width + 50
    height: label.height + 25
    color: "dodgerblue"
    border.color: "black"
    border.width: 5
    radius: 90

    Text {
        id: label
        font.pointSize: 12
        color: "white"
        anchors.centerIn: parent
    }
}
