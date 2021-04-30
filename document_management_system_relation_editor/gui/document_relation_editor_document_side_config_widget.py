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
from qgis.core import QgsProject
from qgis.gui import QgsAbstractRelationEditorConfigWidget

WidgetUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../ui/document_relation_editor_document_side_config_widget.ui'))


class DocumentRelationEditorDocumentSideConfigWidget(QgsAbstractRelationEditorConfigWidget, WidgetUi):

    def __init__(self, relation, parent):
        super().__init__(relation, parent)
        self.setupUi(self)

        polymorphicRelations = QgsProject.instance().relationManager().polymorphicRelations()
        for polymorphicRelationId in polymorphicRelations:
            polymorphicRelationReferencingLayer = polymorphicRelations[polymorphicRelationId].referencingLayer()
            if (
                polymorphicRelationReferencingLayer.id() == relation.referencingLayer().id() or
                polymorphicRelationReferencingLayer.id() == relation.referencedLayer().id()
               ):
                self.mPolymorphicRelationComboBox.addItem(polymorphicRelations[polymorphicRelationId].name(), polymorphicRelationId)

    def config(self):
        return {
            'polymorphic_relation_enabled': self.mPolymorphicRelationGroupBox.isChecked(),
            'polymorphic_relation_id': self.mPolymorphicRelationComboBox.currentData(),
        }

    def setConfig(self, config):
        self.mPolymorphicRelationGroupBox.setChecked(config.get('polymorphic_relation_enabled'))

        polymorphicRelationId = config.get('polymorphic_relation_id')
        polymorphicRelation = QgsProject.instance().relationManager().polymorphicRelation(polymorphicRelationId)
        self.mPolymorphicRelationComboBox.setCurrentText(polymorphicRelation.name())
        pass

    def setNmRelation(self, nmRelation):

        super().setNmRelation(nmRelation)

        if nmRelation.isValid():
            self.mPolymorphicRelationGroupBox.setEnabled(False)
            self.mPolymorphicRelationGroupBox.setToolTip(self.tr('Polymorphic relation available only for cardinality "Many to one"'))
        else:
            self.mPolymorphicRelationGroupBox.setEnabled(True)
            self.mPolymorphicRelationGroupBox.setToolTip("")
