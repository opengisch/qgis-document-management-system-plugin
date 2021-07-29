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
        console.log("Completed: " + parentWidget.currentView)
        button_IconView.checked = parentWidget.currentView === parentWidget.ICON_VIEW
        button_ListView.checked = !button_IconView.checked
    }

    Rectangle {
        id: rectangle_Header
        width: parent.width
        height: button_IconView.height + 6
        z: 1
        color: myPalette.window

        RowLayout
        {
            anchors.fill: parent

            // Buttons links
            ButtonToolTip {
                Layout.preferredWidth: height
                display: AbstractButton.IconOnly
                action: action_ShowForm
                tooltip: action_ShowForm.text
            }
            ButtonToolTip {
                Layout.preferredWidth: height
                display: AbstractButton.IconOnly
                action: action_AddDocument
                tooltip: action_AddDocument.text
            }
            ButtonToolTip {
                Layout.preferredWidth: height
                display: AbstractButton.IconOnly
                action: action_DropDocument
                tooltip: action_DropDocument.text
            }
            ButtonToolTip {
                Layout.preferredWidth: height
                display: AbstractButton.IconOnly
                action: action_LinkDocument
                tooltip: action_LinkDocument.text
            }
            ButtonToolTip {
                Layout.preferredWidth: height
                display: AbstractButton.IconOnly
                action: action_UnlinkDocument
                tooltip: action_UnlinkDocument.text
            }

            // Spacer item
            Item { Layout.fillWidth: true }

            // Buttons right
            ButtonToolTip {
                id: button_ListView
                Layout.preferredWidth: height
                tooltip: qsTr("List view")
                icon.source: "qrc:///images/themes/default/mIconListView.svg"
                checkable: true

                onToggled: {
                    button_IconView.checked = !button_ListView.checked
                    if(button_IconView.checked)
                        parentWidget.currentView = parentWidget.ICON_VIEW
                    else
                        parentWidget.currentView = parentWidget.LIST_VIEW
                }
            }
            ButtonToolTip {
                id: button_IconView
                Layout.preferredWidth: height
                tooltip: qsTr("Icon view")
                icon.source: "qrc:///images/themes/default/mActionIconView.svg"
                checkable: true

                onToggled: {
                    button_ListView.checked = !button_IconView.checked
                    if(button_IconView.checked)
                        parentWidget.currentView = parentWidget.ICON_VIEW
                    else
                        parentWidget.currentView = parentWidget.LIST_VIEW
                }
            }
        } // RowLayout
    } // rectangle_Header

    Rectangle {
        id: rectangle_Content
        width: parent.width
        anchors.top: rectangle_Header.bottom
        anchors.bottom: parent.bottom

        ListView {
            id: listView
            width: parent.width
            anchors.fill: parent
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
                    height: 22

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
                            property string documentURL: DocumentURL
                            property string documentType: DocumentType
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
                            visible: !DocumentIsImage && DocumentIcon != ""
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
                            visible: DocumentIsImage || DocumentIcon == ""
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
                visible: documentIsImage
                source: documentExists == false ? "qrc:///images/composer/missing_image.svg"
                                                : documentIsImage ? documentURL
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


