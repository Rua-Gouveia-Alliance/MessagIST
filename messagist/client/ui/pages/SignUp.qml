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
        id: wordListDialog
        title: "Identity key recovery list of words."
        anchors.centerIn: parent

        Column {
            spacing: 10

            Text {
                font.pointSize: 12
                color: "white"
                horizontalAlignment: Text.AlignLeft
                text: {
                    "The following list of words/numbers can be used to recover " +
                    "your identity key when you change devices. Memorize them or " +
                    "store them somewhere safe.\n Words:\n"
                }
            }
            TextEdit {
                id: wordList
                font.pointSize: 12
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                anchors.horizontalCenter: parent.horizontalCenter
                readOnly: true
                selectByMouse: true
            }
        }

        standardButtons: Dialog.Ok
        modal: true
        visible: false
        onAccepted: stack.pop()
        onRejected: stack.pop()
    }

    Dialog {
        id: twoFactorAuthenticationDialog
        title: "Two-Factor Authentication."
        anchors.centerIn: parent

        Column {
            spacing: 10

            Text {
                font.pointSize: 12
                color: "white"
                text: "Please enter your two-factor authentication token:"
            }
            TextField {
                id: twoFactorToken
                placeholderText: "Token"
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true
        visible: false
        onAccepted: {
            const result = messagist.submitTwoFactorTokenSignUp(
                formSignUp.username, formSignUp.password, twoFactorToken.text
            );
            twoFactorToken.text = "";
            if (result.success) {
                twoFactorAuthenticationDialog.visible = false;
                wordList.text = result.words;
                wordListDialog.visible = true;
            } else {
                errorMessage.text = result.error;
                errorMessage.visible = true;
            }
        }
    }

    Column {
        spacing: 10
        anchors.horizontalCenter: parent.horizontalCenter

        Form {
            id: formSignUp
            text: "Sign Up"
            formAction: (ist_email, password) => {
                const result = messagist.signup(ist_email, password);
                if (result.success) {
                    errorMessage.text = "";
                    twoFactorAuthenticationDialog.visible = true
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
        action: () => {
            stack.pop();
        }
        anchors.horizontalCenter: parent.horizontalCenter
    }
}
