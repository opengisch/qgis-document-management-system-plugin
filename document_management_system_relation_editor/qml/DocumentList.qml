import QtQuick 2.10
import QtQuick.Controls 2.5

Item {

    Rectangle {
        id: rectangle_Header
        width: parent.width
        height: 40
        z: 1
        color: "lightgray"
        border.color: "purple"

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
            checkable: true
            checked: false

            onToggled: button_ListView.checked = !button_IconView.checked
        }
        Button {
            id: button_ListView
            anchors.right: button_IconView.left
            anchors.verticalCenter: parent.verticalCenter
            text: qsTr("List view")
            checkable: true
            checked: true

            onToggled: button_IconView.checked = !button_ListView.checked
        }
    }


    Rectangle {
        id: rectangle_Footer
        width: parent.width
        height: 40
        anchors.bottom: parent.bottom
        z: 1
        color: "lightgray"
        border.color: "cyan"

        Button {
            id: button_RemoveDocument
            anchors.right: rectangle_Footer.right
            anchors.verticalCenter: parent.verticalCenter
            action: action_RemoveDocument
        }
        Button {
            id: button_AddDocument
            anchors.right: button_RemoveDocument.left
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

        delegate: Component {
            Item
            {
                width: listView.width
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
                    text: DocumentName + DocumentIsImage
                }

                ToolTip {
                    id: toolTip
                    visible: mouseArea.containsMouse
                    delay: 1000

                    contentItem: Row{
                        spacing: 5

                        Image {
                            height: column_Names.height
                            visible: DocumentIsImage
                            source: DocumentIsImage ? DocumentPath : ""
                            fillMode: Image.PreserveAspectFit
                        }

                        Column {
                            id: column_Names
                            Text {
                                color: "white"
                                text: qsTr("Path:")
                            }
                            Text {
                                color: "white"
                                text: qsTr("Type:")
                            }
                            Text {
                                color: "white"
                                text: qsTr("Created on:")
                            }
                            Text {
                                color: "white"
                                text: qsTr("Created by:")
                            }
                        }

                        Column {
                            Text {
                                color: "white"
                                font.italic: !DocumentPath
                                text: DocumentPath ? DocumentPath : "<Unknown>"
                            }
                            Text {
                                color: "white"
                                font.italic: !DocumentType
                                text: DocumentType ? DocumentType : "<Unknown>"
                            }
                            Text {
                                color: "white"
                                font.italic: !DocumentCreatedTime
                                text: DocumentCreatedTime ? DocumentCreatedTime : "<Unknown>"
                            }
                            Text {
                                color: "white"
                                font.italic: !DocumentCreatedUser
                                text: DocumentCreatedUser ? DocumentCreatedUser : "<Unknown>"
                            }
                        }
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
                    onDoubleClicked: Qt.openUrlExternally(DocumentPath);
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

        delegate: Component {
            Item
            {
                id: item_Delegate
                width: gridView.cellWidth
                height: gridView.cellHeight

                Column {
                    anchors.fill: parent


                    Button {
                        width: parent.width
                        height: 60
                        anchors.horizontalCenter: parent.horizontalCenter
                        visible: !DocumentIsImage
                        flat: true
                        icon.name: DocumentIcon
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

                    contentItem: Row{
                        spacing: 5

                        Image {
                            height: column_Names.height
                            visible: DocumentIsImage
                            source: DocumentIsImage ? DocumentPath : ""
                            fillMode: Image.PreserveAspectFit
                        }

                        Column {
                            id: column_Names
                            Text {
                                color: "white"
                                text: qsTr("Path:")
                            }
                            Text {
                                color: "white"
                                text: qsTr("Type:")
                            }
                            Text {
                                color: "white"
                                text: qsTr("Created on:")
                            }
                            Text {
                                color: "white"
                                text: qsTr("Created by:")
                            }
                        }

                        Column {
                            Text {
                                color: "white"
                                font.italic: !DocumentPath
                                text: DocumentPath ? DocumentPath : "<Unknown>"
                            }
                            Text {
                                color: "white"
                                font.italic: !DocumentType
                                text: DocumentType ? DocumentType : "<Unknown>"
                            }
                            Text {
                                color: "white"
                                font.italic: !DocumentCreatedTime
                                text: DocumentCreatedTime ? DocumentCreatedTime : "<Unknown>"
                            }
                            Text {
                                color: "white"
                                font.italic: !DocumentCreatedUser
                                text: DocumentCreatedUser ? DocumentCreatedUser : "<Unknown>"
                            }
                        }
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
                    onDoubleClicked: Qt.openUrlExternally(DocumentPath);
                }
            }
        }
    } // GridView

    Action {
        id: action_AddDocument
        text: qsTr("Add document")
//        icon.name: qgsApplicationInstance.activeThemePath + "/symbologyAdd.svg"
//        icon.name: qgsApplicationInstance.defaultThemePath + "/symbologyAdd.svg"
        // icon.name: themePath + "/symbologyAdd.svg"
        //        icon.name: ":/images/themes/default/symbologyAdd.svg"
        icon.name: parent.getPath("/symbologyAdd.svg")
        onTriggered: addDocument()
    }
    Action {
        id: action_RemoveDocument
        text: "Remove document"
        icon.name: ":/images/themes/default/symbologyRemove.svg"
        onTriggered: removeDocument()
    }
    Action {
        id: action_ShowForm
        text: "Show form"
        icon.name: ":/images/themes/default/mActionMultiEdit.svg"
        onTriggered: showForm()
    }

    Menu {
        id: contextMenu
        MenuItem {
            action: action_ShowForm
        }
        MenuItem {
            action: action_RemoveDocument
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
}


