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
from qgis.gui import QgisInterface, QgsGui
from document_management_system_relation_editor.gui.document_relation_editor_widget_factory import DocumentRelationEditorWidgetFactory, WIDGET_TYPE

DEBUG = True


class DocumentManagementSystemRelationEditorPlugin(QObject):

    plugin_name = "&Document Management System Relation Editor"

    def __init__(self, iface: QgisInterface):
        QObject.__init__(self)
        self.iface = iface

        # initialize translation
        qgis_locale = QLocale(QSettings().value('locale/userLocale'))
        locale_path = os.path.join(os.path.dirname(__file__), 'i18n')
        self.translator = QTranslator()
        self.translator.load(qgis_locale, 'actions_for_relations', '_', locale_path)
        QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        QgsGui.relationWidgetRegistry().addRelationWidget(DocumentRelationEditorWidgetFactory())

    def unload(self):
        QgsGui.relationWidgetRegistry().removeRelationWidget(WIDGET_TYPE)
