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
from document_management_system.gui.relation_editor_feature_side_widget import RelationEditorWidget
from document_management_system.gui.relation_editor_feature_side_config_widget import RelationEditorConfigWidget


class RelationEditorWidgetFactory(QgsAbstractRelationEditorWidgetFactory):

    @staticmethod
    def type():
        return "document_relation_editor_feature_side"

    def name(self):
        return "Document relation editor (Feature side)"

    def create(self, config, parent):
        return RelationEditorWidget(config, parent)

    def configWidget(self, relation, parent):
        return RelationEditorConfigWidget(relation, parent)
