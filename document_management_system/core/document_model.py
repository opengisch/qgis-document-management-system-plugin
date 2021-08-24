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
from qgis.PyQt.QtCore import (
    Qt,
    QObject,
    QAbstractTableModel,
    QModelIndex,
    QFileInfo,
    QDir,
    QSysInfo,
    QUrl
)
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsRelation, QgsFeature, QgsExpression, QgsExpressionContext, QgsExpressionContextUtils, QgsFeatureRequest
from document_management_system.core.preview_image_provider import PreviewImageProvider

class Role(Enum):
    RelationRole = Qt.UserRole + 1
    RelationIdRole = Qt.UserRole + 2
    AggregateRole = Qt.UserRole + 3
    FieldRole = Qt.UserRole + 4


class DocumentModel(QAbstractTableModel):

    DocumentIdRole      = Qt.UserRole + 1
    DocumentPathRole    = Qt.UserRole + 2
    DocumentNameRole    = Qt.UserRole + 3
    DocumentExistsRole  = Qt.UserRole + 4
    DocumentToolTipRole = Qt.UserRole + 5
    DocumentIsImageRole = Qt.UserRole + 6

    def __init__(self, parent: QObject = None):
        super(DocumentModel, self).__init__(parent)
        self._relation = QgsRelation()
        self._nmRelation = QgsRelation()
        self._documents_path = str()
        self._document_filename = str()
        self._feature = QgsFeature()
        self._document_list = []

    def init(self,
             relation: QgsRelation,
             nmRelation: QgsRelation,
             feature: QgsFeature,
             documents_path: str,
             document_filename: str):
        self._relation = relation
        self._nmRelation = nmRelation
        self._documents_path = documents_path
        self._document_filename = document_filename
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

        return self._document_list[index.row()][role]

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if index.row() < 0 or index.row() >= self.rowCount(QModelIndex()):
            return False

        return False

    def roleNames(self):
        return {
            self.DocumentIdRole:      b'DocumentId',
            self.DocumentPathRole:    b'DocumentPath',
            self.DocumentNameRole:    b'DocumentName',
            self.DocumentExistsRole:  b'DocumentExists',
            self.DocumentToolTipRole: b'DocumentToolTip',
            self.DocumentIsImageRole: b'DocumentIsImage'
        }

    def reloadData(self):
        self.beginResetModel()
        self._document_list = []

        if self._relation.isValid() is False or self._feature.isValid() is False:
            self.endResetModel()
            return

        feature_list = []
        layer = self._relation.referencingLayer()
        request = self._relation.getRelatedFeaturesRequest(self._feature)
        for feature in layer.getFeatures(request):
            feature_list.append(feature)

        if self._nmRelation.isValid():
            filters = []
            for joinTableFeature in feature_list:
                referencedFeatureRequest = self._nmRelation.getReferencedFeatureRequest(joinTableFeature)
                filterExpression = referencedFeatureRequest.filterExpression()
                filters.append("(" + filterExpression.expression() + ")")

            nmRequest = QgsFeatureRequest()
            nmRequest.setFilterExpression(" OR ".join(filters))

            feature_list = []
            layer = self._nmRelation.referencedLayer()
            for documentFeature in layer.getFeatures(nmRequest):
                feature_list.append(documentFeature)

        for documentFeature in feature_list:
            documents_path = str()
            if self._documents_path:
                exp = QgsExpression(self._documents_path)
                context = QgsExpressionContext()
                context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
                context.setFeature(documentFeature)
                documents_path = exp.evaluate(context)

            document_filename = str()
            if self._document_filename:
                exp = QgsExpression(self._document_filename)
                context = QgsExpressionContext()
                context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
                context.setFeature(documentFeature)
                document_filename = exp.evaluate(context)
            file_info = QFileInfo(QDir(str(documents_path)),
                                  str(document_filename))

            # ToolTip
            toolTipList = []
            toolTipList.append("<ul>")
            for field in documentFeature.fields():
                index = documentFeature.fields().indexFromName(field.name())
                toolTipList.append("<li><strong>{0}</strong>: {1}</li>".format(field.displayName(),
                                                                               documentFeature[index]))
            toolTipList.append("</ul>")

            self._document_list.append({
              self.DocumentIdRole:          documentFeature.id(),
              self.DocumentPathRole:        file_info.filePath(),
              self.DocumentNameRole:        file_info.fileName(),
              self.DocumentExistsRole:      file_info.exists(),
              self.DocumentToolTipRole:     "".join(toolTipList),
              self.DocumentIsImageRole:     PreviewImageProvider.isMimeTypeSupported(file_info.filePath())
              })

        self.endResetModel()
