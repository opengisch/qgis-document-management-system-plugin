import QtQuick 2.10
import QtQuick.Controls 2.5
import QtQuick.Dialogs 1.1

Item {

    SystemPalette {
        id: myPalette;
        colorGroup: SystemPalette.Active
    }

    Rectangle {
        id: rectangle_Header
        width: parent.width
        height: button_IconView.height
        z: 1
        color: myPalette.window

        Text {
            id: text_Title
            anchors.left: rectangle_Header.left
            anchors.verticalCenter: parent.verticalCenter
            style: Text.Raised
            text: qsTr("Documents:")
        }

        Button {
            id: button_IconView
            anchors.right: rectangle_Header.right
            anchors.verticalCenter: parent.verticalCenter
            text: qsTr("Icon view")
            icon.name: ":/images/themes/default/mActionIconView.svg"
            checkable: true
            checked: false

            onToggled: button_ListView.checked = !button_IconView.checked
        }
        Button {
            id: button_ListView
            anchors.right: button_IconView.left
            anchors.verticalCenter: parent.verticalCenter
            text: qsTr("List view")
            icon.name: ":/images/themes/default/mIconListView.svg"
            checkable: true
            checked: true

            onToggled: button_IconView.checked = !button_ListView.checked
        }
    }

    Rectangle {
        id: rectangle_Footer
        width: parent.width
        height: button_UnlinkDocument.height
        anchors.bottom: parent.bottom
        z: 1
        color: myPalette.window

        Button {
            id: button_UnlinkDocument
            anchors.right: rectangle_Footer.right
            anchors.verticalCenter: parent.verticalCenter
            action: action_UnlinkDocument
        }
        Button {
            id: button_LinkDocument
            anchors.right: button_UnlinkDocument.left
            anchors.verticalCenter: parent.verticalCenter
            action: action_LinkDocument
        }
        Button {
            id: button_AddDocument
            anchors.right: button_LinkDocument.left
            anchors.verticalCenter: parent.verticalCenter
            action: action_AddDocument
        }
        Button {
            id: button_ShowForm
            anchors.right: button_AddDocument.left
            anchors.verticalCenter: parent.verticalCenter
            action: action_ShowForm
        }
    }

    ListView {
        id: listView
        width: parent.width
        anchors.top: rectangle_Header.bottom
        anchors.bottom: rectangle_Footer.top
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
                    icon.name: DocumentExists == false ? ":/images/composer/missing_image.svg"
                                                       : DocumentIcon == "" ? ":/images/themes/default/mIconFile.svg"
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
                        property string documentType: DocumentType
                        property string documentCreatedTime: DocumentCreatedTime
                        property string documentCreatedUser: DocumentCreatedUser
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
        anchors.bottom: rectangle_Footer.top
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
                        icon.name: DocumentExists == false ? ":/images/composer/missing_image.svg"
                                                           : DocumentIcon == "" ? ":/images/themes/default/mIconFile.svg"
                                                                                : DocumentIcon
                        icon.height: height
                        icon.width: height
                    }
                    Image {
                        width: parent.width
                        height: 60
                        anchors.horizontalCenter: parent.horizontalCenter
                        visible: DocumentIsImage
                        source: DocumentIsImage ? DocumentPath : ""
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
                        property string documentType: DocumentType
                        property string documentCreatedTime: DocumentCreatedTime
                        property string documentCreatedUser: DocumentCreatedUser
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
                                                                        qsTr("Document '%1' does't exists.").arg(DocumentPath));
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
                source: documentIsImage ? documentPath : ""
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
        icon.name: ":/images/themes/default/symbologyAdd.svg"
        onTriggered: {
            parentWidget.addDocument()
        }
    }
    Action {
        id: action_LinkDocument
        text: qsTr("Link document")
        icon.name: ":/images/themes/default/mActionLink.svg"
        onTriggered: {
            parentWidget.linkDocument()
        }
    }
    Action {
        id: action_UnlinkDocument
        text: "Unlink document"
        icon.name: ":/images/themes/default/mActionUnlink.svg"
        onTriggered: {
            var selectedDocumentId = getSelectedDocumentId();
            if (selectedDocumentId < 0)
            {
                showMessageDialog(qsTr("No document selected"),
                                  qsTr("Please select a document to remove."));
                return;
            }
            parentWidget.unlinkDocument(selectedDocumentId);
        }
    }
    Action {
        id: action_ShowForm
        text: "Show form"
        icon.name: ":/images/themes/default/mActionMultiEdit.svg"
        onTriggered:  {
            var selectedDocumentId = getSelectedDocumentId();
            if (selectedDocumentId < 0)
            {
                showMessageDialog(qsTr("No document selected"),
                                  qsTr("Please select a document to remove."));
                return;
            }
            parentWidget.showDocumentForm(selectedDocumentId);
        }
    }

    Menu {
        id: contextMenu
        MenuItem {
            action: action_ShowForm
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
          var fileUrl = drop.urls[0];
          textHeader.text = fileUrl;
          drop.acceptProposedAction();
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

    function getSelectedDocumentPath()
    {
        if (listView.visible)
        {
            if(listView.currentItem)
                return listView.currentItem.documentPath;
        }
        else
        {
            if(gridView.currentItem)
                return gridView.currentItem.documentPath;
        }

        return "";
    }

    function getSelectedDocumentId()
    {
        if (listView.visible)
        {
            if(listView.currentItem)
                return listView.currentItem.documentId;
        }
        else
        {
            if(gridView.currentItem)
                return gridView.currentItem.documentId;
        }

        return -1;
    }
}


