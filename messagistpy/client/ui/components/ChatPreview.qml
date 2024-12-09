import QtQuick
import QtQuick.Controls

Rectangle {
    property alias partner: label.text
    required property var action

    id: chatPreview
    width: 200
    height: label.height + 50
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
    MouseArea {
        id: chatPreviewMouseArea
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: action()
    }
}
