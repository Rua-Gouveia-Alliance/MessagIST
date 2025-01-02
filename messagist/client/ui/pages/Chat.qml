import QtQuick
import QtQuick.Controls
import ui

Column {
    required property string partner

    id: chatPage
    spacing: 10

    Button {
        id: button
        text: "Go Back"
        onClicked: stack.pop()
    }

    Title {
        text: `Conversation with ${partner}`
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Repeater {
        model: messagist.chats[partner].slice(1)
        Message {
            required property var modelData
            messageObject: modelData
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }

    Row {
        spacing: 5
        anchors.horizontalCenter: parent.horizontalCenter

        TextField {
            id: message
            placeholderText: "Message"
            font.pointSize: 12
        }
        Button {
            id: send
            text: "Send"
            font.pointSize: 12
            onClicked: {
                if (messagist.sendMessage(message.text, partner)) {
                    message.text = "";
                } else {
                    stack.pop()
                }
            }
        }
    }

    Dialog {
        id: dialog
        title: "Insert the passphrase for this conversation"
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true
        visible: messagist.chats[partner][0]
        anchors.centerIn: parent

        TextField {
            id: passphrase
            placeholderText: "Passphrase"
        }

        onAccepted: messagist.setChatPassphrase(partner, passphrase.text) || stack.pop()
        onRejected: stack.pop()
    }
}
