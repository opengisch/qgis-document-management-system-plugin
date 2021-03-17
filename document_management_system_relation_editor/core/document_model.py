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
from qgis.PyQt.QtCore import Qt, QObject, QAbstractTableModel, QModelIndex, QFileInfo, QMimeDatabase
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsRelation, QgsFeature, QgsExpression, QgsExpressionContext, QgsApplication, QgsExpressionContextUtils, QgsFeatureRequest

class Role(Enum):
    RelationRole = Qt.UserRole + 1
    RelationIdRole = Qt.UserRole + 2
    AggregateRole = Qt.UserRole + 3
    FieldRole = Qt.UserRole + 4


class DocumentModel(QAbstractTableModel):

    DocumentIdRole          = Qt.UserRole + 1
    DocumentPathRole        = Qt.UserRole + 2
    DocumentNameRole        = Qt.UserRole + 3
    DocumentExistsRole      = Qt.UserRole + 4
    DocumentTypeRole        = Qt.UserRole + 5
    DocumentCreatedTimeRole = Qt.UserRole + 6
    DocumentCreatedUserRole = Qt.UserRole + 7
    DocumentIconRole        = Qt.UserRole + 8
    DocumentIsImageRole     = Qt.UserRole + 9

    def __init__(self, parent: QObject = None):
        super(DocumentModel, self).__init__(parent)
        self._relation = QgsRelation()
        self._nmRelation = QgsRelation()
        self._document_path = str()
        self._feature = QgsFeature()
        self._document_list = []

    def init(self, relation: QgsRelation, nmRelation: QgsRelation, feature: QgsFeature, document_path: str):
        self._relation = relation
        self._nmRelation = nmRelation
        self._document_path = document_path
        self._feature = feature
        self.reloadData()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._document_list)

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

        return self._document_list[ index.row() ][ role ]

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if index.row() < 0 or index.row() >= self.rowCount(QModelIndex()):
            return False

        return False

    def roleNames(self):
        return {
            self.DocumentIdRole:          b'DocumentId',
            self.DocumentPathRole:        b'DocumentPath',
            self.DocumentNameRole:        b'DocumentName',
            self.DocumentExistsRole:      b'DocumentExists',
            self.DocumentTypeRole:        b'DocumentType',
            self.DocumentCreatedTimeRole: b'DocumentCreatedTime',
            self.DocumentCreatedUserRole: b'DocumentCreatedUser',
            self.DocumentIconRole:        b'DocumentIcon',
            self.DocumentIsImageRole:     b'DocumentIsImage'
        }

    def reloadData(self):
        self.beginResetModel()
        self._document_list = []

        if self._relation.isValid() == False or self._feature.isValid() == False:
            self.endResetModel()
            return

        feature_list = []
        layer = self._relation.referencingLayer()
        request = self._relation.getRelatedFeaturesRequest(self._feature)
        for feature in layer.getFeatures(request):
            feature_list.append(feature)

        if self._nmRelation:
            filters = []
            for feature in feature_list:
                referencedFeatureRequest = self._nmRelation.getReferencedFeatureRequest( feature )
                filterExpression = referencedFeatureRequest.filterExpression()
                filters.append("(" + filterExpression.expression() + ")")

            nmRequest = QgsFeatureRequest()
            nmRequest.setFilterExpression(" OR ".join(filters))

            feature_list = []
            layer = self._nmRelation.referencedLayer()
            for feature in layer.getFeatures(nmRequest):
                feature_list.append(feature)

        mime_database = QMimeDatabase()
        for feature in feature_list:
            print("n:m feature", feature.id(), "path:", feature["path"])
            exp = QgsExpression(self._document_path)
            context = QgsExpressionContext()
            context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
            context.setFeature(feature)
            expression_result = exp.evaluate(context)
            file_info = QFileInfo(expression_result)

            mime_types = mime_database.mimeTypesForFileName(file_info.filePath())
            mime_type_name = str()
            icon_name = str()
            for mime_type in mime_types:
                if mime_type:
                    mime_type_name = mime_type.name()
                    icon_name = mime_type.iconName()
                    break

            self._document_list.append({ self.DocumentIdRole:          feature.id(),
                                         self.DocumentPathRole:        file_info.filePath(),
                                         self.DocumentNameRole:        file_info.fileName(),
                                         self.DocumentExistsRole:      file_info.exists(),
                                         self.DocumentTypeRole:        mime_type_name,
                                         self.DocumentCreatedTimeRole: file_info.created(),
                                         self.DocumentCreatedUserRole: getpass.getuser(),
                                         self.DocumentIconRole:        icon_name,
                                         self.DocumentIsImageRole:     mime_type_name.startswith("image/")
                                       })

        self.endResetModel()

