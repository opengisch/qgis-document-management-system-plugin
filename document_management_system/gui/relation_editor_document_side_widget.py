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
from enum import Enum, IntEnum
from qgis.PyQt.QtCore import Qt, QTimer, pyqtSlot
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QInputDialog, QMessageBox, QTreeWidgetItem
from qgis.PyQt.uic import loadUiType
from qgis.core import (
    QgsProject,
    QgsRelation,
    QgsPolymorphicRelation,
    QgsGeometry,
    QgsFeature,
    QgsFeatureRequest,
    QgsIconUtils,
    QgsLogger,
    QgsVectorLayerUtils,
)
from qgis.gui import QgsAbstractRelationEditorWidget, QgsAttributeDialog, QgsFeatureSelectionDlg
from document_management_system.core.plugin_helper import PluginHelper

WidgetUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), "../ui/relation_editor_document_side_widget.ui"))


class Cardinality(Enum):
    ManyToOne = 1
    ManyToMany = 2
    ManyToOnePolymorphic = 3
    ManyToManyPolymorphic = 4


class TreeWidgetItemType(Enum):
    Layer = 1
    Feature = 2


class TreeWidgetItemRole(IntEnum):
    Type = Qt.UserRole + 1
    Layer = Qt.UserRole + 2
    Feature = Qt.UserRole + 3
    LinkFeature = Qt.UserRole + 4


