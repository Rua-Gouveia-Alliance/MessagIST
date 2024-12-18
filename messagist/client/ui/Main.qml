import QtQuick
import QtQuick.Controls
import ui

Window {
    id: window
    title: "MessagIST"
    color: "Brown"
    visible: true
    visibility: Window.Maximized

    Connections {
        target: messagist
        function onLoggedOut() {
            stack.pop(null);
        }
    }

    StackView {
        id: stack
        initialItem: Login {}
        anchors.fill: parent
    }
}
