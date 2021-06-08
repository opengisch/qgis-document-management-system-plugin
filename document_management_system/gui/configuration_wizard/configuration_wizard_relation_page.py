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
from qgis.PyQt.QtCore import pyqtSlot
from qgis.PyQt.QtWidgets import (
    QWizardPage
)
from qgis.core import (
    QgsProject,
    QgsMapLayer
)

from qgis.PyQt.uic import loadUiType

DialogUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../../ui/configuration_wizard/configuration_wizard_relation_page.ui'))


class ConfigurationWizardRelationPage(QWizardPage, DialogUi):

    class RelationType(IntEnum):
        ManyToOne = 0
        ManyToMany = 1

    class Cardinality(Enum):
        ManyToOne = 1
        ManyToMany = 2
        ManyToOnePolymorphic = 3
        ManyToManyPolymorphic = 4

    def __init__(self, configurationWizardLayerPage, parent=None):
        """Constructor
        """
        self.valid = False
        self.cardinality = self.Cardinality.ManyToOne
        self.documentLayer = None
        self.featureLayers = []
        self.configurationWizardLayerPage = configurationWizardLayerPage

        super(ConfigurationWizardRelationPage, self).__init__(parent=parent)
        self.setupUi(self)

        self.setTitle(self.tr("Relations"))

        self.mRelationTypeComboBox.insertItem(self.RelationType.ManyToOne, self.tr('One to many'))
        self.mRelationTypeComboBox.insertItem(self.RelationType.ManyToMany, self.tr('Many to many'))

        # Signal slots
        self.mRelationTypeComboBox.currentIndexChanged.connect(self.relationTypeComboBoxCurrentIndexChanged)

    def initializePage(self):        
        self.documentLayer = self.configurationWizardLayerPage.documentLayer()
        self.featureLayers = self.configurationWizardLayerPage.featureLayers()

        self.updateRelations()

    def updateRelations(self):
        print("updateRelations cb currentIndex {0}, layers count {1}".format(self.mRelationTypeComboBox.currentIndex(), len(self.featureLayers)))
        
        if (self.mRelationTypeComboBox.currentIndex() == self.RelationType.ManyToOne and
            len(self.featureLayers) == 1):
            self.cardinality = self.Cardinality.ManyToOne
            self.updateRelationsManyToOne()

        elif (self.mRelationTypeComboBox.currentIndex() == self.RelationType.ManyToMany and
              len(self.featureLayers) == 1):
            self.cardinality = self.Cardinality.ManyToMany

        elif (self.mRelationTypeComboBox.currentIndex() == self.RelationType.ManyToOne and
              len(self.featureLayers) > 1):
            self.cardinality = self.Cardinality.ManyToOnePolymorphic

        elif (self.mRelationTypeComboBox.currentIndex() == self.RelationType.ManyToMany and
              len(self.featureLayers) > 1):
            self.cardinality = self.Cardinality.ManyToManyPolymorphic

        self.completeChanged.emit()

    def updateRelationsManyToOne(self):
        
        self.mManyToOneDocumentLayerLineEdit.setText(self.documentLayer.name())
        self.mManyToOneFeatureLayerLineEdit.setText(self.featureLayers[0].name())
        
        for relation in QgsProject.instance().relationManager().referencedRelations(self.documentLayer):
            if relation.referencingLayer() == self.featureLayers[0]:
                self.setInvalideRelations(False)
            else:
                self.setInvalideRelations(True, self.tr("At least one feature layer must be selected."))

    def isComplete(self):
        return self.valid

    def setInvalideRelations(self, invalid, errorText=""):
        self.mErrorLabel.setText(errorText)

        if self.valid == invalid:
            self.valid = not self.valid
            self.completeChanged.emit()

    @pyqtSlot()
    def relationTypeComboBoxCurrentIndexChanged(self, layerNames):
        pass


