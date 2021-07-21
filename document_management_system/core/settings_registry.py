# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Document Management System Plugin
# Copyright (C) 2021 Damiano Lombardi
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

from qgis.core import QgsSettingsRegistry
from document_management_system.gui.document_relation_editor_feature_side_widget import DocumentRelationEditorWidget

class SettingsRegistry(QgsSettingsRegistry):

    def __init__(self):
        super().__init__()

        self.addSettingsEntry(DocumentRelationEditorWidget.settingsDefaultView)
        self.addSettingsEntry(DocumentRelationEditorWidget.settingsLastView)
