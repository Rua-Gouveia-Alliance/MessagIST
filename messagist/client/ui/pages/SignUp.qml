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

    Dialog {
        id: wordList
        title: "Account recovery list of words."
        anchors.centerIn: parent

        Text {
            font.pointSize: 12
            color: "white"
            horizontalAlignment: Text.AlignHCenter
            text: {
                "The following list of words/numbers can be used to recover " +
                "your private key when you change devices. Memorize them or " +
                "store them somewhere safe.\n Words:\n"
            }
        }

        standardButtons: Dialog.Ok
        modal: true
        visible: false
        onAccepted: stack.pop()
        onRejected: stack.pop()
    }

    Column {
        spacing: 10
        anchors.horizontalCenter: parent.horizontalCenter

        Form {
            text: "Sign Up"
            formAction: (username, password) => {
                const result = messagist.signup(username, password);
                if (result.success) {
                    wordList.text += result.words;
                    wordList.visible = true;
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
