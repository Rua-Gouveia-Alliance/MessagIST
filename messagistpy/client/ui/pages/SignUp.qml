import QtQuick
import QtQuick.Controls
import ui

Column {
    id: signupPage
    spacing: 200

    Title {
        text: "MessagIST - Secure Messaging App"
        anchors.horizontalCenter: parent.horizontalCenter
    }
    Subtitle {
        text: "Sign Up"
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Form {
        text: "Sign Up"
        formAction: (username, password) => messagist.signup(username, password) && stack.pop()
        anchors.horizontalCenter: parent.horizontalCenter
    }
    ClickableText {
        text: "Already have an account? Log in instead."
        action: () => stack.pop()
        anchors.horizontalCenter: parent.horizontalCenter
    }
}
