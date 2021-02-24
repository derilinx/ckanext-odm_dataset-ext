import pytest
from ckanext.odm_dataset_ext import plugin
from ckanext.odm_dataset_ext.tests import odm_dataset_factories
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from ckan import model
import ckan.tests.helpers as helpers
from ckan.tests import factories
from ckan.logic import _actions
import mock


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestOdm_Dataset_ExtPlugin:

    def setup(self):
        self.instance = plugin.Odm_Dataset_ExtPlugin()

    def test_plugin_setup(self):

        assert len(self.instance.get_helpers()) > 0
        assert len(self.instance.get_validators()) > 0
        assert len(self.instance.get_actions()) > 0 and 'package_search' not in self.instance.get_actions()

    def test_before_index(self):

        pkg_dict = odm_dataset_factories.OdmDataset().create()

        self.instance.before_index(pkg_dict)
        assert 'CI_ResponsibleParty' in pkg_dict
        assert 'CI_Citation_title' in pkg_dict
        assert 'odm_language_list' in pkg_dict
        assert 'extras_odm_keywords' in pkg_dict
        assert 'extras_odm_keywords_text' in pkg_dict
        assert 'taxonomy' in pkg_dict

    def test_before_index_normalization(self):

        pkg_dict = {
            "MD_Constraints": '{"en": "test2", "km": "test3"}',
            "extras_DQ_PositionalAccuracy": '{"en": "test2", "km": "test3"}'
        }

        pkg_dict = self.instance.before_index(pkg_dict)

        assert "MD_Constraints_en" in pkg_dict
        assert "MD_Constraints_km" in pkg_dict
        assert "extras_DQ_PositionalAccuracy_en" in pkg_dict
        assert "extras_DQ_PositionalAccuracy_km" in pkg_dict
        assert "MD_Constraints" not in pkg_dict
        assert "extras_DQ_PositionalAccuracy" not in pkg_dict

    def test_after_create_is_issue_created(self, monkeypatch):

        context = {
            'user': None,
            'model': model
        }
        pkg_dict = odm_dataset_factories.OdmDataset().create()

        def issue_create(context, data_dict):
            # Patch the issue create and see if the module is called
            assert "title" in data_dict
            assert "description" in data_dict
            assert "dataset_id" in data_dict
            return True

        monkeypatch.setitem(_actions, 'issue_create', issue_create)

        assert pkg_dict.get('type', '') == "dataset"
        assert toolkit.asbool(toolkit.config.get("ckanext.issues.review_system", False))
        self.instance.after_create(context, pkg_dict)

    def test_after_show(self):

        pkg_dict = odm_dataset_factories.OdmDataset().create()

        assert "CI_ResponsibleParty" in pkg_dict
        assert "CI_Citation_title" in pkg_dict
        assert "MD_DataIdentification_topicCategory" in pkg_dict
        assert "EX_GeographicBoundingBox_north" in pkg_dict
        assert "EX_GeographicBoundingBox_east" in pkg_dict
        assert "EX_GeographicBoundingBox_south" in pkg_dict
        assert "EX_GeographicBoundingBox_west" in pkg_dict
        assert "MD_DataIdentification_spatialResolution" in pkg_dict


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestOdm_Dataset_Resource:

    def setup(self):
        pass

    def test_wms_bounding_box_resource_to_package(self, monkeypatch):

        context = {
            'user': None,
            'model': model
        }

        def vectorstorer_spatial_metadata_for_resource(context, data_dict):
            return {
                'crs': ("epsg:4326", ),
                "EX_GeographicBoundingBox": {
                    "northBoundLatitude": 1,
                    "southBoundLatitude": 1,
                    "westBoundLongitude": 1,
                    "eastBoundLongitude": 1
                }
            }

        monkeypatch.setitem(_actions,
                            'vectorstorer_spatial_metadata_for_resource',
                            vectorstorer_spatial_metadata_for_resource)
        pkg_dict = odm_dataset_factories.OdmDataset().create()
        resource = factories.Resource(format="WMS", package_id=pkg_dict.get('id', ''))
        pkg_dict = toolkit.get_action('package_show')(context, {'id': resource['package_id']})

        # Bounding box should be float
        assert pkg_dict.get('EX_GeographicBoundingBox_north', '') == '1.0'
        assert pkg_dict.get('EX_GeographicBoundingBox_south', '') == '1.0'
        assert pkg_dict.get('EX_GeographicBoundingBox_west', '') == '1.0'
        assert pkg_dict.get('EX_GeographicBoundingBox_east', '') == '1.0'
