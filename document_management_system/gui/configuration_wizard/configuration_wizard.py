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
    QWizard,
    QWizardPage
)
from qgis.core import QgsProject
from qgis.gui import QgsCheckableComboBox

from qgis.PyQt.uic import loadUiType

from document_management_system.gui.configuration_wizard.configuration_wizard_layer_page import ConfigurationWizardLayerPage
from document_management_system.gui.configuration_wizard.configuration_wizard_relation_page import ConfigurationWizardRelationPage
from document_management_system.gui.configuration_wizard.configuration_wizard_widget_page import ConfigurationWizardWidgetPage

class ConfigurationWizard(QWizard):

    def __init__(self, interface, parent=None):
        """Constructor.
        """
        super(ConfigurationWizard, self).__init__(parent=parent)
        self.interface = interface

        self.layerPage = ConfigurationWizardLayerPage(self)
        self.addPage(self.layerPage)
        
        self.relationPage = ConfigurationWizardRelationPage(self.layerPage, self)
        self.addPage(self.relationPage)
        
        self.widgetPage = ConfigurationWizardWidgetPage(self)
        self.addPage(self.widgetPage)
