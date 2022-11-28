from qgis.testing import unittest, start_app
from document_management_system.gui.relation_editor_document_side_widget_factory import (
    RelationEditorDocumentSideWidgetFactory,
)

start_app()


class TestRelationEditorDocumentSideWidgetFactory(unittest.TestCase):
    def test_instantiate(self):
        RelationEditorDocumentSideWidgetFactory()
