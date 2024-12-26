import QtQuick
import QtQuick.Controls
import ui

Column {
    id: signupPage
    spacing: 30

    Title {
        text: "MessagIST - Secure Messaging App"
        anchors.horizontalCenter: parent.horizontalCenter
    }
    Subtitle {
        text: "Sign Up"
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Column {
        spacing: 10
        anchors.horizontalCenter: parent.horizontalCenter

        Form {
            text: "Sign Up"
            formAction: (username, password) => {
                const result = messagist.signup(username, password);
                if (result.success) {
                    stack.pop()
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
        text: "Already have an account? Login instead."
        action: () => stack.pop()
        anchors.horizontalCenter: parent.horizontalCenter
    }
}
