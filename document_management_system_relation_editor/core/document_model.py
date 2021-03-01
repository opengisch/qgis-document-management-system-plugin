# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Ordered Relation Editor Plugin
# Copyright (C) 2020 Denis Rouzaud
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

from enum import Enum
from qgis.PyQt.QtCore import Qt, QObject, QAbstractTableModel, QModelIndex, QDir
from qgis.core import QgsRelation, QgsFeature, QgsExpression, QgsExpressionContext

class Role(Enum):
    RelationRole = Qt.UserRole + 1
    RelationIdRole = Qt.UserRole + 2
    AggregateRole = Qt.UserRole + 3
    FieldRole = Qt.UserRole + 4


class DocumentModel(QAbstractTableModel):

    DocumentPathRole = Qt.UserRole + 1

    def __init__(self, parent: QObject = None):
        super(DocumentModel, self).__init__(parent)
        self._relation = QgsRelation()
        self._document_path = str()
        self._feature = QgsFeature()
        self._file_list = []

    def init(self, relation: QgsRelation, feature: QgsFeature, document_path: str):
        self._relation = relation
        self._document_path = document_path
        self._feature = feature
        self._updateData()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._file_list)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 1

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        return flags

    def data(self, index: QModelIndex, role: int = ...):
        if index.row() < 0 or index.row() >= self.rowCount(QModelIndex()):
            return None

        if role == self.DocumentPathRole:
            return self._file_list[ index.row() ]

        return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if index.row() < 0 or index.row() >= self.rowCount(QModelIndex()):
            return False

        return False

    def roleNames(self):
        return {
            self.DocumentPathRole: b'DocumentPath'
        }

    def _updateData(self):
        self.beginResetModel()
        self._file_list = []

        exp = QgsExpression(self._document_path)
        context = QgsExpressionContext()

        #qDir = QDir(exp.evaluate(context), ['*'], QDir.Files)
        qDir = QDir('/home/domi')

        self._file_list = qDir.entryList(['*'], QDir.Files)

        self.endResetModel()




