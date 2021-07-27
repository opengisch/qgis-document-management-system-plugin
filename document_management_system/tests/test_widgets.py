
from qgis.testing import unittest, start_app
from document_management_system.gui.relation_editor_feature_side_widget_factory import RelationEditorFeatureSideWidgetFactory

start_app()

class TestRelationEditorFeaturesSideWidgetFactory(unittest.TestCase):

    def test_instantiate(self):
        RelationEditorFeatureSideWidgetFactory()

