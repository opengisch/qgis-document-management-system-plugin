# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Document Management System Plugin
# Copyright (C) 2021 Damiano Lombardi
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

from enum import Enum
import getpass
from qgis.PyQt.QtCore import Qt, QObject, QAbstractTableModel, QModelIndex, QDir, QMimeDatabase
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsRelation, QgsFeature, QgsExpression, QgsExpressionContext, QgsApplication

class Role(Enum):
    RelationRole = Qt.UserRole + 1
    RelationIdRole = Qt.UserRole + 2
    AggregateRole = Qt.UserRole + 3
    FieldRole = Qt.UserRole + 4


class DocumentModel(QAbstractTableModel):

    DocumentPathRole        = Qt.UserRole + 1
    DocumentNameRole        = Qt.UserRole + 2
    DocumentTypeRole        = Qt.UserRole + 3
    DocumentCreatedTimeRole = Qt.UserRole + 4
    DocumentCreatedUserRole = Qt.UserRole + 5
    DocumentIconRole        = Qt.UserRole + 6
    DocumentIsImageRole     = Qt.UserRole + 7

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

        return self._file_list[ index.row() ][ role ]

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if index.row() < 0 or index.row() >= self.rowCount(QModelIndex()):
            return False

        return False

    def roleNames(self):
        return {
            self.DocumentPathRole:        b'DocumentPath',
            self.DocumentNameRole:        b'DocumentName',
            self.DocumentTypeRole:        b'DocumentType',
            self.DocumentCreatedTimeRole: b'DocumentCreatedTime',
            self.DocumentCreatedUserRole: b'DocumentCreatedUser',
            self.DocumentIconRole:        b'DocumentIcon',
            self.DocumentIsImageRole:     b'DocumentIsImage'
        }

    def _updateData(self):
        self.beginResetModel()
        self._file_list = []

#        self._file_list.append("Valid relation: {} Valid feature: {}".format(self._relation.isValid(), self._feature.isValid()))

#        if self._relation.isValid() and self._feature.isValid():
#            request = self._relation.getRelatedFeaturesRequest(self._feature)
#            for f in self._relation.referencingLayer().getFeatures(request):
#                self._file_list.append("f")
                #self._related_features.append(f)

#            self._file_list.append("b")

#        exp = QgsExpression(self._document_path)
#        context = QgsExpressionContext()
#        expression_result = exp.evaluate(context)

        file_info_list = QDir("/home/domi").entryInfoList(['*'], QDir.Files)

        mime_database = QMimeDatabase()
        for file_info in file_info_list:
          mime_types = mime_database.mimeTypesForFileName(file_info.filePath())
          mime_type_name = str()
          icon_name = str()
          for mime_type in mime_types:
            mime_type_name = mime_type.name()
            if mime_type:
              icon_name = mime_type.iconName()
              break

          self._file_list.append({ self.DocumentPathRole:        file_info.filePath(),
                                   self.DocumentNameRole:        file_info.fileName(),
                                   self.DocumentTypeRole:        mime_type_name,
                                   self.DocumentCreatedTimeRole: file_info.created(),
                                   self.DocumentCreatedUserRole: getpass.getuser(),
                                   self.DocumentIconRole:        icon_name,
                                   self.DocumentIsImageRole:     mime_type_name.startswith("image/")
                                 })

        self.endResetModel()

