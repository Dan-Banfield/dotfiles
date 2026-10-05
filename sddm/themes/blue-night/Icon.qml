import QtQuick 2.15

Canvas {
    id: icon
    property string kind: "lock"
    property color ink: "#c1d5f0"
    implicitWidth: 20
    implicitHeight: 20
    onKindChanged: requestPaint()
    onInkChanged: requestPaint()
    onPaint: {
        var ctx = getContext("2d");
        ctx.reset();
        ctx.scale(width / 24, height / 24);
        ctx.strokeStyle = ink;
        ctx.lineWidth = 1.8;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.beginPath();
        if (kind === "lock") {
            ctx.rect(5, 10, 14, 11);
            ctx.moveTo(8, 10); ctx.lineTo(8, 7);
            ctx.arc(12, 7, 4, Math.PI, 0);
            ctx.lineTo(16, 10);
            ctx.moveTo(12, 14); ctx.lineTo(12, 17);
        } else if (kind === "arrow") {
            ctx.moveTo(5, 12); ctx.lineTo(19, 12);
            ctx.moveTo(13, 6); ctx.lineTo(19, 12); ctx.lineTo(13, 18);
        } else if (kind === "down") {
            ctx.moveTo(6, 9); ctx.lineTo(12, 15); ctx.lineTo(18, 9);
        } else if (kind === "power") {
            ctx.moveTo(12, 3); ctx.lineTo(12, 11);
            ctx.moveTo(17.7, 6.3);
            ctx.arc(12, 12, 8, -Math.PI / 4, 5 * Math.PI / 4);
        } else if (kind === "restart") {
            // Clockwise curve ending at the arrowhead in the upper right.
            ctx.moveTo(18.9, 16);
            ctx.arc(12, 12, 8, Math.PI / 6, 11 * Math.PI / 6);
            ctx.moveTo(18.9, 2); ctx.lineTo(18.9, 8); ctx.lineTo(12.9, 8);
        } else if (kind === "sleep") {
            ctx.moveTo(18, 17);
            ctx.bezierCurveTo(5, 21, 1, 8, 10, 4);
            ctx.bezierCurveTo(6, 12, 11, 18, 18, 17);
        }
        ctx.stroke();
    }
}
