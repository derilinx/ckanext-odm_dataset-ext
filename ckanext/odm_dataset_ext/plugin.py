# encoding: utf-8
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class Odm_Dataset_ExtPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)

    '''
    def _modify_package_schema(self, schema):
        schema.update({
            'odm_date_created': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')]
        })
        return schema
    '''

    def create_package_schema(self):
        schema = super(Odm_Dataset_ExtPlugin, self).create_package_schema()
        #schema = self._modify_package_schema(schema)
        schema.update({
            'CI_citation_title': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_abstract': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_topicCategory': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_keywords': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'CI_citation_identAuth': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_language': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_constraints': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_legalConstraints': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'CI_ResponsibleParty': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_format_version': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'CI_Citation_date': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_metadata_dateStamp': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'CI_citation_lastRevision': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'CI_citation_updatefreq': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'Ex_TemporalExtent_startdate': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'Ex_TemporalExtent_enddate': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'Ex_geoname': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'EX_GeographicBoundingBox_west': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'EX_GeographicBoundingBox_east': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'EX_GeographicBoundingBox_south': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'EX_GeographicBoundingBox_north': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_DataIdentification_spatialResolution': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_spatialreferencesystem': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'DQ_PositionalAccuracy': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'DQ_QuantitativeAttribute': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'DQ_logicalConsistency': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'DQ_completeness': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'LI_ProcessStep': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'LI_Lineage': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'CI_ResponsibleParty_contact': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_metadata_contact': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_scopeDescription_attributes': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')]

            })

        return schema

    def update_package_schema(self):
        schema = super(Odm_Dataset_ExtPlugin, self).update_package_schema()
        #schema = self._modify_package_schema(schema)
        schema.update({
            'CI_citation_title': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_abstract': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_topicCategory': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_keywords': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'CI_citation_identAuth': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_language': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_constraints': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_legalConstraints': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'CI_ResponsibleParty': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_format_version': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'CI_Citation_date': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_metadata_dateStamp': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'CI_citation_lastRevision': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'CI_citation_updatefreq': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'Ex_TemporalExtent_startdate': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'Ex_TemporalExtent_enddate': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'Ex_geoname': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'EX_GeographicBoundingBox_west': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'EX_GeographicBoundingBox_east': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'EX_GeographicBoundingBox_south': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'EX_GeographicBoundingBox_north': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_DataIdentification_spatialResolution': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_spatialreferencesystem': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'DQ_PositionalAccuracy': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'DQ_QuantitativeAttribute': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'DQ_logicalConsistency': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'DQ_completeness': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'LI_ProcessStep': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'LI_Lineage': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'CI_ResponsibleParty_contact': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_metadata_contact': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')],
            'MD_scopeDescription_attributes': [toolkit.get_converter('convert_to_extras'), toolkit.get_validator('ignore_missing')]
        })

        return schema

    def show_package_schema(self):
        schema = super(Odm_Dataset_ExtPlugin, self).show_package_schema()
        #schema = self._modify_package_schema(schema)
        schema.update({
            'CI_citation_title': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_abstract': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_topicCategory': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_keywords': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'CI_citation_identAuth': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_language': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'MD_constraints': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'MD_legalConstraints': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'CI_ResponsibleParty': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'MD_format_version': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'CI_Citation_date': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'MD_metadata_dateStamp': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'CI_citation_lastRevision': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'CI_citation_updatefreq': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'Ex_TemporalExtent_startdate': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'Ex_TemporalExtent_enddate': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'Ex_geoname': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'EX_GeographicBoundingBox_west': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'EX_GeographicBoundingBox_east': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'EX_GeographicBoundingBox_south': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'EX_GeographicBoundingBox_north': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'MD_DataIdentification_spatialResolution': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'MD_dataidentification_spatialreferencesystem': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'DQ_PositionalAccuracy': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'DQ_QuantitativeAttribute': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'DQ_logicalConsistency': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'DQ_completeness': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'LI_ProcessStep': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'LI_Lineage': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'CI_ResponsibleParty_contact': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'MD_metadata_contact': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')],
            'MD_scopeDescription_attributes': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')]
        })
        return schema


    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'odm_dataset_ext')

    #IDatasetForm
    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    #IDatasetForm
    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []



