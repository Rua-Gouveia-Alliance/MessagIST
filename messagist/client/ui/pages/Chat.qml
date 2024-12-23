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

    Dialog {
        id: dialog
        title: "Insert the passphrase for this conversation"
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true
        visible: messagist.chats[partner][0]

        onAccepted: messagist.setChatPassphrase(partner, passphrase.text)
        onRejected: stack.pop()
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
            onClicked: messagist.sendMessage(message.text, partner);
        }
    }
}
