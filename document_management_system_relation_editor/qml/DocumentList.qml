import QtQuick 2.10
import QtQuick.Controls 2.5

Item {
   id: top
    width: 200
    height: 300

    ListView {
        id: listView
        anchors.fill: parent

        model: documentModel

        delegate: Text {
            text: "Animal: " +  DocumentPath
        }
    }
}
