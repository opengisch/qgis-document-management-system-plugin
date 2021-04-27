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
from qgis.PyQt.QtCore import QUrl, QObject, QFileInfo, pyqtSignal, pyqtProperty, pyqtSlot
from qgis.PyQt.QtWidgets import QVBoxLayout, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsApplication, QgsProject, QgsRelation, QgsPolymorphicRelation, QgsExpression, QgsExpressionContext, QgsExpressionContextUtils, QgsFields, QgsVectorLayerTools, QgsVectorLayerUtils, QgsGeometry, QgsFeature
from qgis.gui import QgsAbstractRelationEditorWidget, QgsAttributeDialog
from document_management_system_relation_editor.core.document_model import DocumentModel

WidgetUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../ui/document_relation_editor_widget.ui'))


class DocumentRelationEditorWidget(QgsAbstractRelationEditorWidget, WidgetUi):

    def __init__(self, config, parent):
        super().__init__(config, parent)
        self.setupUi(self)

        print('DocumentRelationEditorWidget.__init__')

        self.documents_path = str()
        self.document_filename = str()
        self.document_author = str()

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
        self.documents_path = config['documents_path']
        self.document_filename = config['document_filename']
        self.document_author = config['document_author']

    def updateUi(self):
        print('DocumentRelationEditorWidget.updateUi')
        self.model.init(self.relation(),
                        self.nmRelation(),
                        self.feature(),
                        self.documents_path,
                        self.document_filename,
                        self.document_author)

    def afterSetRelations(self):
        self._nmRelation = QgsProject.instance().relationManager().relation(self.nmRelationId())

    def checkLayerEditingMode(self):

        if self.relation().referencingLayer().isEditable() is False:
            QMessageBox.critical(self,
                                 self.tr("Layer not editable"),
                                 self.tr("Layer '{0}' is not in editing mode.").format(self.relation().referencingLayer().name()))
            return False

        if self.nmRelation().isValid():
            if self.nmRelation().referencedLayer().isEditable() is False:
                QMessageBox.critical(self,
                                     self.tr("Layer not editable"),
                                     self.tr("Layer '{0}' is not in editing mode.").format(self.nmRelation().referencedLayer().name()))
                return False

        return True

    @pyqtSlot()
    def addDocument(self):

        if self.checkLayerEditingMode() is False:
            return

        self.addFeature()

    @pyqtSlot(str)
    def addDroppedDocument(self, fileUrl):

        if self.checkLayerEditingMode() is False:
            return

        layer = self.relation().referencingLayer()
        if self.nmRelation().isValid():
            layer = self.nmRelation().referencedLayer()

        default_documents_path = str()
        if self.documents_path:
            exp = QgsExpression(self.documents_path)
            context = QgsExpressionContext()
            context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
            default_documents_path = exp.evaluate(context)

        fileinfo = QFileInfo(QUrl(fileUrl).toLocalFile())
        print("Filename: {0}, default location {1}".format(fileinfo.filePath(),
                                                           default_documents_path))

        keyAttrs = dict()

        # Fields of the linking table
        fields = self.relation().referencingLayer().fields()

        # For generated relations insert the referenced layer field
        if self.relation().type() is QgsRelation.Generated:
            polyRel = self.relation().polymorphicRelation()
            keyAttrs.insert(fields.indexFromName(polyRel.referencedLayerField()),
                            polyRel.layerRepresentation(self.relation().referencedLayer()))

        if self.nmRelation().isValid():
            # only normal relations support m:n relation
            if self.nmRelation().type() != QgsRelation.Normal:
                QMessageBox.critical(self,
                                     self.tr("Add document"),
                                     self.tr("Invalid relation, Only normal relations support m:n relation."))
                return

            # n:m Relation: first let the user create a new feature on the other table
            # and autocreate a new linking feature.
            ok, feature = self.editorContext().vectorLayerTools().addFeature(self.nmRelation().referencedLayer(),
                                                                             dict(),
                                                                             QgsGeometry())
            if not ok:
                QMessageBox.critical(self,
                                     self.tr("Add document"),
                                     self.tr("Could not add a new feature."))
                return

            linkAttributes = keyAttrs.copy()
            for key in self.relation().fieldPairs():
                linkAttributes[fields.indexOf(key)] = self.feature().attribute(self.relation().fieldPairs()[key])

            for key in self.nmRelation().fieldPairs():
                linkAttributes[fields.indexOf(key)] = feature.attribute(self.nmRelation().fieldPairs()[key])

            linkFeature = QgsVectorLayerUtils.createFeature(self.relation().referencingLayer(),
                                                            QgsGeometry(),
                                                            linkAttributes,
                                                            self.relation().referencingLayer().createExpressionContext())

            if not self.relation().referencingLayer().addFeature(linkFeature):
                QMessageBox.critical(self,
                                     self.tr("Add document"),
                                     self.tr("Could not add a new linking feature."))
                return

        else:
            for key in self.relation().fieldPairs():
                keyAttrs[fields.indexFromName(key)] = self.feature().attribute(self.relation().fieldPairs()[key])

            ok, feature = self.editorContext().vectorLayerTools().addFeature(self.relation().referencingLayer(),
                                                                             keyAttrs,
                                                                             QgsGeometry())
            if not ok:
                QMessageBox.critical(self,
                                     self.tr("Add document"),
                                     self.tr("Could not add a new feature."))
                return

        self.updateUi()

    @pyqtSlot()
    def linkDocument(self):

        if self.checkLayerEditingMode() is False:
            return

        self.linkFeature()

    @pyqtSlot(int)
    def unlinkDocument(self, documentId):

        if self.checkLayerEditingMode() is False:
            return

        self.unlinkFeature(documentId)

    @pyqtSlot(int)
    def showDocumentForm(self, documentId):

        if self.checkLayerEditingMode() is False:
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
