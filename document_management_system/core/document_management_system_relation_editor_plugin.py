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
from qgis.PyQt.QtCore import QCoreApplication, QTranslator, QObject, QLocale, QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsApplication
from qgis.gui import (
    QgisInterface,
    QgsGui
)

from document_management_system.core.settings_registry import SettingsRegistry
from document_management_system.gui.relation_editor_feature_side_widget_factory import RelationEditorFeatureSideWidgetFactory
from document_management_system.gui.relation_editor_document_side_widget_factory import RelationEditorDocumentSideWidgetFactory

DEBUG = True

class DocumentManagementSystemRelationEditorPlugin(QObject):

    plugin_name = "&Document Management System Relation Editor"

    def __init__(self, interface: QgisInterface):
        QObject.__init__(self)
        self.interface = interface

        # initialize translation
        qgis_locale = QLocale(QSettings().value('locale/userLocale'))
        locale_path = os.path.join(os.path.dirname(__file__), 'i18n')
        self.translator = QTranslator()
        self.translator.load(qgis_locale, 'actions_for_relations', '_', locale_path)
        QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.MENU_ITEM_NAME = self.tr('&Document management system')

        # Plugin settings
        self.settingsRegistry = SettingsRegistry()
        QgsApplication.settingsRegistryCore().addSubRegistry(self.settingsRegistry)

    def initGui(self):        
        QgsGui.relationWidgetRegistry().addRelationWidget(RelationEditorFeatureSideWidgetFactory())
        QgsGui.relationWidgetRegistry().addRelationWidget(RelationEditorDocumentSideWidgetFactory())

    def unload(self):
        # Removes the plugin menu item
        for action in self.actions:
            self.interface.removePluginMenu(self.MENU_ITEM_NAME,
                                            action)

        QgsGui.relationWidgetRegistry().removeRelationWidget(RelationEditorFeatureSideWidgetFactory.type())
        QgsGui.relationWidgetRegistry().removeRelationWidget(RelationEditorDocumentSideWidgetFactory.type())
