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
    # wait on https://github.com/qgis/QGIS/pull/65874
    # from qgis.PyQt.QtQuick import QQuickImageProvider
    from PyQt6.QtQuick import QQuickImageProvider
except ImportError:
    # QtQuick was not monkey patched in QGIS 3.x
    from PyQt5.QtQuick import QQuickImageProvider

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
