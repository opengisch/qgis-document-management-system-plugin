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
from enum import Enum
from qgis.PyQt.QtCore import (
    QUrl,
    QObject,
    QDir,
    QSysInfo,
    pyqtSignal,
    pyqtProperty,
    pyqtSlot
)
from qgis.PyQt.QtWidgets import (
    QMessageBox,
    QVBoxLayout
)
from qgis.PyQt.uic import loadUiType
from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsRelation,
    QgsPolymorphicRelation,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils,
    QgsFields,
    QgsVectorLayerTools,
    QgsVectorLayerUtils,
    QgsGeometry,
    QgsFeature,
    QgsSettingsEntryString
)
from qgis.gui import (
    QgsAbstractRelationEditorWidget,
    QgsAttributeDialog
)
from document_management_system.core.document_model import DocumentModel
from document_management_system.core.plugin_helper import PluginHelper

WidgetUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../ui/relation_editor_feature_side_widget.ui'))


class RelationEditorFeatureSideWidget(QgsAbstractRelationEditorWidget, WidgetUi):

    class LastView(str, Enum):
        ListView = "ListView"
        IconView = "IconView"

    settingsLastView = QgsSettingsEntryString('relationEditorFeatureSideLastView',
                                              PluginHelper.PLUGIN_SLUG,
                                              LastView.ListView,
                                              PluginHelper.tr('Last view used in the relation editor document side widget'))

    def __init__(self, config, parent):
        super().__init__(config, parent)
        self.setupUi(self)

        print('DocumentRelationEditorFeatureSideWidget.__init__')

        self.documents_path = str()
        self.document_filename = str()

        self.model = DocumentModel()

        self._nmRelation = QgsRelation()

        if QSysInfo.productType() == "windows":
            os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"

        layout = QVBoxLayout()
        self.view = QQuickWidget()
        self.view.rootContext().setContextProperty("documentModel", self.model)
        self.view.rootContext().setContextProperty("parentWidget", self)
        self.view.setSource(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../qml/DocumentList.qml')))
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        layout.addWidget(self.view)
        self.setLayout(layout)

    @pyqtProperty(str)
    def LIST_VIEW(self):
      return str(RelationEditorFeatureSideWidget.LastView.ListView)

    @pyqtProperty(str)
    def ICON_VIEW(self):
      return str(RelationEditorFeatureSideWidget.LastView.IconView)

    @pyqtProperty(str)
    def currentView(self):
        return self.settingsLastView.value()

    @currentView.setter
    def currentView(self, value):
        self.settingsLastView.setValue(value)

    def nmRelation(self):
        return self._nmRelation

    def config(self):
        return {

        }

    def setConfig(self, config):
        self.documents_path = config['documents_path']
        self.document_filename = config['document_filename']

    def updateUi(self):
        print('DocumentRelationEditorFeatureSideWidget.updateUi')
        self.model.init(self.relation(),
                        self.nmRelation(),
                        self.feature(),
                        self.documents_path,
                        self.document_filename)

    def afterSetRelations(self):
        self._nmRelation = QgsProject.instance().relationManager().relation(str(self.nmRelationId()))

    def parentFormValueChanged(self, attribute, newValue):
        pass

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

    @pyqtSlot(int)
    def dropDocument(self, documentId):

        if self.checkLayerEditingMode() is False:
            return

        self.deleteFeature(documentId)

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
            default_documents_path = str(exp.evaluate(context))

        filename = QUrl(fileUrl).toLocalFile()
        if default_documents_path:
            filename = QDir(default_documents_path).relativeFilePath(filename)

        keyAttrs = dict()

        # Fields of the linking table
        fields = self.relation().referencingLayer().fields()

        # For generated relations insert the referenced layer field
        if self.relation().type() == QgsRelation.Generated:
            polyRel = self.relation().polymorphicRelation()
            keyAttrs[fields.indexFromName(polyRel.referencedLayerField())] = polyRel.layerRepresentation(self.relation().referencedLayer())

        if self.nmRelation().isValid():
            # only normal relations support m:n relation
            if self.nmRelation().type() != QgsRelation.Normal:
                QMessageBox.critical(self,
                                     self.tr("Add document"),
                                     self.tr("Invalid relation, Only normal relations support m:n relation."))
                return

            # Pre fill inserting document filepath
            attributes = {
                self.nmRelation().referencedLayer().fields().indexFromName(self.document_filename): filename
            }

            # n:m Relation: first let the user create a new feature on the other table
            # and autocreate a new linking feature.
            ok, feature = self.editorContext().vectorLayerTools().addFeature(self.nmRelation().referencedLayer(),
                                                                             attributes,
                                                                             QgsGeometry())
            if not ok:
                QMessageBox.critical(self,
                                     self.tr("Add document"),
                                     self.tr("Could not add a new linking feature."))
                return

            for key in self.relation().fieldPairs():
                keyAttrs[fields.indexOf(key)] = self.feature().attribute(self.relation().fieldPairs()[key])

            for key in self.nmRelation().fieldPairs():
                keyAttrs[fields.indexOf(key)] = feature.attribute(self.nmRelation().fieldPairs()[key])

            linkFeature = QgsVectorLayerUtils.createFeature(self.relation().referencingLayer(),
                                                            QgsGeometry(),
                                                            keyAttrs,
                                                            self.relation().referencingLayer().createExpressionContext())

            if not self.relation().referencingLayer().addFeature(linkFeature):
                QMessageBox.critical(self,
                                     self.tr("Add document"),
                                     self.tr("Could not add a new feature."))
                return

        else:
            for key in self.relation().fieldPairs():
                keyAttrs[fields.indexFromName(key)] = self.feature().attribute(self.relation().fieldPairs()[key])

            # Pre fill inserting document filepath
            keyAttrs[fields] = filename

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
