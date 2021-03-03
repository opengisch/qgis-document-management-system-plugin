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
                }

                ToolTip {
                    id: toolTip
                    visible: mouseArea.containsMouse
                    delay: 1000

                    contentItem: Row{

                        spacing: 5

                        Column {
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
                }
            }
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
