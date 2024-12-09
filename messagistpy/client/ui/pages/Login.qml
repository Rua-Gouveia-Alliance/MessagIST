import QtQuick
import QtQuick.Controls
import ui

Column {
    id: loginPage
    spacing: 200

    Title {
        text: "MessagIST - Secure Messaging App"
        anchors.horizontalCenter: parent.horizontalCenter
    }
    Subtitle {
        text: "Login"
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Form {
        text: "Login"
        formAction: (username, password) => messagist.login(username, password) && stack.push("UserChats.qml")
        anchors.horizontalCenter: parent.horizontalCenter
    }
    ClickableText {
        text: "Don\'t have an account? Sign up instead."
        action: () => stack.push("SignUp.qml")
        anchors.horizontalCenter: parent.horizontalCenter
    }
}
