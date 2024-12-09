import QtQuick
import QtQuick.Controls
import ui

Window {
    id: window
    title: "MessagIST"
    color: "Brown"
    visible: true
    visibility: Window.Maximized

    StackView {
        id: stack
        initialItem: Login {}
        anchors.fill: parent
    }
}
