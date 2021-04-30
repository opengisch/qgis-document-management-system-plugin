# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Document Management System Plugin
# Copyright (C) 2021 Damiano Lombardi
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

from qgis.gui import QgsAbstractRelationEditorWidgetFactory
from document_management_system_relation_editor.gui.document_relation_editor_document_side_widget import DocumentRelationEditorDocumentSideWidget
from document_management_system_relation_editor.gui.document_relation_editor_document_side_config_widget import DocumentRelationEditorDocumentSideConfigWidget


class DocumentRelationEditorDocumentSideWidgetFactory(QgsAbstractRelationEditorWidgetFactory):

    @staticmethod
    def type():
        return "document_relation_editor_document_side"

    def name(self):
        return "Document relation editor (Document side)"

    def create(self, config, parent):
        return DocumentRelationEditorDocumentSideWidget(config, parent)

    def configWidget(self, relation, parent):
        return DocumentRelationEditorDocumentSideConfigWidget(relation, parent)
