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
from qgis.PyQt.QtWidgets import QVBoxLayout, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsApplication, QgsProject, QgsRelation
from qgis.gui import QgsAbstractRelationEditorWidget, QgsAttributeDialog
from document_management_system_relation_editor.core.document_model import DocumentModel

WidgetUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../ui/document_relation_editor_widget.ui'))

class DocumentRelationEditorWidget(QgsAbstractRelationEditorWidget, WidgetUi):

    def __init__(self, config, parent):
        super().__init__(config, parent)
        self.setupUi(self)

        print('DocumentRelationEditorWidget.__init__')

        self.document_path = str()

        self.model = DocumentModel()

        self._nmRelation = QgsRelation()

        layout = QVBoxLayout()
        self.view = QQuickWidget()
        self.view.rootContext().setContextProperty("documentModel", self.model)
        self.view.rootContext().setContextProperty("parentWidget", self)
        self.view.setSource(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../qml/DocumentList.qml')))
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        layout.addWidget(self.view)
        self.setLayout(layout)

    def nmRelation(self):
        return self._nmRelation

    def config(self):
        return {

        }

    def setConfig(self, config):
        self.document_path = config['document_path']

    def updateUi(self):
        print('DocumentRelationEditorWidget.updateUi')
        self.model.init(self.relation(), self.nmRelation(), self.feature(), self.document_path)

    def afterSetRelations(self):
        self._nmRelation = QgsProject.instance().relationManager().relation( self.nmRelationId() )
        
    def checkLayerEditingMode(self):
      
        if self.relation().referencingLayer().isEditable() == False:
            QMessageBox.critical(self,
                                 self.tr("Layer not editable"),
                                 self.tr("Layer '{0}' is not in editing mode.").format(self.relation().referencingLayer().name()))
            return False
        
        if self.nmRelation().isValid():
            if self.nmRelation().referencedLayer().isEditable() == False:
                QMessageBox.critical(self,
                                     self.tr("Layer not editable"),
                                     self.tr("Layer '{0}' is not in editing mode.").format(self.nmRelation().referencedLayer().name()))
                return False
          
        return True
      

    @pyqtSlot()
    def addDocument(self):
        
        if self.checkLayerEditingMode() == False:
          return
        
        self.addFeature()

        # WORKAROUND: remove by qgis version > 3.18
        if self.nmRelation().isValid() == False:
          self.updateUi()

    @pyqtSlot()
    def linkDocument(self):
        
        if self.checkLayerEditingMode() == False:
          return
        
        self.linkFeature()

    @pyqtSlot(int)
    def unlinkDocument(self, documentId):
        
        if self.checkLayerEditingMode() == False:
          return
        
        self.unlinkFeature(documentId)
        
        # WORKAROUND: remove by qgis version > 3.18
        if self.nmRelation().isValid() == False:
          self.updateUi()

    @pyqtSlot(int)
    def showDocumentForm(self, documentId):
        
        if self.checkLayerEditingMode() == False:
          return
        
        layer = self.relation().referencingLayer()
        if self.nmRelation().isValid():
          layer = self.nmRelation().referencedLayer()
          
        showDocumentFormDialog = QgsAttributeDialog(layer,
                                                    layer.getFeature(documentId),
                                                    False,
                                                    self,
                                                    True)
        showDocumentFormDialog.exec()
        self.updateUi()

