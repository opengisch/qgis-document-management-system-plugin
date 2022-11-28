# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Document Management System Plugin
# Copyright (C) 2021 Damiano Lombardi
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsDataSourceUri


class PluginHelper(object):

    PLUGIN_SLUG = "DMSRelationEditor"

    @staticmethod
    def tr(message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate(PluginHelper.PLUGIN_SLUG, message)

    @staticmethod
    def removeLayerIdOrName(layerUri):
        layerUriStripped = str()
        for toRemove in ["|layername=", "|layerid="]:
            pos = layerUri.find(toRemove)
            if pos >= 0:
                end = layerUri.find("|", pos + 1)
                if end >= 0:
                    layerUriStripped = layerUri[pos:end]
                else:
                    layerUriStripped = layerUri[0:pos]

        return layerUriStripped

    @staticmethod
    def connectionString(layerUri):
        connString = QgsDataSourceUri(layerUri).connectionInfo(False)
        # In the case of a OGR datasource, connectionInfo() will return an empty
        # string. In that case, use the layer->source() itself, and strip any
        # reference to layers from it.
        if len(connString) == 0:
            connString = PluginHelper.removeLayerIdOrName(layerUri)

        return connString
