
import QtQuick
import QtQuick.Controls

Column {
    required property var formAction
    property alias text: button.text
    property alias password: password.text

    id: formLogin
    spacing: 5

    Row {
        id: fields
        spacing: 5

        TextField {
            id: username
            placeholderText: "username"
        }
        TextField {
            id: password
            placeholderText: "Password"
            passwordCharacter: "●"
            passwordMaskDelay: 500
            echoMode: TextInput.Password
        }
    }
    Button {
        id: button
        onClicked: formAction(username.text, password.text)
    }
}
