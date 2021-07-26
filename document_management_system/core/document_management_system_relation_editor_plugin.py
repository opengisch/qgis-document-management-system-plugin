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
from document_management_system.gui.configuration_wizard.configuration_wizard import ConfigurationWizard

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

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.interface.addPluginToMenu(
                self.MENU_ITEM_NAME,
                action)

        self.actions.append(action)

        return action

    def initGui(self):

        #self.add_action(str(),
        #                text=self.tr('Configuration &wizard'),
        #                callback=self.showConfigurationWizard,
        #                parent=self.interface.mainWindow(),
        #                add_to_toolbar=False)
        
        QgsGui.relationWidgetRegistry().addRelationWidget(RelationEditorFeatureSideWidgetFactory())
        QgsGui.relationWidgetRegistry().addRelationWidget(RelationEditorDocumentSideWidgetFactory())

    def unload(self):

        # Removes the plugin menu item
        for action in self.actions:
            self.interface.removePluginMenu(self.MENU_ITEM_NAME,
                                            action)

        QgsGui.relationWidgetRegistry().removeRelationWidget(RelationEditorFeatureSideWidgetFactory.type())
        QgsGui.relationWidgetRegistry().removeRelationWidget(RelationEditorDocumentSideWidgetFactory.type())

        #if qgisversion > 3.20:
        #    QgsApplication.settingsRegistryCore().removeSubRegistry(self.settingsRegistry)

    def showConfigurationWizard(self):
        """
        Show configuration wizard
        """
        configurationWizard = ConfigurationWizard(self.interface)
        configurationWizard.exec_()
