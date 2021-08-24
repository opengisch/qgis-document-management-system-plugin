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
    QObject,
    QDir,
    QSysInfo,
    QUrl,
    QVariant,
    pyqtSignal,
    pyqtProperty,
    pyqtSlot
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QAction,
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
from document_management_system.core.file_type_icon_image_provider import FileTypeIconImageProvider
from document_management_system.core.preview_image_provider import PreviewImageProvider
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

    signalCurrentViewChanged = pyqtSignal()

    def __init__(self, config, parent):
        super().__init__(config, parent)
        self.setupUi(self)

        print('DocumentRelationEditorFeatureSideWidget.__init__')

        self.documents_path = str()
        self.document_filename = str()

        self.model = DocumentModel()

        self._nmRelation = QgsRelation()
        self._layerInSameTransactionGroup = False

        self._currentDocumentId = None

        # Actions
        self.actionToggleEditing = QAction(QIcon(":/images/themes/default/mActionToggleEditing.svg"),
                                           self.tr("Toggle editing mode for child layers"))
        self.actionToggleEditing.setCheckable(True)
        self.actionSaveEdits = QAction(QIcon(":/images/themes/default/mActionSaveEdits.svg"),
                                       self.tr("Save child layer edits"))
        self.actionShowForm = QAction(QIcon(":/images/themes/default/mActionMultiEdit.svg"),
                                      self.tr("Show form"))
        self.actionAddFeature = QAction(QIcon(":/images/themes/default/symbologyAdd.svg"),
                                        self.tr("Add document"))
        self.actionDeleteFeature = QAction(QIcon(":/images/themes/default/mActionDeleteSelected.svg"),
                                           self.tr("Drop document"))
        self.actionLinkFeature = QAction(QIcon(":/images/themes/default/mActionLink.svg"),
                                         self.tr("Link document"))
        self.actionUnlinkFeature = QAction(QIcon(":/images/themes/default/mActionUnlink.svg"),
                                           self.tr("Unlink document"))

        # Tool buttons
        self.mToggleEditingToolButton.setDefaultAction(self.actionToggleEditing)
        self.mSaveEditsToolButton.setDefaultAction(self.actionSaveEdits)
        self.mShowFormToolButton.setDefaultAction(self.actionShowForm)
        self.mAddFeatureToolButton.setDefaultAction(self.actionAddFeature)
        self.mDeleteFeatureToolButton.setDefaultAction(self.actionDeleteFeature)
        self.mLinkFeatureToolButton.setDefaultAction(self.actionLinkFeature)
        self.mUnlinkFeatureToolButton.setDefaultAction(self.actionUnlinkFeature)

        self.mListViewToolButton.setIcon(QIcon(":/images/themes/default/mIconListView.svg"))
        self.mIconViewToolButton.setIcon(QIcon(":/images/themes/default/mActionIconView.svg"))
        self.mListViewToolButton.setChecked(self.currentView == str(RelationEditorFeatureSideWidget.LastView.ListView))
        self.mIconViewToolButton.setChecked(self.currentView == str(RelationEditorFeatureSideWidget.LastView.IconView))

        # Quick image providers
        self._previewImageProvider = PreviewImageProvider()
        self._fileTypeSmallIconProvider = FileTypeIconImageProvider(32)
        self._fileTypeBigIconProvider = FileTypeIconImageProvider(100)

        # Setup QML part
        self.view = QQuickWidget()
        self.view.rootContext().setContextProperty("documentModel", self.model)
        self.view.rootContext().setContextProperty("parentWidget", self)
        self.view.rootContext().setContextProperty("CONST_LIST_VIEW", str(RelationEditorFeatureSideWidget.LastView.ListView))
        self.view.rootContext().setContextProperty("CONST_ICON_VIEW", str(RelationEditorFeatureSideWidget.LastView.IconView))
        self.view.engine().addImageProvider("previewImageProvider", self._previewImageProvider)
        self.view.engine().addImageProvider("fileTypeSmallIconProvider", self._fileTypeSmallIconProvider)
        self.view.engine().addImageProvider("fileTypeBigIconProvider", self._fileTypeBigIconProvider)
        self.view.setSource(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../qml/DocumentList.qml')))
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.layout().addWidget(self.view)

        # Set initial state for add / remove etc.buttons
        self.updateButtons()

        # Signal slots
        self.actionToggleEditing.triggered.connect(self.toggleEditing)
        self.actionSaveEdits.triggered.connect(self.saveChildLayerEdits)
        self.actionShowForm.triggered.connect(self.showDocumentForm)
        self.actionAddFeature.triggered.connect(self.addDocument)
        self.actionDeleteFeature.triggered.connect(self.dropDocument)
        self.actionLinkFeature.triggered.connect(self.linkDocument)
        self.actionUnlinkFeature.triggered.connect(self.unlinkDocument)
        self.mListViewToolButton.toggled.connect(self.listViewToolButtonToggled)
        self.mIconViewToolButton.toggled.connect(self.iconViewToolButtonToggled)

    @pyqtProperty(str)
    def currentView(self):
        return self.settingsLastView.value()

    def updateCurrentView(self):
        if self.mListViewToolButton.isChecked():
            self.settingsLastView.setValue(str(RelationEditorFeatureSideWidget.LastView.ListView))
        else:
            self.settingsLastView.setValue(str(RelationEditorFeatureSideWidget.LastView.IconView))

        self.signalCurrentViewChanged.emit()

    @pyqtProperty(QVariant)
    def currentDocumentId(self):
        return self._currentDocumentId

    @pyqtSlot(QVariant)
    def setCurrentDocumentId(self, value):
        self._currentDocumentId = value
        self.updateButtons()

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

    def updateButtons(self):
        toggleEditingButtonEnabled = False
        editable = False
        linkable = False
        spatial = False
        selectionNotEmpty = self._currentDocumentId is not None

        if self.relation().isValid():
            toggleEditingButtonEnabled = self.relation().referencingLayer().supportsEditing()
            editable = self.relation().referencingLayer().isEditable()
            linkable = self.relation().referencingLayer().isEditable()
            spatial = self.relation().referencingLayer().isSpatial()

        if self.nmRelation().isValid():
            toggleEditingButtonEnabled |= self.nmRelation().referencedLayer().supportsEditing()
            editable = self.nmRelation().referencedLayer().isEditable()
            spatial = self.nmRelation().referencedLayer().isSpatial()

        self.mToggleEditingToolButton.setEnabled(toggleEditingButtonEnabled)
        self.mAddFeatureToolButton.setEnabled(editable)
        self.mLinkFeatureToolButton.setEnabled(linkable)
        self.mDeleteFeatureToolButton.setEnabled(editable and selectionNotEmpty)
        self.mUnlinkFeatureToolButton.setEnabled(linkable and selectionNotEmpty)
        self.mToggleEditingToolButton.setChecked(editable)
        self.mSaveEditsToolButton.setEnabled(editable or linkable)

        self.mShowFormToolButton.setEnabled(selectionNotEmpty)

        self.mToggleEditingToolButton.setVisible(self._layerInSameTransactionGroup is False)
        self.mSaveEditsToolButton.setVisible(self._layerInSameTransactionGroup is False)

    def afterSetRelations(self):
        self._nmRelation = QgsProject.instance().relationManager().relation(str(self.nmRelationId()))

        self._checkTransactionGroup()

        if self.relation().isValid():
            self.relation().referencingLayer().editingStopped.connect(self.updateButtons)
            self.relation().referencingLayer().editingStarted.connect(self.updateButtons)

        if self.nmRelation().isValid():
            self.nmRelation().referencedLayer().editingStarted.connect(self.updateButtons)
            self.nmRelation().referencedLayer().editingStopped.connect(self.updateButtons)

        self.updateButtons()

    def _checkTransactionGroup(self):

        self._layerInSameTransactionGroup = False
        connectionString = PluginHelper.connectionString(self.relation().referencedLayer().source())
        transactionGroup = QgsProject.instance().transactionGroup(self.relation().referencedLayer().providerType(),
                                                                  connectionString)

        if transactionGroup is None:
            self.updateButtons()
            return

        if self.nmRelation().isValid():
            if (self.relation().referencedLayer() in transactionGroup.layers() and
               self.relation().referencingLayer() in transactionGroup.layers() and
               self.nmRelation().referencedLayer() in transactionGroup.layers()):
                self._layerInSameTransactionGroup = True
        else:
            if (self.relation().referencedLayer() in transactionGroup.layers() and
               self.relation().referencingLayer() in transactionGroup.layers()):
                self._layerInSameTransactionGroup = True

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

    @pyqtSlot(bool)
    def toggleEditing(self, state):

        super().toggleEditing(state)
        self.updateButtons()

    @pyqtSlot()
    def saveChildLayerEdits(self):

        super().saveEdits()

    @pyqtSlot()
    def addDocument(self):

        # Workaround because of QGIS not resetting this property after linking features
        self.editorContext().vectorLayerTools().setForceSuppressFormPopup(False)
        self.addFeature()

    @pyqtSlot()
    def dropDocument(self):

        if self._currentDocumentId is None:
            return

        self.deleteFeature(self._currentDocumentId)

    @pyqtSlot(str)
    def addDroppedDocument(self, fileUrl):

        if self.checkLayerEditingMode() is False:
            return

        # Workaround because of QGIS not resetting this property after linking features
        self.editorContext().vectorLayerTools().setForceSuppressFormPopup(False)

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

        self.linkFeature()

    @pyqtSlot()
    def unlinkDocument(self):

        if self._currentDocumentId is None:
            return

        self.unlinkFeature(self._currentDocumentId)

    @pyqtSlot()
    def showDocumentForm(self):

        if self._currentDocumentId is None:
            return

        layer = self.relation().referencingLayer()
        if self.nmRelation().isValid():
            layer = self.nmRelation().referencedLayer()

        showDocumentFormDialog = QgsAttributeDialog(layer,
                                                    layer.getFeature(self._currentDocumentId),
                                                    False,
                                                    self,
                                                    True)
        showDocumentFormDialog.exec()
        self.updateUi()

    @pyqtSlot(bool)
    def listViewToolButtonToggled(self, checked):
        self.mIconViewToolButton.blockSignals(True)
        self.mIconViewToolButton.setChecked(checked is False)
        self.mIconViewToolButton.blockSignals(False)
        self.updateCurrentView()

    @pyqtSlot(bool)
    def iconViewToolButtonToggled(self, checked):
        self.mListViewToolButton.blockSignals(True)
        self.mListViewToolButton.setChecked(checked is False)
        self.mListViewToolButton.blockSignals(False)
        self.updateCurrentView()
