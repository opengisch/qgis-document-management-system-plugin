import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.1
import QtQuick.Layouts 1.15

Item {

    property int selectedDocumentId: listView.visible
                                     ? (listView.currentItem
                                        ? listView.currentItem.documentId
                                        : -1)
                                     : (gridView.currentItem
                                        ? gridView.currentItem.documentId
                                        : -1)
                                     
    onSelectedDocumentIdChanged: {
        if(selectedDocumentId >= 0)
        {
          parentWidget.setCurrentDocumentId(selectedDocumentId)
        }
        else
        {
          parentWidget.setCurrentDocumentId(null)
        }
    }

    SystemPalette {
        id: myPalette;
        colorGroup: SystemPalette.Active
    }

    Component.onCompleted: updateCurrentView()

    Connections{
        target: parentWidget
        function onSignalCurrentViewChanged()
        {
            updateCurrentView()
        }
    }

    Rectangle {
        id: rectangle_Content
        anchors.fill: parent

        ListView {
            id: listView
            width: parent.width
            anchors.fill: parent
            focus: true
            model: documentModel
            highlight: Rectangle { color: "lightsteelblue"; radius: 5 }
            ScrollBar.vertical: ScrollBar {
                active: true
            }

            delegate: Component {
                Item
                {
                    width: listView.width
                    height: 22

                    property int documentId: DocumentId
                    property string documentPath: DocumentPath

                    Image {
                        id: imageFileTypeIcon
                        width: parent.height
                        height: parent.height
                        fillMode: Image.PreserveAspectFit
                        source: "image://fileTypeSmallIconProvider/" + DocumentPath
                    }

                    Text {
                        id: textDocumentName
                        anchors.left: imageFileTypeIcon.right
                        height: parent.height
                        text: DocumentName
                        verticalAlignment: Text.AlignVCenter
                    }

                    ToolTip {
                        id: toolTip
                        visible: mouseArea.containsMouse
                        delay: 1000

                        contentItem: Loader {
                            sourceComponent: component_ToolTip;

                            property string documentPath: DocumentPath
                            property string documentToolTip: DocumentToolTip
                            property bool documentExists: DocumentExists
                            property bool documentIsImage: DocumentIsImage
                        }
                    }

                    MouseArea {
                        id: mouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        acceptedButtons: Qt.LeftButton | Qt.RightButton
                        onClicked: {
                            listView.currentIndex = index

                            if(mouse.button == Qt.RightButton)
                                contextMenu.popup()

                        }
                        onDoubleClicked: DocumentExists ? Qt.openUrlExternally(DocumentPath)
                                                        : showMessageDialog(qsTr("Inexisting document"),
                                                                            qsTr("Document '%1' does't exists.").arg(DocumentPath));
                    }
                }
            }
        } // ListView

        GridView {
            id: gridView
            width: parent.width
            anchors.fill: parent
            focus: true
            model: documentModel
            cellWidth: 100
            cellHeight: 140
            highlight: Rectangle { color: "lightsteelblue"; radius: 5 }
            ScrollBar.vertical: ScrollBar {
                active: true
            }

            delegate: Component {
                Item
                {
                    id: item_Delegate
                    width: gridView.cellWidth
                    height: gridView.cellHeight

                    property int documentId: DocumentId
                    property string documentPath: DocumentPath

                    Column {
                        anchors.fill: parent

                        Image {
                            width: parent.width
                            height: 60
                            anchors.horizontalCenter: parent.horizontalCenter
                            fillMode: Image.PreserveAspectFit
                            source: DocumentIsImage ? (DocumentExists ? "image://previewImageProvider/" + documentPath
                                                                      : "qrc:///images/composer/missing_image.svg")
                                                    : "image://fileTypeBigIconProvider/" + documentPath
                        }
                        Text {
                            id: textDocumentName
                            width: parent.width
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: DocumentName
                            horizontalAlignment: Text.AlignHCenter
                            wrapMode: Text.Wrap
                        }
                    }

                    ToolTip {
                        id: toolTip
                        visible: mouseArea.containsMouse
                        delay: 1000

                        contentItem: Loader {
                            sourceComponent: component_ToolTip;

                            property string documentPath: DocumentPath
                            property string documentToolTip: DocumentToolTip
                            property bool documentExists: DocumentExists
                            property bool documentIsImage: DocumentIsImage
                        }
                    }

                    MouseArea {
                        id: mouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        acceptedButtons: Qt.LeftButton | Qt.RightButton
                        onClicked: {
                            gridView.currentIndex = index

                            if(mouse.button == Qt.RightButton)
                                contextMenu.popup()
                        }
                        onDoubleClicked: DocumentExists ? Qt.openUrlExternally(DocumentPath)
                                                        : showMessageDialog(qsTr("Inexisting document"),
                                                                            qsTr("Document '%1' does't exists.").arg(DocumentPath))
                    }
                }
            }
        } // GridView
    } // rectangle_Content

    Component {
        id: component_ToolTip

        RowLayout
        {
            anchors.fill: parent
            spacing: 5

            Image {
                width: 100
                Layout.maximumWidth: 100
                Layout.maximumHeight: 100
                visible: documentIsImage
                source: documentExists ? (documentIsImage ? "image://previewImageProvider/" + documentPath
                                                          : "")
                                       : ""
                fillMode: Image.PreserveAspectFit
            }

            Text {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                textFormat: Text.RichText
                text: documentToolTip
            }
        }
    } // component_ToolTip

    Action {
        id: action_DropDocument
        text: qsTr("Drop document")
        icon.source: "qrc:///images/themes/default/mActionDeleteSelected.svg"
        enabled: selectedDocumentId >= 0
        onTriggered: {
            parentWidget.unlinkDocument();
        }
    }
    Action {
        id: action_UnlinkDocument
        text: "Unlink document"
        icon.source: "qrc:///images/themes/default/mActionUnlink.svg"
        enabled: selectedDocumentId >= 0
        onTriggered: {
            parentWidget.unlinkDocument();
        }
    }
    Action {
        id: action_ShowForm
        text: "Show form"
        icon.source: "qrc:///images/themes/default/mActionMultiEdit.svg"
        enabled: selectedDocumentId >= 0
        onTriggered:  {
            parentWidget.showDocumentForm();
        }
    }

    Menu {
        id: contextMenu
        MenuItem {
            action: action_ShowForm
        }
        MenuItem {
            action: action_DropDocument
        }
        MenuItem {
            action: action_UnlinkDocument
        }
    }

    DropArea {
      anchors.fill: parent
      keys: ["text/uri-list"]

      onDropped:
      {
        if (drop.hasUrls)
        {
          drop.acceptProposedAction();
          parentWidget.addDroppedDocument(drop.urls[0])
        }
      }
    } // DropArea

    MessageDialog {
        id: messageDialog
    }

    function showMessageDialog(title, text)
    {
        messageDialog.title = title;
        messageDialog.text = text;
        messageDialog.open();
    }

    function updateCurrentView()
    {
        gridView.visible = parentWidget.currentView === CONST_ICON_VIEW
        listView.visible = !gridView.visible
    }
}


