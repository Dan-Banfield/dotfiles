import QtQuick 2.15
import QtQuick.Controls 2.15

FocusScope {
    id: root
    objectName: "blue-night"
    width: 1920
    height: 1080
    property color textColor: "#c1d5f0"
    property color mutedColor: "#8395af"
    property string fontFamily: config.stringValue("Font") || "JetBrainsMono Nerd Font"
    property date now: new Date()
    property bool busy: false
    property string feedback: ""
    property bool failed: false
    property string powerAction: ""
    property bool blurAvailable: GraphicsInfo.api === GraphicsInfo.OpenGL

    function attemptLogin() {
        if (busy) return;
        if (!account.editText.trim().length) {
            feedback = "Choose a user account.";
            account.forceActiveFocus();
            return;
        }
        if (session.count === 0 || session.currentIndex < 0 || session.currentIndex >= session.count) {
            feedback = "No desktop sessions are available.";
            return;
        }
        failed = false;
        feedback = "Signing in…";
        busy = true;
        sddm.login(account.editText.trim(), password.text, session.currentIndex);
    }

    function confirmPower(action) {
        powerAction = action;
        confirmation.open();
        cancelButton.forceActiveFocus();
    }

    Timer { interval: 1000; running: true; repeat: true; onTriggered: root.now = new Date() }
    Connections {
        target: sddm
        function onLoginFailed() {
            root.busy = false;
            root.failed = true;
            root.feedback = "Couldn't sign in. Check your password.";
            password.clear();
            password.forceActiveFocus();
            shake.restart();
        }
        function onLoginSucceeded() {
            root.feedback = "Welcome back.";
            card.opacity = 0;
        }
        function onInformationMessage(message) { root.feedback = message; }
    }
    Keys.onEscapePressed: {
        if (confirmation.opened) confirmation.close();
        else if (!root.busy) { password.clear(); root.feedback = ""; root.failed = false; }
    }

    Rectangle { anchors.fill: parent; color: "#0d1423" }
    Image {
        id: wallpaper
        anchors.fill: parent
        source: Qt.resolvedUrl(config.stringValue("Background") || "wallpaper.jpeg")
        fillMode: Image.PreserveAspectCrop
        asynchronous: false
        smooth: true
    }
    Loader {
        anchors.fill: parent
        active: root.blurAvailable && wallpaper.status === Image.Ready
        sourceComponent: Component { SoftBlur { sourceItem: wallpaper } }
    }
    Rectangle {
        anchors.fill: parent
        color: "#65080c14"
    }
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0; color: "#180d1423" }
            GradientStop { position: 1; color: "#85080c14" }
        }
    }

    Item {
        id: card
        anchors.centerIn: parent
        width: 480
        height: 580
        scale: Math.min(1, (root.height - 160) / height, (root.width - 40) / width)
        opacity: 0
        transform: Translate { id: entrance; y: 24 }
        Behavior on opacity { NumberAnimation { duration: 250 } }
        Rectangle {
            x: -14; y: -6
            width: parent.width + 28; height: parent.height + 28
            radius: 44; color: "#10000000"
        }
        Rectangle {
            x: -7; y: 0
            width: parent.width + 14; height: parent.height + 14
            radius: 38; color: "#20000000"
        }
        Rectangle {
            anchors.fill: parent
            radius: 32
            gradient: Gradient {
                GradientStop { position: 0; color: "#7397c8" }
                GradientStop { position: 0.5; color: "#39485e" }
                GradientStop { position: 1; color: "#203758" }
            }
            Rectangle {
                anchors.fill: parent
                anchors.margins: 1
                radius: 31
                color: "#ed0d1423"
            }
        }
        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 30
            width: 352
            spacing: 0
            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 132; height: 28; radius: 14
                color: "#203758"
                Row {
                    anchors.centerIn: parent
                    spacing: 8
                    Icon { width: 13; height: 13; kind: "lock"; ink: "#b9d5f4" }
                    Text { text: "SIGN IN"; color: "#b9d5f4"; font.family: root.fontFamily; font.pixelSize: 10; font.letterSpacing: 1 }
                }
            }
            Item { width: 1; height: 22 }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: Qt.formatTime(root.now, "hh:mm AP")
                color: root.textColor
                font.family: root.fontFamily
                font.pixelSize: 54
                font.bold: true
            }
            Item { width: 1; height: 8 }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: Qt.formatDate(root.now, "dddd, d MMMM")
                color: root.mutedColor
                font.family: root.fontFamily
                font.pixelSize: 12
            }
            Item { width: 1; height: 22 }
            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 48; height: 2; radius: 1
                color: "#8aade0"
                opacity: 0.6
            }
            Item { width: 1; height: 24 }
            Choice {
                id: account
                objectName: "account"
                width: parent.width
                editable: true
                placeholder: "User account"
                model: userModel
                textRole: "name"
                currentIndex: userModel.lastIndex >= 0 ? userModel.lastIndex : 0
                enabled: !root.busy
                Accessible.name: "User account"
                KeyNavigation.tab: password
                KeyNavigation.backtab: session
            }
            Item { width: 1; height: 12 }
            TextField {
                id: password
                objectName: "password"
                width: parent.width; height: 56
                enabled: !root.busy
                leftPadding: 20; rightPadding: 20
                color: root.textColor
                placeholderText: "Password"
                placeholderTextColor: root.mutedColor
                font.family: root.fontFamily
                font.pixelSize: 14
                echoMode: TextInput.Password
                selectByMouse: true
                selectionColor: "#8aade0"
                selectedTextColor: "#101c30"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                Accessible.name: "Password"
                onAccepted: root.attemptLogin()
                onTextEdited: { root.failed = false; root.feedback = ""; }
                KeyNavigation.tab: loginButton
                KeyNavigation.backtab: account
                transform: Translate { id: passwordShake }
                background: Rectangle {
                    radius: 28
                    color: root.failed ? "#f2b5c2" : (keyboard.capsLock ? "#eed6a4" : "#8aade0")
                    gradient: !root.failed && !keyboard.capsLock ? passwordGradient : null
                    Gradient {
                        id: passwordGradient
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0; color: "#517fc4" }
                        GradientStop { position: 0.5; color: "#8aade0" }
                        GradientStop { position: 1; color: "#b9d5f4" }
                    }
                    Rectangle {
                        anchors.fill: parent; anchors.margins: 2
                        radius: 26; color: "#101c30"
                    }
                    Behavior on color { ColorAnimation { duration: 180 } }
                }
            }
            Item {
                width: parent.width; height: 36
                Text {
                    anchors.centerIn: parent
                    text: root.feedback.length ? root.feedback : (keyboard.capsLock ? "Caps Lock is on" : "")
                    color: root.failed ? "#f2b5c2" : (keyboard.capsLock ? "#eed6a4" : root.mutedColor)
                    font.family: root.fontFamily
                    font.pixelSize: 10
                    width: parent.width
                    horizontalAlignment: Text.AlignHCenter
                    elide: Text.ElideRight
                    opacity: text.length ? 1 : 0
                    Behavior on opacity { NumberAnimation { duration: 180 } }
                }
            }
            ActionButton {
                id: loginButton
                objectName: "loginButton"
                width: parent.width
                text: root.busy ? "Signing in…" : "Sign in"
                accent: true
                enabled: !root.busy && account.editText.trim().length > 0 && session.count > 0 && session.currentIndex >= 0
                onClicked: root.attemptLogin()
                KeyNavigation.tab: session
                KeyNavigation.backtab: password
            }
            Item { width: 1; height: 22 }
            Text {
                text: "SESSION"
                color: root.mutedColor
                font.family: root.fontFamily
                font.pixelSize: 9
                font.letterSpacing: 1
            }
            Item { width: 1; height: 7 }
            Choice {
                id: session
                objectName: "session"
                width: parent.width
                model: sessionModel
                textRole: "name"
                currentIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
                enabled: !root.busy
                Accessible.name: "Desktop session"
                KeyNavigation.tab: account
                KeyNavigation.backtab: loginButton
            }
            Item { width: 1; height: 18 }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Enter to sign in"
                color: root.mutedColor
                font.family: root.fontFamily
                font.pixelSize: 10
            }
        }
    }

    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 24
        spacing: 8
        Choice {
            width: 96
            model: keyboard.layouts
            visible: count > 0
            textRole: "shortName"
            currentIndex: keyboard.currentLayout
            enabled: keyboard.enabled && !root.busy
            Accessible.name: "Keyboard layout"
            onActivated: keyboard.currentLayout = currentIndex
        }
        ActionButton {
            iconKind: "sleep"; hint: "Sleep"
            visible: sddm.canSuspend
            enabled: !root.busy
            onClicked: sddm.suspend()
        }
        ActionButton {
            iconKind: "restart"; hint: "Restart"
            visible: sddm.canReboot
            enabled: !root.busy
            onClicked: root.confirmPower("restart")
        }
        ActionButton {
            iconKind: "power"; hint: "Power off"
            visible: sddm.canPowerOff
            enabled: !root.busy
            onClicked: root.confirmPower("poweroff")
        }
    }

    Dialog {
        id: confirmation
        parent: root
        x: (root.width - width) / 2
        y: (root.height - height) / 2
        width: Math.min(400, root.width - 32)
        padding: 24
        modal: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        Overlay.modal: Rectangle { color: "#a6080c14" }
        background: Rectangle {
            color: "#0d1423"; radius: 24
            border.width: 1; border.color: "#39485e"
        }
        contentItem: Column {
            spacing: 20
            Text {
                text: root.powerAction === "restart" ? "Restart the laptop?" : "Power off the laptop?"
                color: root.textColor
                font.family: root.fontFamily
                font.pixelSize: 14
            }
            Row {
                spacing: 12
                ActionButton { id: cancelButton; text: "Go back"; onClicked: confirmation.close() }
                ActionButton {
                    text: root.powerAction === "restart" ? "Restart" : "Power off"
                    accent: true
                    onClicked: {
                        confirmation.close();
                        if (root.powerAction === "restart") sddm.reboot();
                        else sddm.powerOff();
                    }
                }
            }
        }
        enter: Transition {
            ParallelAnimation {
                NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 180 }
                NumberAnimation { property: "scale"; from: 0.97; to: 1; duration: 180; easing.type: Easing.OutCubic }
            }
        }
        exit: Transition { NumberAnimation { property: "opacity"; to: 0; duration: 120 } }
        onClosed: password.forceActiveFocus()
    }

    NumberAnimation { id: entranceAnimation; target: entrance; property: "y"; from: 24; to: 0; duration: 420; easing.type: Easing.OutCubic }
    SequentialAnimation {
        id: shake
        NumberAnimation { target: passwordShake; property: "x"; to: -6; duration: 50 }
        NumberAnimation { target: passwordShake; property: "x"; to: 6; duration: 80 }
        NumberAnimation { target: passwordShake; property: "x"; to: -3; duration: 60 }
        NumberAnimation { target: passwordShake; property: "x"; to: 0; duration: 60 }
    }
    Component.onCompleted: {
        card.opacity = 1;
        entranceAnimation.start();
        if (account.editText.length) password.forceActiveFocus();
        else account.forceActiveFocus();
    }
}
