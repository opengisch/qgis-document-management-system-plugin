# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Document Management System Plugin
# Copyright (C) 2021 Damiano Lombardi
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

from PyQt5.QtQuickWidgets import QQuickWidget
import os
from qgis.PyQt.QtCore import QUrl, QObject, pyqtSignal, pyqtProperty, pyqtSlot
from qgis.PyQt.QtWidgets import QVBoxLayout, QFileDialog
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsApplication
from qgis.gui import QgsAbstractRelationEditorWidget
from document_management_system_relation_editor.core.document_model import DocumentModel

WidgetUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../ui/document_relation_editor_widget.ui'))

class DocumentRelationEditorWidget(QgsAbstractRelationEditorWidget, WidgetUi):

    def __init__(self, config, parent):
        super().__init__(config, parent)
        self.setupUi(self)

        print('__init__')

        self.document_path = str()

        self.model = DocumentModel()

        layout = QVBoxLayout()
        self.view = QQuickWidget()
        self.view.rootContext().setContextProperty("documentModel", self.model)
        self.view.rootContext().setContextProperty("parentWidget", self)
        self.view.setSource(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../qml/DocumentList.qml')))
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        layout.addWidget(self.view)
        self.setLayout(layout)

    def config(self):
        return {

        }

    def setConfig(self, config):
        self.document_path = config['document_path']

    def updateUi(self):
        print("updateUi")
        self.model.init(self.relation(), self.feature(), self.document_path)

    @pyqtSlot()
    def addDocument(self):

        file_name = QFileDialog.getOpenFileName(self,
                                                self.tr("Add file"))
        if not file_name:
          return

        print("file_name", file_name)

        # WORKAROUND: remove by qgis version > 3.18
        self.updateUi()

    @pyqtSlot()
    def linkDocument(self):
      super(DocumentRelationEditorWidget, self).linkFeature()

    @pyqtSlot(int)
    def unlinkDocument(self, documentId):
        super(DocumentRelationEditorWidget, self).unlinkFeature(documentId)

        # WORKAROUND: remove by qgis version > 3.18
        self.updateUi()

