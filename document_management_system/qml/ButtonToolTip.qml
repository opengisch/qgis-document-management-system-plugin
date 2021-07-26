import QtQuick 2.15
import QtQuick.Controls 2.15

Button {

    default property alias tooltip: toolTip.text

    ToolTip {
        id: toolTip
        visible: hovered
        delay: 1000
    }
}
