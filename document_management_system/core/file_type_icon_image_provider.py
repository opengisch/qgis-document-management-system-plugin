# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Document Management System Plugin
# Copyright (C) 2021 Damiano Lombardi
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

try:
    from qgis.PyQt.QtQuick import QQuickImageProvider
except ImportError:
    from PyQt6.QtQuick import QQuickImageProvider

from qgis.PyQt.QtCore import QFileInfo
from qgis.PyQt.QtWidgets import QFileIconProvider


class FileTypeIconImageProvider(QQuickImageProvider):
    def __init__(self, maxSize):
        super().__init__(QQuickImageProvider.ImageType.Pixmap)

        self._maxSize = maxSize
        self._provider = QFileIconProvider()

    def requestPixmap(self, id, size):
        qIcon = self._provider.icon(QFileInfo(id))
        pixmap = qIcon.pixmap(self._maxSize, self._maxSize)
        return pixmap, pixmap.size()
