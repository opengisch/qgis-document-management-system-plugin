import QtQuick 2.10
import QtQuick.Controls 2.5

Item {
    width: 300
    height: 300

    ListView {
        id: listView
        anchors.fill: parent
        visible: documentModel.empty
        focus: true
        model: documentModel
        highlight: Rectangle { color: "lightsteelblue"; radius: 5 }

        header: Rectangle {
            width: parent.width
            height: textHeader.height
            Text {
                id: textHeader
                style: Text.Raised
                text: qsTr("Documents:")
            }
        }

        delegate: Component {
            Item
            {
                width: parent.width
                height: textDocumentName.height

                Button {
                    id: buttonIcon
                    width: parent.height
                    height: parent.height
                    flat: true
                    icon.name: DocumentIcon
                }

                Text {
                    id: textDocumentName

                    anchors.left: buttonIcon.right

                    text: DocumentName

                    ToolTip.visible: mouseArea.containsMouse
                    ToolTip.delay: 1000
                    ToolTip.text: DocumentPath
                }
                MouseArea {
                    id: mouseArea
                    hoverEnabled: true
                    anchors.fill: parent
                    onClicked: listView.currentIndex = index
                    onDoubleClicked: Qt.openUrlExternally(DocumentPath);
                }
            }
        }
    }
}
