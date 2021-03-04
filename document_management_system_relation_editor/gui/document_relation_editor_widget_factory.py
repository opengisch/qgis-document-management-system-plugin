# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Document Management System Plugin
# Copyright (C) 2021 Damiano Lombardi
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

from qgis.PyQt.QtCore import QObject
from qgis.gui import QgsAbstractRelationEditorWidgetFactory
from document_management_system_relation_editor.gui.document_relation_editor_widget import DocumentRelationEditorWidget
from document_management_system_relation_editor.gui.document_relation_editor_config_widget import DocumentRelationEditorConfigWidget

WIDGET_TYPE = "document_relation_editor"


class DocumentRelationEditorWidgetFactory(QgsAbstractRelationEditorWidgetFactory):
    def type(self):
        return WIDGET_TYPE

    def name(self):
        return "Document relation editor"

    def create(self, config, parent):
        return DocumentRelationEditorWidget(config, parent)

    def configWidget(self, relation, parent):
        return DocumentRelationEditorConfigWidget(relation, parent)
