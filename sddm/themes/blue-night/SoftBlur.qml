import QtQuick 2.15

// Two static, downsampled Gaussian passes; no extra QML effects package.
Item {
    id: blur
    property Item sourceItem
    ShaderEffectSource {
        id: original
        sourceItem: blur.sourceItem
        hideSource: true
        live: false
        visible: false
        textureSize: Qt.size(Math.max(1, blur.width / 3), Math.max(1, blur.height / 3))
    }
    ShaderEffect {
        id: horizontal
        anchors.fill: parent
        property variant source: original
        property vector2d direction: Qt.vector2d(3 / original.textureSize.width, 0)
        fragmentShader: "varying highp vec2 qt_TexCoord0;\n"
            + "uniform sampler2D source; uniform highp vec2 direction; uniform lowp float qt_Opacity;\n"
            + "void main() {\n"
            + "lowp vec4 c = texture2D(source, qt_TexCoord0) * 0.227027;\n"
            + "c += (texture2D(source, qt_TexCoord0 + direction) + texture2D(source, qt_TexCoord0 - direction)) * 0.1945946;\n"
            + "c += (texture2D(source, qt_TexCoord0 + direction * 2.0) + texture2D(source, qt_TexCoord0 - direction * 2.0)) * 0.1216216;\n"
            + "c += (texture2D(source, qt_TexCoord0 + direction * 3.0) + texture2D(source, qt_TexCoord0 - direction * 3.0)) * 0.054054;\n"
            + "c += (texture2D(source, qt_TexCoord0 + direction * 4.0) + texture2D(source, qt_TexCoord0 - direction * 4.0)) * 0.016216;\n"
            + "gl_FragColor = c * qt_Opacity; }"
    }
    ShaderEffectSource {
        id: intermediate
        sourceItem: horizontal
        hideSource: true
        live: false
        visible: false
        textureSize: original.textureSize
    }
    ShaderEffect {
        anchors.fill: parent
        property variant source: intermediate
        property vector2d direction: Qt.vector2d(0, 3 / intermediate.textureSize.height)
        fragmentShader: horizontal.fragmentShader
    }
}
