# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Ordered Relation Editor Plugin
# Copyright (C) 2020 Denis Rouzaud
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

from qgis.PyQt.QtCore import QObject
from qgis.gui import QgsAbstractRelationEditorWidgetFactory
from ordered_relation_editor.gui.ordered_relation_editor_widget import OrderedRelationEditorWidget
from ordered_relation_editor.gui.ordered_relation_editor_config_widget import OrderedRelationEditorConfigWidget

WIDGET_TYPE = "ordered_relation_editor"


class OrderedRelationEditorWidgetFactory(QgsAbstractRelationEditorWidgetFactory):
    def type(self):
        return WIDGET_TYPE

    def name(self):
        return "Ordered relation editor"

    def create(self, config, parent):
        return OrderedRelationEditorWidget(config, parent)

    def configWidget(self, relation, parent):
        return OrderedRelationEditorConfigWidget(relation, parent)