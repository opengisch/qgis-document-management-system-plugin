from qgis.testing import unittest, start_app
from document_management_system.gui.relation_editor_document_side_widget_factory import (
    RelationEditorDocumentSideWidgetFactory,
)
from document_management_system.core.preview_image_provider import PreviewImageProvider

start_app()


class TestRelationEditorDocumentSideWidgetFactory(unittest.TestCase):
    def test_instantiate(self):
        RelationEditorDocumentSideWidgetFactory()


class TestPreviewImageProvider(unittest.TestCase):
    def test_instantiate(self):
        PreviewImageProvider()
