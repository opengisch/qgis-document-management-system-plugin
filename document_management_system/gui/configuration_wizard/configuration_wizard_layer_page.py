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
from qgis.PyQt.QtCore import pyqtSlot
from qgis.PyQt.QtWidgets import (
    QWizardPage
)
from qgis.core import QgsProject
from qgis.gui import QgsCheckableComboBox

from qgis.PyQt.uic import loadUiType

DialogUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../../ui/configuration_wizard/configuration_wizard_layer_page.ui'))


class ConfigurationWizardLayerPage(QWizardPage, DialogUi):

    def __init__(self, parent=None):
        """Constructor
        """
        self.valid = False
        self._featureLayers = []

        super(ConfigurationWizardLayerPage, self).__init__(parent=parent)
        self.setupUi(self)

        self.setTitle(self.tr("Layer selection"))

        # Fill layers combobox
        mapLayers = QgsProject.instance().mapLayers(True)
        for layerId, layer in mapLayers.items():
            self.mFeatureLayersComboBox.addItem(layer.name(), layerId)

        # Signal slots
        self.mFeatureLayersComboBox.checkedItemsChanged.connect(self.featureLayersComboBoxCheckedItemsChanged)

    def isComplete(self):
        return self.valid

    def setSelectionError(self, error, errorText=""):
        self.mErrorLabel.setText(errorText)

        if self.valid == error:
            self.valid = not self.valid
            self.completeChanged.emit()

    def documentLayer(self):
        return self.mDocumentLayerComboBox.currentLayer()
    
    def featureLayers(self):
        return self._featureLayers

    @pyqtSlot('QStringList')
    def featureLayersComboBoxCheckedItemsChanged(self, layerNames):

        self._featureLayers = []

        layerIds = self.mFeatureLayersComboBox.checkedItemsData()
        
        if len(layerIds) <= 0:
            self.setSelectionError(True, self.tr("At least one feature layer must be selected."))
            return

        firstLayer = True
        fields = []
        for layerId in layerIds:
            layer = QgsProject.instance().mapLayers(True)[layerId]
            self._featureLayers.append(layer)
            if layer and layer.isValid():
                layerFields = layer.fields().names()

                if firstLayer:
                    fields = layerFields
                    firstLayer = False

                else:
                    fields = list(set(fields) & set(layerFields))

        if len(fields) <= 0:
            self.setSelectionError(True, self.tr("The feature layers must have at least one common fields."))
            return

        self.setSelectionError(False)