class RelationEditorDocumentSideWidget(QgsAbstractRelationEditorWidget, WidgetUi):
    def __init__(self, config, parent):
        super().__init__(config, parent)
        self._updateUiTimer = QTimer()
        self._updateUiTimer.setSingleShot(True)
        self._updateUiTimer.timeout.connect(self.updateUiTimeout)
        self.setupUi(self)

        self.polymorphicRelationEnabled = False
        self.polymorphicRelationId = str()

        self.generatedRelationList = []

        self._nmRelation = QgsRelation()
        self._polymorphicRelation = QgsPolymorphicRelation()
        self._layerInSameTransactionGroup = False

        self.cardinality = Cardinality.ManyToOne

        # Actions
        self.actionToggleEditing = QAction(
            QIcon(":/images/themes/default/mActionToggleEditing.svg"), self.tr("Toggle editing mode for child layers")
        )
        self.actionToggleEditing.setCheckable(True)
        self.actionSaveEdits = QAction(
            QIcon(":/images/themes/default/mActionSaveEdits.svg"), self.tr("Save child layer edits")
        )
        self.actionShowForm = QAction(QIcon(":/images/themes/default/mActionMultiEdit.svg"), self.tr("Show form"))
        self.actionLinkFeature = QAction(QIcon(":/images/themes/default/mActionLink.svg"), self.tr("Link feature"))
        self.actionUnlinkFeature = QAction(
            QIcon(":/images/themes/default/mActionUnlink.svg"), self.tr("Unlink feature")
        )

        # Tool buttons
        self.mToggleEditingToolButton.setDefaultAction(self.actionToggleEditing)
        self.mSaveEditsToolButton.setDefaultAction(self.actionSaveEdits)
        self.mShowFormToolButton.setDefaultAction(self.actionShowForm)
        self.mShowFormToolButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.mLinkFeaturesToolButton.setDefaultAction(self.actionLinkFeature)
        self.mLinkFeaturesToolButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.mUnlinkFeaturesToolButton.setDefaultAction(self.actionUnlinkFeature)
        self.mUnlinkFeaturesToolButton.setToolButtonStyle(Qt.ToolButtonIconOnly)

        # TreeWidgetItem menu
        self.mFeaturesTreeWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.mFeaturesTreeWidget.addAction(self.actionShowForm)
        self.mFeaturesTreeWidget.addAction(self.actionUnlinkFeature)

        # Set initial state for add / remove etc.buttons
        self.updateButtons()

        # Signal slots
        self.actionToggleEditing.triggered.connect(self.toggleEditing)
        self.actionSaveEdits.triggered.connect(self.saveChildLayerEdits)
        self.actionShowForm.triggered.connect(self.actionShowFormTriggered)
        self.actionLinkFeature.triggered.connect(self.actionLinkFeatureTriggered)
        self.actionUnlinkFeature.triggered.connect(self.actionUnlinkFeatureTriggered)
        self.mFeaturesTreeWidget.currentItemChanged.connect(self.updateButtons)

    def nmRelation(self):
        return self._nmRelation

    def config(self):
        return {}

    def setConfig(self, config):
        self.polymorphicRelationEnabled = config["polymorphic_relation_enabled"]
        self.polymorphicRelationId = config["polymorphic_relation_id"]

        if self.polymorphicRelationEnabled is False:
            return

        self._polymorphicRelation = (
            QgsProject.instance().relationManager().polymorphicRelation(self.polymorphicRelationId)
        )

        self._setCardinality()

    def updateUi(self):
        self._updateUiTimer.start(200)

    def updateUiTimeout(self):
        print("DocumentRelationEditorDocumentSideWidget.updateUiTimeout")

        self.mFeaturesTreeWidget.clear()

        if self.relation().isValid() is False or self.feature().isValid() is False:
            return

        if self.cardinality == Cardinality.ManyToOne:
            self.updateUiManyToOne()

        if self.cardinality == Cardinality.ManyToMany:
            self.updateUiManyToMany()

        if self.cardinality == Cardinality.ManyToOnePolymorphic:
            self.updateUiManyToOnePolymorphic()

        if self.cardinality == Cardinality.ManyToManyPolymorphic:
            self.updateUiManyToManyPolymorphic()

    def updateUiManyToOne(self):
        layer = self.relation().referencingLayer()
        request = self.relation().getRelatedFeaturesRequest(self.feature())
        for feature in layer.getFeatures(request):
            treeWidgetItem = QTreeWidgetItem(
                self.mFeaturesTreeWidget, [QgsVectorLayerUtils.getFeatureDisplayString(layer, feature)]
            )
            treeWidgetItem.setData(0, TreeWidgetItemRole.Type, TreeWidgetItemType.Feature)
            treeWidgetItem.setData(0, TreeWidgetItemRole.Layer, layer)
            treeWidgetItem.setData(0, TreeWidgetItemRole.Feature, feature)

    def updateUiManyToMany(self):
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
                treeWidgetItem = QTreeWidgetItem(
                    self.mFeaturesTreeWidget, [QgsVectorLayerUtils.getFeatureDisplayString(finalLayer, finalFeature)]
                )
                treeWidgetItem.setData(0, TreeWidgetItemRole.Type, TreeWidgetItemType.Feature)
                treeWidgetItem.setData(0, TreeWidgetItemRole.Layer, finalLayer)
                treeWidgetItem.setData(0, TreeWidgetItemRole.Feature, feature)

    def updateUiManyToOnePolymorphic(self):
        layerFeature = dict()
        for relation in self._polymorphicRelation.generateRelations():
            layer = relation.referencingLayer()
            request = relation.getRelatedFeaturesRequest(self.feature())
            finalLayer = relation.referencedLayer()
            for feature in layer.getFeatures(request):
                if finalLayer in layerFeature:
                    layerFeature[finalLayer].append(feature)
                else:
                    layerFeature[finalLayer] = [feature]

        for layer in layerFeature:
            treeWidgetItemLayer = QTreeWidgetItem(self.mFeaturesTreeWidget, [layer.name()])
            treeWidgetItemLayer.setData(0, TreeWidgetItemRole.Type, TreeWidgetItemType.Layer)
            treeWidgetItemLayer.setData(0, TreeWidgetItemRole.Layer, layer)
            treeWidgetItemLayer.setIcon(0, QgsIconUtils.iconForLayer(layer))
            for feature in layerFeature[layer]:
                treeWidgetItem = QTreeWidgetItem(
                    treeWidgetItemLayer, [QgsVectorLayerUtils.getFeatureDisplayString(layerFeature, feature)]
                )
                treeWidgetItem.setData(0, TreeWidgetItemRole.Type, TreeWidgetItemType.Feature)
                treeWidgetItem.setData(0, TreeWidgetItemRole.Layer, layer)
                treeWidgetItem.setData(0, TreeWidgetItemRole.Feature, feature)
            treeWidgetItemLayer.setExpanded(True)

    def updateUiManyToManyPolymorphic(self):
        layer = self.relation().referencingLayer()
        request = self.relation().getRelatedFeaturesRequest(self.feature())
        layerFeature = dict()
        for linkFeature in layer.getFeatures(request):
            for relation in self._polymorphicRelation.generateRelations():
                referencedFeatureRequest = relation.getReferencedFeatureRequest(linkFeature)
                filterExpression = referencedFeatureRequest.filterExpression()
                nmRequest = QgsFeatureRequest()
                nmRequest.setFilterExpression(filterExpression.expression())

                finalLayer = relation.referencedLayer()
                for finalFeature in finalLayer.getFeatures(nmRequest):
                    features = finalFeature, linkFeature
                    if finalLayer in layerFeature:
                        layerFeature[finalLayer].append(features)
                    else:
                        layerFeature[finalLayer] = [features]

        for layer in layerFeature:
            treeWidgetItemLayer = QTreeWidgetItem(self.mFeaturesTreeWidget, [layer.name()])
            treeWidgetItemLayer.setData(0, TreeWidgetItemRole.Type, TreeWidgetItemType.Layer)
            treeWidgetItemLayer.setData(0, TreeWidgetItemRole.Layer, layer)
            treeWidgetItemLayer.setIcon(0, QgsIconUtils.iconForLayer(layer))
            for feature, linkFeature in layerFeature[layer]:
                treeWidgetItem = QTreeWidgetItem(
                    treeWidgetItemLayer, [QgsVectorLayerUtils.getFeatureDisplayString(layer, feature)]
                )
                treeWidgetItem.setData(0, TreeWidgetItemRole.Type, TreeWidgetItemType.Feature)
                treeWidgetItem.setData(0, TreeWidgetItemRole.Layer, layer)
                treeWidgetItem.setData(0, TreeWidgetItemRole.Feature, feature)
                treeWidgetItem.setData(0, TreeWidgetItemRole.LinkFeature, linkFeature)
            treeWidgetItemLayer.setExpanded(True)

    def afterSetRelations(self):
        self._nmRelation = QgsProject.instance().relationManager().relation(str(self.nmRelationId()))

        if not self.relation().isValid():
            QgsLogger.warning(self.tr(f"Invalid relation set, relation id: '{self.relation().id()}'"))
            self.updateButtons()
            return

        self._setCardinality()

        self._checkTransactionGroup()

        self.relation().referencingLayer().editingStopped.connect(self.updateButtons)
        self.relation().referencingLayer().editingStarted.connect(self.updateButtons)

        if self.nmRelation().isValid():
            self.nmRelation().referencedLayer().editingStarted.connect(self.updateButtons)
            self.nmRelation().referencedLayer().editingStopped.connect(self.updateButtons)

        self.updateButtons()

    def parentFormValueChanged(self, attribute, newValue):
        self.updateUi()

    def checkLayerEditingMode(self):

        if self.relation().referencingLayer().isEditable() is False:
            QMessageBox.critical(
                self,
                self.tr("Layer not editable"),
                self.tr("Layer '{0}' is not in editing mode.").format(self.relation().referencingLayer().name()),
            )
            return False

        if self.nmRelation().isValid():
            if self.nmRelation().referencedLayer().isEditable() is False:
                QMessageBox.critical(
                    self,
                    self.tr("Layer not editable"),
                    self.tr("Layer '{0}' is not in editing mode.").format(self.nmRelation().referencedLayer().name()),
                )
                return False

        return True

    def _setCardinality(self):

        if self.nmRelation().isValid() is False and self.polymorphicRelationEnabled is False:
            self.cardinality = Cardinality.ManyToOne
            return

        elif self.nmRelation().isValid() and self.polymorphicRelationEnabled is False:
            self.cardinality = Cardinality.ManyToMany
            return

        elif (
            self.polymorphicRelationEnabled
            and self._polymorphicRelation.referencingLayer().id() == self.relation().referencedLayer().id()
        ):
            self.cardinality = Cardinality.ManyToOnePolymorphic
            return

        elif (
            self.polymorphicRelationEnabled
            and self._polymorphicRelation.referencingLayer().id() == self.relation().referencingLayer().id()
        ):
            self.cardinality = Cardinality.ManyToManyPolymorphic
            return

        else:
            print("WARNING invalid cardinality set")

    @pyqtSlot(bool)
    def toggleEditing(self, state):

        super().toggleEditing(state)
        self.updateButtons()

    @pyqtSlot()
    def saveChildLayerEdits(self):

        super().saveEdits()

    def actionShowFormTriggered(self):

        if self.mFeaturesTreeWidget.currentItem() is None:
            QMessageBox.critical(self, self.tr("No feature selected"), self.tr("Please select a feature."))
            return

        if self.mFeaturesTreeWidget.currentItem().data(0, TreeWidgetItemRole.Type) != TreeWidgetItemType.Feature:
            QMessageBox.critical(self, self.tr("Selected item is not a feature"), self.tr("Please select a feature."))
            return

        showDocumentFormDialog = QgsAttributeDialog(
            self.mFeaturesTreeWidget.currentItem().data(0, TreeWidgetItemRole.Layer),
            self.mFeaturesTreeWidget.currentItem().data(0, TreeWidgetItemRole.Feature),
            False,
            self,
            True,
        )
        showDocumentFormDialog.exec()
        self.updateUi()

    def actionLinkFeatureTriggered(self):

        if self.checkLayerEditingMode() is False:
            return

        if self.cardinality == Cardinality.ManyToOne:
            self.linkFeature()

        if self.cardinality == Cardinality.ManyToMany:
            self.linkFeature()

        if self.cardinality == Cardinality.ManyToOnePolymorphic:
            self.linkFeatureManyToOnePolymorphic()
            self.updateUi()

        if self.cardinality == Cardinality.ManyToManyPolymorphic:
            self.linkFeatureManyToManyPolymorphic()
            self.updateUi()

    def linkFeatureManyToOnePolymorphic(self):
        print("link ManyToOnePolymorphic")

    def linkFeatureManyToManyPolymorphic(self):

        nmRelations = dict()
        for relation in self._polymorphicRelation.generateRelations():
            nmRelations[relation.referencedLayer().name()] = relation

        layerName, ok = QInputDialog.getItem(
            self, self.tr("Please selct a layer"), self.tr("Layer:"), nmRelations.keys()
        )

        if not ok:
            return

        nmRelation = nmRelations[layerName]
        selectionDlg = QgsFeatureSelectionDlg(nmRelation.referencedLayer(), self.editorContext(), self)
        selectionDlg.setWindowTitle(self.tr("Please select the features to link. Layer: {0}").format(layerName))
        if not selectionDlg.exec():
            return

        # Fields of the linking table
        fields = self.relation().referencingLayer().fields()

        linkAttributes = dict()
        linkAttributes[
            fields.indexFromName(self._polymorphicRelation.referencedLayerField())
        ] = self._polymorphicRelation.layerRepresentation(nmRelation.referencedLayer())
        for key in self.relation().fieldPairs():
            linkAttributes[fields.indexOf(key)] = self.feature().attribute(self.relation().fieldPairs()[key])

        # Expression context for the linking table
        context = self.relation().referencingLayer().createExpressionContext()

        featureIterator = nmRelation.referencedLayer().getFeatures(
            QgsFeatureRequest()
            .setFilterFids(selectionDlg.selectedFeatures())
            .setSubsetOfAttributes(nmRelation.referencedFields())
        )
        relatedFeature = QgsFeature()
        newFeatures = []
        while featureIterator.nextFeature(relatedFeature):
            for key in nmRelation.fieldPairs():
                linkAttributes[fields.indexOf(key)] = relatedFeature.attribute(nmRelation.fieldPairs()[key])

            linkFeature = QgsVectorLayerUtils.createFeature(
                self.relation().referencingLayer(), QgsGeometry(), linkAttributes, context
            )
            newFeatures.append(linkFeature)

        self.relation().referencingLayer().addFeatures(newFeatures)
        ids = []
        for feature in newFeatures:
            ids.append(feature.id())
        self.relation().referencingLayer().selectByIds(ids)

    def actionUnlinkFeatureTriggered(self):

        if self.checkLayerEditingMode() is False:
            return

        if self.mFeaturesTreeWidget.currentItem() is None:
            QMessageBox.critical(self, self.tr("No feature selected"), self.tr("Please select a feature to unlink."))
            return

        if self.mFeaturesTreeWidget.currentItem().data(0, TreeWidgetItemRole.Type) != TreeWidgetItemType.Feature:
            QMessageBox.critical(self, self.tr("Selected item is not a feature"), self.tr("Please select a feature."))
            return

        if self.cardinality == Cardinality.ManyToOne:
            self.unlinkFeature(self.mFeaturesTreeWidget.currentItem().data(0, TreeWidgetItemRole.Feature).id())

        if self.cardinality == Cardinality.ManyToMany:
            self.unlinkFeature(self.mFeaturesTreeWidget.currentItem().data(0, TreeWidgetItemRole.Feature).id())

        if self.cardinality == Cardinality.ManyToOnePolymorphic:
            print("unlink ManyToOnePolymorphic")

        if self.cardinality == Cardinality.ManyToManyPolymorphic:
            self.relation().referencingLayer().deleteFeature(
                self.mFeaturesTreeWidget.currentItem().data(0, TreeWidgetItemRole.LinkFeature).id()
            )
            self.updateUi()

    def updateButtons(self):

        toggleEditingButtonEnabled = False
        editable = False
        linkable = False

        selectionNotEmpty = True
        if (
            self.mFeaturesTreeWidget.currentItem() is None
            or self.mFeaturesTreeWidget.currentItem().data(0, TreeWidgetItemRole.Type) != TreeWidgetItemType.Feature
        ):
            selectionNotEmpty = False

        if self.relation().isValid():
            toggleEditingButtonEnabled = self.relation().referencingLayer().supportsEditing()
            editable = self.relation().referencingLayer().isEditable()
            linkable = self.relation().referencingLayer().isEditable()

        if self.nmRelation().isValid():
            toggleEditingButtonEnabled |= self.nmRelation().referencedLayer().supportsEditing()
            editable = self.nmRelation().referencedLayer().isEditable()

        self.actionToggleEditing.setEnabled(toggleEditingButtonEnabled)
        self.actionLinkFeature.setEnabled(linkable)
        self.actionUnlinkFeature.setEnabled(linkable and selectionNotEmpty)
        self.actionToggleEditing.setChecked(editable)
        self.actionSaveEdits.setEnabled(editable or linkable)

        self.actionShowForm.setEnabled(selectionNotEmpty)

        self.mToggleEditingToolButton.setVisible(self._layerInSameTransactionGroup is False)
        self.mSaveEditsToolButton.setVisible(self._layerInSameTransactionGroup is False)

    def _checkTransactionGroup(self):

        self._layerInSameTransactionGroup = False
        connectionString = PluginHelper.connectionString(self.relation().referencedLayer().source())
        transactionGroup = QgsProject.instance().transactionGroup(
            self.relation().referencedLayer().providerType(), connectionString
        )

        if transactionGroup is None:
            self.updateButtons()
            return

        if self.nmRelation().isValid():
            if (
                self.relation().referencedLayer() in transactionGroup.layers()
                and self.relation().referencingLayer() in transactionGroup.layers()
                and self.nmRelation().referencedLayer() in transactionGroup.layers()
            ):
                self._layerInSameTransactionGroup = True
        else:
            if (
                self.relation().referencedLayer() in transactionGroup.layers()
                and self.relation().referencingLayer() in transactionGroup.layers()
            ):
                self._layerInSameTransactionGroup = True
