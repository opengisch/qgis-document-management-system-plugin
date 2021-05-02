# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Document Management System Plugin
# Copyright (C) 2021 Damiano Lombardi
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

import os
from enum import Enum
from qgis.PyQt.QtCore import Qt, pyqtSlot
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMessageBox, QTreeWidgetItem, QAction
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsProject, QgsRelation, QgsPolymorphicRelation, QgsExpression, QgsExpressionContext, QgsExpressionContextUtils, QgsGeometry, QgsFeature, QgsFeatureRequest
from qgis.gui import QgsAbstractRelationEditorWidget

WidgetUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../ui/document_relation_editor_document_side_widget.ui'))


class Cardinality(Enum):
    ManyToOne = 1
    ManyToMany = 2
    ManyToOnePolymorphic = 3
    ManyToManyPolymorphic = 4


class DocumentRelationEditorDocumentSideWidget(QgsAbstractRelationEditorWidget, WidgetUi):

    def __init__(self, config, parent):
        super().__init__(config, parent)
        self.setupUi(self)

        print('DocumentRelationEditorDocumentSideWidget.__init__')

        self.polymorphicRelationEnabled = False
        self.polymorphicRelationId = str()

        self.generatedRelationList = []

        self._nmRelation = QgsRelation()
        self._polymorphicRelation = QgsPolymorphicRelation()

        self.cardinality = Cardinality.ManyToOne

        # Actions
        self.actionShowForm = QAction(QIcon(":/images/themes/default/mActionMultiEdit.svg"),
                                      self.tr("Show form"))
        self.actionLinkFeature = QAction(QIcon(":/images/themes/default/mActionLink.svg"),
                                         self.tr("Link feature"))
        self.actionUnlinkFeature = QAction(QIcon(":/images/themes/default/mActionUnlink.svg"),
                                           self.tr("Unlink feature"))

        # Tool buttons
        self.mShowFormToolButton.setDefaultAction(self.actionShowForm)
        self.mShowFormToolButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.mLinkFeaturesToolButton.setDefaultAction(self.actionLinkFeature)
        self.mLinkFeaturesToolButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.mUnlinkFeaturesToolButton.setDefaultAction(self.actionUnlinkFeature)
        self.mUnlinkFeaturesToolButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # Signal slots
        self.actionShowForm.triggered.connect(self.actionShowFormTriggered)
        self.actionLinkFeature.triggered.connect(self.actionLinkFeatureTriggered)
        self.actionUnlinkFeature.triggered.connect(self.actionUnlinkFeatureTriggered)

    def nmRelation(self):
        return self._nmRelation

    def config(self):
        return {

        }

    def setConfig(self, config):
        self.polymorphicRelationEnabled = config['polymorphic_relation_enabled']
        self.polymorphicRelationId = config['polymorphic_relation_id']

        if self.polymorphicRelationEnabled is False:
            return

        self._polymorphicRelation = QgsProject.instance().relationManager().polymorphicRelation(self.polymorphicRelationId)

        self._setCardinality()

    def updateUi(self):
        print('DocumentRelationEditorDocumentSideWidget.updateUi')

        self.mFeaturesTreeWidget.clear()

        if self.relation().isValid() is False or self.feature().isValid() is False:
            return

        if self.cardinality == Cardinality.ManyToOne:
            layer = self.relation().referencingLayer()
            request = self.relation().getRelatedFeaturesRequest(self.feature())
            for feature in layer.getFeatures(request):
                QTreeWidgetItem(self.mFeaturesTreeWidget, [str(feature.id())])
            return

        if self.cardinality == Cardinality.ManyToMany:
            layer = self.relation().referencingLayer()
            request = self.relation().getRelatedFeaturesRequest(self.feature())
            filters = []
            for feature in layer.getFeatures(request):
                referencedFeatureRequest = self.nmRelation().getReferencedFeatureRequest(feature)
                filterExpression = referencedFeatureRequest.filterExpression()
                filters.append("(" + filterExpression.expression() + ")")

                nmRequest = QgsFeatureRequest()
                nmRequest.setFilterExpression(" OR ".join(filters))

                finalLayer = self.nmRelation().referencedLayer()
                for finalFeature in finalLayer.getFeatures(nmRequest):
                    QTreeWidgetItem(self.mFeaturesTreeWidget, [str(finalFeature.id())])
            return

        if self.cardinality == Cardinality.ManyToOnePolymorphic:
            layerFeature = dict()
            for relation in self._polymorphicRelation.generateRelations():
                layer = relation.referencingLayer()
                request = relation.getRelatedFeaturesRequest(self.feature())
                for feature in layer.getFeatures(request):
                    if finalLayer.name() in layerFeature:
                        layerFeature[finalLayer.name()].append(finalFeature.id())
                    else:
                        layerFeature[finalLayer.name()] = [finalFeature.id()]

            for layerName in layerFeature:
                treeWidgetItemLayer = QTreeWidgetItem(self.mFeaturesTreeWidget, [layerName])
                for featureId in layerFeature[layerName]:
                    QTreeWidgetItem(treeWidgetItemLayer, [str(featureId)])
                treeWidgetItemLayer.setExpanded(True)

        if self.cardinality == Cardinality.ManyToManyPolymorphic:
            layer = self.relation().referencingLayer()
            request = self.relation().getRelatedFeaturesRequest(self.feature())
            filters = []
            layerFeature = dict()
            for feature in layer.getFeatures(request):
                for relation in self._polymorphicRelation.generateRelations():
                    referencedFeatureRequest = relation.getReferencedFeatureRequest(feature)
                    filterExpression = referencedFeatureRequest.filterExpression()
                    filters.append("(" + filterExpression.expression() + ")")

                    nmRequest = QgsFeatureRequest()
                    nmRequest.setFilterExpression(" OR ".join(filters))

                    finalLayer = relation.referencedLayer()
                    for finalFeature in finalLayer.getFeatures(nmRequest):
                        if finalLayer.name() in layerFeature:
                            layerFeature[finalLayer.name()].append(finalFeature.id())
                        else:
                            layerFeature[finalLayer.name()] = [finalFeature.id()]

            for layerName in layerFeature:
                treeWidgetItemLayer = QTreeWidgetItem(self.mFeaturesTreeWidget, [layerName])
                for featureId in layerFeature[layerName]:
                    QTreeWidgetItem(treeWidgetItemLayer, [str(featureId)])
                treeWidgetItemLayer.setExpanded(True)

    def afterSetRelations(self):
        self._nmRelation = QgsProject.instance().relationManager().relation(str(self.nmRelationId()))

        self._setCardinality()

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

    def _setCardinality(self):

        if (
             self.nmRelation().isValid() is False and
             self.polymorphicRelationEnabled is False
           ):
            self.cardinality = Cardinality.ManyToOne
            return

        elif (
               self.nmRelation().isValid() and
               self.polymorphicRelationEnabled is False
             ):
            self.cardinality = Cardinality.ManyToMany
            return

        elif (
               self.polymorphicRelationEnabled and
               self._polymorphicRelation.referencingLayer().id() == self.relation().referencedLayer().id()
             ):
            self.cardinality = Cardinality.ManyToManyPolymorphic
            return

        elif (
               self.polymorphicRelationEnabled and
               self._polymorphicRelation.referencingLayer().id() == self.relation().referencingLayer().id()
             ):
            self.cardinality = Cardinality.ManyToManyPolymorphic
            return

        else:
            print("WARNING invalid cardinality set")

    def actionShowFormTriggered(self):

        if self.mFeaturesTreeWidget.currentItem() is None:
            QMessageBox.critical(self,
                                 self.tr("No feature selected"),
                                 self.tr("Please select a feature."))
            return

        print("actionShowFormTriggered: {0}".format(self.mFeaturesTreeWidget.currentItem()))

    def actionLinkFeatureTriggered(self):
        print("actionLinkFeatureTriggered")

    def actionUnlinkFeatureTriggered(self):

        if self.mFeaturesTreeWidget.currentItem() is None:
            QMessageBox.critical(self,
                                 self.tr("No feature selected"),
                                 self.tr("Please select a feature to unlink."))

        print("actionUnlinkFeatureTriggered")
