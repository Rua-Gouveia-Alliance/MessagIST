import QtQuick
import QtQuick.Controls

Text {
    property alias text: clickableText.text
    required property var action

    id: clickableText
    font.pointSize: 12
    color: "white"
    horizontalAlignment: Text.AlignHCenter
    MouseArea {
        id: loginPromptMouseArea
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: action()
    }
}
