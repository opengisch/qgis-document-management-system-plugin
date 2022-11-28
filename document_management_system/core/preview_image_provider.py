# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Document Management System Plugin
# Copyright (C) 2021 Damiano Lombardi
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

from PyQt5.QtQuick import QQuickImageProvider
from qgis.PyQt.QtCore import QMimeDatabase
from qgis.PyQt.QtGui import QImageReader


class PreviewImageProvider(QQuickImageProvider):

    mime_database = QMimeDatabase()

    def __init__(self):
        super().__init__(QQuickImageProvider.Image)

        # use an image reader to ensure image orientation and transforms are correctly handled
        self._imageReader = QImageReader()
        self._imageReader.setAutoTransform(True)

        print("supportedMimeTypes {}".format(self._imageReader.supportedMimeTypes()))

    def requestImage(self, id, size):
        self._imageReader.setFileName(id)
        image = self._imageReader.read()
        return image, image.size()

    @staticmethod
    def isMimeTypeSupported(filePath):
        mime_type_name = str()
        for mime_type in PreviewImageProvider.mime_database.mimeTypesForFileName(filePath):
            if mime_type:
                mime_type_name = mime_type.name()
                break

        return mime_type_name in QImageReader().supportedMimeTypes()
