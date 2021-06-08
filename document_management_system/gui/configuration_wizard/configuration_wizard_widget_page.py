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

DialogUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../../ui/configuration_wizard/configuration_wizard_widget_page.ui'))


class ConfigurationWizardWidgetPage(QWizardPage, DialogUi):

    def __init__(self, parent=None):
        """Constructor
        """
        self.valid = False

        super(ConfigurationWizardWidgetPage, self).__init__(parent=parent)
        self.setupUi(self)

        self.setTitle(self.tr("Widget configuration"))

    def isComplete(self):
        return self.valid


