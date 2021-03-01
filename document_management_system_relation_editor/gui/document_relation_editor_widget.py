# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Ordered Relation Editor Plugin
# Copyright (C) 2020 Denis Rouzaud
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

from PyQt5.QtQuickWidgets import QQuickWidget
import os
from qgis.PyQt.QtCore import QUrl, QObject, pyqtSignal, pyqtProperty
from qgis.PyQt.QtWidgets import QVBoxLayout
from qgis.PyQt.uic import loadUiType
from qgis.gui import QgsAbstractRelationEditorWidget
from document_management_system_relation_editor.core.document_model import DocumentModel

WidgetUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../ui/document_relation_editor_widget.ui'))


class Foo(QObject):
    modelChanged = pyqtSignal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._model = DocumentModel(parent)

    @pyqtProperty(str, notify=modelChanged)
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        if self._model == value:
            return
        self._model = value
        self.modelChanged.emit()


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
        self.view.setSource(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../qml/DocumentList.qml')))
        layout.addWidget(self.view)
        self.mListView.setLayout(layout)

    def config(self):
        return {

        }

    def setConfig(self, config):
        self.document_path = config['document_path']

    def updateUi(self):
        print('updateUi')
        self.model.init(self.relation(), self.feature(), self.document_path)
