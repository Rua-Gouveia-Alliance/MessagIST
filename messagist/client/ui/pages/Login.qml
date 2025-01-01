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

    Dialog {
        id: recoveryDialog
        title: "Identity key recovery."
        anchors.centerIn: parent

        Column {
            spacing: 10

            Text {
                font.pointSize: 12
                color: "white"
                horizontalAlignment: Text.AlignLeft
                text: {
                    "Identity key not found. Please insert the word list used to " +
                    "recover it:"
                }
            }
            TextArea {
                id: wordList
                placeholderText: "Word list"
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true
        visible: false
        onAccepted: {
            console.log(form.password)
            const success = messagist.recoverIdentityKey(wordList.text, form.password);
            if (success) {
                stack.push("UserChats.qml");
            } else {
                messagist.logout("");
            }
        }
        onRejected: messagist.logout("")
    }
    // 2FA dialog
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
            const result = messagist.submitTwoFactorToken(form.username, form.password, twoFactorToken.text);
            if (result.success) {
                if (result.recovery) {
                    recoveryDialog.visible = true;
                } else {
                    stack.push("UserChats.qml");
                }
            } else {
                errorMessage.text = result.error;
                errorMessage.visible = true;
                twoFactorAuthenticationDialog.visible = false;
            }
        }
    }

    Column {
        spacing: 10
        anchors.horizontalCenter: parent.horizontalCenter

        Form  {
            id: formLogin
            text: "Login"
            formAction: (username, password) => {
                const result = messagist.login(username, password);
                if (result.success) {
                    twoFactorAuthenticationDialog.visible = true;
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
        action: () => {
            stack.push("SignUp.qml");
        }

        anchors.horizontalCenter: parent.horizontalCenter
    }
}
