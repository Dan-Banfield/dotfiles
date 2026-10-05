import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: control
    property string iconKind: ""
    property bool accent: false
    property string hint: ""
    implicitHeight: 42
    implicitWidth: iconKind.length ? 48 : 130
    hoverEnabled: true
    font.family: config.stringValue("Font") || "JetBrainsMono Nerd Font"
    font.pixelSize: 12
    opacity: enabled ? 1 : 0.4
    Accessible.name: hint.length ? hint : text
    background: Rectangle {
        radius: height / 2
        color: control.accent ? "#8aade0" : (control.hovered ? "#203758" : "#0d1423")
        border.width: 1
        border.color: control.activeFocus ? "#b9d5f4" : "#39485e"
        gradient: control.accent ? blueGradient : null
        Gradient {
            id: blueGradient
            orientation: Gradient.Horizontal
            GradientStop { position: 0; color: "#517fc4" }
            GradientStop { position: 0.6; color: "#8aade0" }
            GradientStop { position: 1; color: "#b9d5f4" }
        }
        Behavior on color { ColorAnimation { duration: 150 } }
        scale: control.down ? 0.97 : 1
        Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }
    }
    contentItem: Item {
        Icon {
            anchors.centerIn: parent
            kind: control.iconKind
            visible: control.iconKind.length > 0
            ink: control.accent ? "#101c30" : "#c1d5f0"
        }
        Text {
            anchors.centerIn: parent
            visible: control.iconKind.length === 0
            text: control.text
            color: control.accent ? "#101c30" : "#c1d5f0"
            font: control.font
        }
    }
    ToolTip {
        parent: control
        visible: control.hovered && control.hint.length > 0
        text: control.hint
        delay: 600
        y: -height - 8
        x: (control.width - width) / 2
        padding: 10
        contentItem: Text {
            text: control.hint
            font: control.font
            color: "#c1d5f0"
        }
        background: Rectangle {
            color: "#0d1423"
            radius: 10
            border.width: 1
            border.color: "#39485e"
        }
    }
}
