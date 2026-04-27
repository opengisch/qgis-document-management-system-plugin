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

from qgis.PyQt.QtGui import QImageReader


class PreviewImageProvider(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.ImageType.Image)

        # use an image reader to ensure image orientation and transforms are correctly handled
        self._imageReader = QImageReader()
        self._imageReader.setAutoTransform(True)

    def requestImage(self, id, size):
        self._imageReader.setFileName(id)
        image = self._imageReader.read()
        return image, image.size()

    @staticmethod
    def isMimeTypeSupported(filePath):
        imageReader = QImageReader()
        imageReader.setFileName(filePath)
        return imageReader.canRead()
