import QtQuick 2.10
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.1

Item {

    Rectangle {
        id: rectangle_Header
        width: parent.width
        height: 40
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
            text: qsTr("Icon view")
            anchors.right: rectangle_Header.right
            anchors.verticalCenter: parent.verticalCenter
        }

        Button {
            id: button_ListView
            anchors.right: button_IconView.left
            anchors.verticalCenter: parent.verticalCenter
            text: qsTr("List view")
        }
    }


    Rectangle {
        id: rectangle_Footer
        width: parent.width
        height: 40
        anchors.bottom: parent.bottom
        color: "lightgray"
        border.color: "cyan"

        Button {
            id: button_RemoveDocument
            text: qsTr("Remove document")
            anchors.right: rectangle_Footer.right
            anchors.verticalCenter: parent.verticalCenter
        }

        Button {
            id: button_AddDocument
            text: qsTr("Add document")
            anchors.right: button_RemoveDocument.left
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    ListView {
        id: listView
        width: parent.width
        anchors.top: rectangle_Header.bottom
        anchors.bottom: rectangle_Footer.top

        focus: true
        model: documentModel
        highlight: Rectangle { color: "lightsteelblue"; radius: 5 }

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
                }

                ToolTip {
                    id: toolTip
                    visible: mouseArea.containsMouse
                    delay: 1000

                    contentItem: Row{
                        spacing: 5

                        Image {
                            height: column_Names.height
                            visible: true
                            source: DocumentPath
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


    Menu {
        id: contextMenu
        MenuItem {
            text: "Show form"
            onTriggered: showForm()
        }
        MenuItem {
            text: "Remove link"
            onTriggered: removeLink()
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


