import QtQuick 2.15
import QtQuick.Controls 2.15

ComboBox {
    id: control
    property string placeholder: ""
    implicitHeight: 42
    implicitWidth: 352
    leftPadding: 18
    rightPadding: 40
    hoverEnabled: true
    font.family: config.stringValue("Font") || "JetBrainsMono Nerd Font"
    font.pixelSize: 12
    palette.text: "#c1d5f0"
    palette.highlight: "#8aade0"
    palette.highlightedText: "#101c30"
    opacity: enabled ? 1 : 0.5
    indicator: Icon {
        x: control.width - width - 14
        y: (control.height - height) / 2
        width: 16
        height: 16
        kind: "down"
        ink: "#8395af"
    }
    contentItem: TextField {
        text: control.editable ? control.editText : control.displayText
        placeholderText: control.placeholder
        placeholderTextColor: "#8395af"
        font: control.font
        color: "#c1d5f0"
        padding: 0
        verticalAlignment: Text.AlignVCenter
        readOnly: !control.editable
        selectByMouse: control.editable
        background: null
        onTextEdited: control.editText = text
    }
    background: Rectangle {
        radius: height / 2
        color: control.hovered ? "#1b2d49" : "#101c30"
        border.width: 1
        border.color: control.activeFocus ? "#8aade0" : "#39485e"
        Behavior on color { ColorAnimation { duration: 150 } }
        Behavior on border.color { ColorAnimation { duration: 150 } }
    }
    delegate: ItemDelegate {
        width: control.width - 12
        height: 38
        highlighted: control.highlightedIndex === index
        contentItem: Text {
            text: control.textAt(index)
            color: highlighted ? "#101c30" : "#c1d5f0"
            font: control.font
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
        background: Rectangle {
            radius: 10
            color: highlighted ? "#8aade0" : "transparent"
        }
    }
    popup: Popup {
        y: control.height + 6
        width: control.width
        padding: 6
        implicitHeight: Math.min(contentItem.implicitHeight + 12, 240)
        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex
            ScrollIndicator.vertical: ScrollIndicator { }
        }
        background: Rectangle {
            radius: 16
            color: "#0d1423"
            border.width: 1
            border.color: "#39485e"
        }
        enter: Transition {
            ParallelAnimation {
                NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 150 }
                NumberAnimation { property: "scale"; from: 0.97; to: 1; duration: 150; easing.type: Easing.OutCubic }
            }
        }
        exit: Transition { NumberAnimation { property: "opacity"; to: 0; duration: 100 } }
    }
}
