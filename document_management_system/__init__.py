# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Document Management System Plugin
# Copyright (C) 2021 Damiano Lombardi
#
# licensed under the terms of GNU GPL 2
#
# -----------------------------------------------------------


def classFactory(iface):
    """Load plugin.
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from document_management_system.core.document_management_system_relation_editor_plugin import (
        DocumentManagementSystemRelationEditorPlugin,
    )

    return DocumentManagementSystemRelationEditorPlugin(iface)
