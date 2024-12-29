import QtQuick
import QtQuick.Controls
import ui

Column {
    id: userChatsPage
    spacing: 10
    anchors.horizontalCenter: parent.horizontalCenter

    Title {
        text: "All chats"
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Row {
        id: newChat
        spacing: 5
        anchors.horizontalCenter: parent.horizontalCenter

        Text {
            text: "Start a new chat:"
            font.pointSize: 12
            color: "white"
        }
        TextField {
            id: newPartner
            placeholderText: "Username"
            font.pointSize: 12
        }
        Button {
            id: button
            text: "New chat"
            font.pointSize: 12
            onClicked: {
                messagist.startChat(newPartner.text) && stack.push("Chat.qml", { partner: newPartner.text })
            }
        }
    }

    Repeater {
        model: Object.keys(messagist.chats)

        ChatPreview {
            required property string modelData
            partner: modelData
            action: () => stack.push("Chat.qml", { partner: modelData })
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }
}
