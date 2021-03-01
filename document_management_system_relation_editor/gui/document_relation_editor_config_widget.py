# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Ordered Relation Editor Plugin
# Copyright (C) 2020 Denis Rouzaud
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

import os
from qgis.PyQt.uic import loadUiType
from qgis.PyQt.QtWidgets import QGridLayout, QLabel
from qgis.gui import QgsAbstractRelationEditorConfigWidget

WidgetUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../ui/document_relation_editor_config_widget.ui'))


class DocumentRelationEditorConfigWidget(QgsAbstractRelationEditorConfigWidget, WidgetUi):

    def __init__(self, relation, parent):
        super().__init__(relation, parent)
        self.setupUi(self)
        self.relation = relation
        self.mDocumentPathExpressionWidget.setLayer(relation.referencingLayer())

    def config(self):
        return {
            'document_path': self.mDocumentPathExpressionWidget.currentField()[0]
        }

    def setConfig(self, config):
        self.mDocumentPathExpressionWidget.setField(config.get('document_path'))
