import QtQuick
import QtQuick.Controls
import ui

Column {
    id: loginPage
    spacing: 30

    Title {
        text: "MessagIST - Secure Messaging App"
        anchors.horizontalCenter: parent.horizontalCenter
    }
    Subtitle {
        text: "Login"
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Column {
        spacing: 10
        anchors.horizontalCenter: parent.horizontalCenter

        Form {
            text: "Login"
            formAction: (username, password) => {
                const result = messagist.login(username, password);
                if (result.success) {
                    stack.push("UserChats.qml");
                } else {
                    errorMessage.text = result.error;
                    errorMessage.visible = true;
                }
            }
        }

        Text {
            id: errorMessage
            visible: false
            color: "red"
            font.pixelSize: 14
            text: "" // The error message will be set dynamically
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }

    ClickableText {
        text: "Don't have an account? Sign up instead."
        action: () => stack.push("SignUp.qml")
        anchors.horizontalCenter: parent.horizontalCenter
    }
}
