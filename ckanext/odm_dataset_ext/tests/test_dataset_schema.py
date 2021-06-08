from ckanext.odm_dataset_ext.tests import odm_dataset_factories
from ckan.tests import factories
import ckan.tests.helpers as helpers
import pytest


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestOdmDatasetSchema:
    def setup(self):
        pass

    def test_default_package_create(self):

        pkg = odm_dataset_factories.OdmDataset().create(
            name="test_default_dataset",
            title_translated={'en': "test default dataset"}
        )

        assert pkg['type'] == 'dataset'

    def test_odm_dataset_schema(self):
        """
        Criteria:
            Alteast ODM dataset specific keys should exist other than core CKAN
        :return:
        """
        pkg = odm_dataset_factories.OdmDataset().create(
            name="test_schema_dataset",
            title_translated={'en': "test schema dataset"},
            MD_DataIdentification_language=["en"],
            CI_Citation_date="2020-08-28",
            odm_spatial_range=["mm"],
            MD_DataIdentification_spatialResolution=""

        )

        assert 'notes_translated' in pkg
        assert 'taxonomy' in pkg
        assert 'MD_DataIdentification_language' in pkg
        assert 'CI_Citation_date' in pkg
        assert 'odm_spatial_range' in pkg
        assert 'MD_DataIdentification_spatialResolution' in pkg

    def test_odm_dataset_resource_schema(self):

        pkg = odm_dataset_factories.OdmDataset().create(
            name="test_schema_dataset",
            title_translated={'en': "test schema dataset"}
        )
        assert pkg['id']
        resource = factories.Resource(format="CSV", package_id=pkg.get('id', ''))
        assert resource['format'].lower() == "csv"

        resource = factories.Resource(
            format="WMS",
            package_id=pkg.get('id', ''),
            odm_external_geoserver_url="https://geoserver.com/",
            odm_geoserver_layer_name="test"
        )
        assert 'odm_geoserver_layer_name' in resource
        assert 'odm_external_geoserver_url' in resource