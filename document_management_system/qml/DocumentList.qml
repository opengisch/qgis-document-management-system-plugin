import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.1
import QtQuick.Layouts 1.15

Item {

    property int selectedDocumentId: listView.visible
                                     ? (listView.currentItem
                                        ? listView.currentItem.documentId
                                        : -1 )
                                     : (gridView.currentItem
                                        ? gridView.currentItem.documentId
                                        : -1)

    SystemPalette {
        id: myPalette;
        colorGroup: SystemPalette.Active
    }

    Component.onCompleted: {
        console.log("Completed: " + parentWidget.defaultViewList)
        button_IconView.checked = !parentWidget.defaultViewList
        button_ListView.checked = parentWidget.defaultViewList
    }

    Rectangle {
        id: rectangle_Header
        width: parent.width
        height: button_IconView.height
        z: 1
        color: myPalette.window

        RowLayout
        {
            anchors.fill: parent

            // Buttons links
            ButtonToolTip {
                id: button_ShowForm
                display: AbstractButton.IconOnly
                action: action_ShowForm
                tooltip: action_ShowForm.text
            }
            ButtonToolTip {
                id: button_AddDocument
                display: AbstractButton.IconOnly
                action: action_AddDocument
                tooltip: action_AddDocument.text
            }
            ButtonToolTip {
                id: button_DropDocument
                display: AbstractButton.IconOnly
                action: action_DropDocument
                tooltip: action_DropDocument.text
            }
            ButtonToolTip {
                id: button_LinkDocument
                display: AbstractButton.IconOnly
                action: action_LinkDocument
                tooltip: action_LinkDocument.text
            }
            ButtonToolTip {
                id: button_UnlinkDocument
                display: AbstractButton.IconOnly
                action: action_UnlinkDocument
                tooltip: action_UnlinkDocument.text
            }

            // Spacer item
            Item { Layout.fillWidth: true }

            // Buttons right
            ButtonToolTip {
                id: button_ListView
                tooltip: qsTr("List view")
                icon.source: "qrc:///images/themes/default/mIconListView.svg"
                checkable: true

                onToggled: {
                    button_IconView.checked = !button_ListView.checked
                    parentWidget.defaultViewList = button_ListView.checked
                }
            }
            ButtonToolTip {
                id: button_IconView
                tooltip: qsTr("Icon view")
                icon.source: "qrc:///images/themes/default/mActionIconView.svg"
                checkable: true

                onToggled: {
                    button_ListView.checked = !button_IconView.checked
                    parentWidget.defaultViewList = button_ListView.checked
                }
            }
        } // RowLayout
    } // rectangle_Header

    ListView {
        id: listView
        width: parent.width
        anchors.top: rectangle_Header.bottom
        anchors.bottom: parent.bottom
        z: 0
        visible: button_ListView.checked
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
                height: textDocumentName.height

                property int documentId: DocumentId
                property string documentPath: DocumentPath

                Button {
                    id: buttonIcon
                    width: parent.height
                    height: parent.height
                    flat: true
                    icon.name: DocumentExists == false ? "qrc:///images/composer/missing_image.svg"
                                                       : DocumentIcon == "" ? "qrc:///images/themes/default/mIconFile.svg"
                                                                            : DocumentIcon
                }

                Text {
                    id: textDocumentName
                    anchors.left: buttonIcon.right
                    text: DocumentName
                }

                ToolTip {
                    id: toolTip
                    visible: mouseArea.containsMouse
                    delay: 1000

                    contentItem: Loader {
                        sourceComponent: component_ToolTip;

                        property string documentPath: DocumentPath
                        property string documentURL: DocumentURL
                        property string documentType: DocumentType
                        property string documentCreatedTime: DocumentCreatedTime
                        property string documentCreatedUser: DocumentCreatedUser
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
        anchors.top: rectangle_Header.bottom
        anchors.bottom: parent.bottom
        z: 0
        visible: !button_ListView.checked
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

                    Button {
                        width: parent.width
                        height: 60
                        anchors.horizontalCenter: parent.horizontalCenter
                        visible: !DocumentIsImage
                        flat: true
                        icon.name: DocumentExists == false ? "qrc:///images/composer/missing_image.svg"
                                                           : DocumentIcon == "" ? "qrc:///images/themes/default/mIconFile.svg"
                                                                                : DocumentIcon
                        icon.height: height
                        icon.width: height
                    }
                    Image {
                        width: parent.width
                        height: 60
                        anchors.horizontalCenter: parent.horizontalCenter
                        visible: DocumentIsImage
                        source: DocumentExists == false ? "qrc:///images/composer/missing_image.svg"
                                                        : DocumentIsImage ? DocumentURL
                                                                          : ""
                        fillMode: Image.PreserveAspectFit
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
                        property string documentURL: DocumentURL
                        property string documentType: DocumentType
                        property string documentCreatedTime: DocumentCreatedTime
                        property string documentCreatedUser: DocumentCreatedUser
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

    Component {
        id: component_ToolTip

        Row {
            spacing: 5

            Image {
                height: grid_Names.height
                visible: documentIsImage
                source: documentExists == false ? "qrc:///images/composer/missing_image.svg"
                                                : documentIsImage ? documentURL
                                                                  : ""
                fillMode: Image.PreserveAspectFit
            }

            Grid {
                id: grid_Names
                columns: 2
                spacing: 5

                // Row 1
                Text {
                    text: qsTr("Path:")
                }
                Text {
                    font.italic: !documentPath
                    text: documentPath ? documentPath : "<Unknown>"
                }
                // Row 2
                Text {
                    text: qsTr("Type:")
                }
                Text {
                    font.italic: !documentType
                    text: documentType ? documentType : "<Unknown>"
                }
                // Row 3
                Text {
                    text: qsTr("Created on:")
                }
                Text {
                    font.italic: !documentCreatedTime
                    text: documentCreatedTime ? documentCreatedTime : "<Unknown>"
                }
                // Row 4
                Text {
                    text: qsTr("Created by:")
                }
                Text {
                    font.italic: !documentCreatedUser
                    text: documentCreatedUser ? documentCreatedUser : "<Unknown>"
                }
            }
        }
    } // component_ToolTip

    Action {
        id: action_AddDocument
        text: qsTr("Add document")
        icon.source: "qrc:///images/themes/default/symbologyAdd.svg"
        onTriggered: {
            parentWidget.addDocument()
        }
    }
    Action {
        id: action_DropDocument
        text: qsTr("Drop document")
        icon.source: "qrc:///images/themes/default/mActionDeleteSelected.svg"
        enabled: selectedDocumentId >= 0
        onTriggered: {
            parentWidget.unlinkDocument(selectedDocumentId);
        }
    }
    Action {
        id: action_LinkDocument
        text: qsTr("Link document")
        icon.source: "qrc:///images/themes/default/mActionLink.svg"
        onTriggered: {
            parentWidget.linkDocument()
        }
    }
    Action {
        id: action_UnlinkDocument
        text: "Unlink document"
        icon.source: "qrc:///images/themes/default/mActionUnlink.svg"
        enabled: selectedDocumentId >= 0
        onTriggered: {
            parentWidget.unlinkDocument(selectedDocumentId);
        }
    }
    Action {
        id: action_ShowForm
        text: "Show form"
        icon.source: "qrc:///images/themes/default/mActionMultiEdit.svg"
        enabled: selectedDocumentId >= 0
        onTriggered:  {
            parentWidget.showDocumentForm(selectedDocumentId);
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
}


