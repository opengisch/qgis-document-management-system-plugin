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
    QDialog,
    QDialogButtonBox,
    QPushButton
)
from qgis.core import QgsProject
from qgis.PyQt.uic import loadUiType

DialogUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../../ui/configuration_wizard/configuration_wizard.ui'))


class ConfigurationWizard(QDialog, DialogUi):

    def __init__(self, interface, parent=None):
        """Constructor.
        """
        super(ConfigurationWizard, self).__init__(parent=parent)
        self.setupUi(self)
        self.interface = interface

        mapLayers = QgsProject.instance().mapLayers(True)
        for layerId, layer in mapLayers.items():
            self.mFeatureLayersComboBox.addItem(layer.name(), layerId)
