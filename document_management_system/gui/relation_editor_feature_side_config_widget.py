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
from qgis.PyQt.uic import loadUiType
from qgis.gui import QgsAbstractRelationEditorConfigWidget

WidgetUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), "../ui/relation_editor_feature_side_config_widget.ui"))


class RelationEditorFeatureSideConfigWidget(QgsAbstractRelationEditorConfigWidget, WidgetUi):
    def __init__(self, relation, parent):
        super().__init__(relation, parent)
        self.setupUi(self)
        self.mDocumentsPathExpressionWidget.setLayer(relation.referencingLayer())
        self.mDocumentFilenameExpressionWidget.setLayer(relation.referencingLayer())

    def config(self):
        return {
            "documents_path": self.mDocumentsPathExpressionWidget.currentField()[0],
            "document_filename": self.mDocumentFilenameExpressionWidget.currentField()[0],
        }

    def setConfig(self, config):
        self.mDocumentsPathExpressionWidget.setField(config.get("documents_path"))
        self.mDocumentFilenameExpressionWidget.setField(config.get("document_filename"))

    def setNmRelation(self, nmRelation):

        super().setNmRelation(nmRelation)

        layer = self.relation().referencingLayer()
        if nmRelation.isValid():
            layer = nmRelation.referencedLayer()

        self.mDocumentsPathExpressionWidget.setLayer(layer)
        self.mDocumentFilenameExpressionWidget.setLayer(layer)
