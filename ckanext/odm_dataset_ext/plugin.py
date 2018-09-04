# encoding: utf-8
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckan
import pylons
import logging
import ckan.lib.helpers as h
from beaker.middleware import SessionMiddleware
import sys
import os
from pylons import config
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import odm_dataset_helper
import odm_dataset_config
import datetime
import time
from urlparse import urlparse
import json
import collections

log = logging.getLogger(__file__)
log.setLevel(logging.DEBUG)

class Odm_Dataset_ExtPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)


    #  IValidators
    def get_validators(self):

        log.error("get_validators")

        return {
            'odm_dataset_if_empty_new_id': odm_dataset_helper.if_empty_new_id,
            'odm_dataset_urlencode': odm_dataset_helper.urlencode,
            'odm_dataset_clean_taxonomy_tags': odm_dataset_helper.clean_taxonomy_tags,
            'odm_dataset_sanitize_list': odm_dataset_helper.sanitize_list,
            'odm_dataset_convert_to_multilingual': odm_dataset_helper.convert_to_multilingual,
            'odm_dataset_if_empty_same_as_name_if_not_empty': odm_dataset_helper.if_empty_same_as_name_if_not_empty,
            'odm_dataset_if_empty_same_as_description_if_not_empty': odm_dataset_helper.if_empty_same_as_description_if_not_empty,
            'odm_dataset_fluent_required': odm_dataset_helper.fluent_required,
            'odm_dataset_record_does_not_exist_yet': odm_dataset_helper.record_does_not_exist_yet,
            'odm_dataset_convert_csv_to_array': odm_dataset_helper.convert_csv_to_array,
            'odm_dataset_remove_topics': odm_dataset_helper.remove_topics
          }

    # ITemplateHelpers
    def get_helpers(self):

        return {
            'odm_dataset_get_current_time': odm_dataset_helper.get_current_time,
            'odm_dataset_get_localized_tag': odm_dataset_helper.get_localized_tag,
            'odm_dataset_get_current_language': odm_dataset_helper.get_current_language,
            'odm_dataset_retrieve_taxonomy_from_tags': odm_dataset_helper.retrieve_taxonomy_from_tags,
            'odm_dataset_convert_to_multilingual': odm_dataset_helper.convert_to_multilingual,
            'odm_dataset_clean_taxonomy_tags': odm_dataset_helper.clean_taxonomy_tags,
            'odm_dataset_get_resource_from_datatable': odm_dataset_helper.get_resource_from_datatable,
            'odm_dataset_get_dataset_name': odm_dataset_helper.get_dataset_name,
            'odm_dataset_get_dataset_notes': odm_dataset_helper.get_dataset_notes,
            'odm_dataset_get_resource_id_for_field' : odm_dataset_config.get_resource_id_for_field,
            'odm_dataset_validate_fields' : odm_dataset_helper.validate_fields,
            'odm_dataset_detail_page_url': odm_dataset_helper.detail_page_url
          }

    # IPackageController
    def before_create(self, context, resource):

        dataset_type = context['package'].type if 'package' in context else ''
        if dataset_type == 'dataset':
            log.info('before_create')

    def after_create(self, context, pkg_dict):

        dataset_type = context['package'].type if 'package' in context else pkg_dict['type']
        if dataset_type == 'dataset':
            log.info('after_create: %s', pkg_dict['name'])


    def after_update(self, context, pkg_dict):

        dataset_type = context['package'].type if 'package' in context else pkg_dict['type']
        if dataset_type == 'dataset':
            log.info('after_update: %s', pkg_dict['name'])





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



