# encoding: utf-8
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from .logic import action
import ckan
import logging
import ckan.lib.helpers as h
from beaker.middleware import SessionMiddleware
import sys
import os
from ckan.common import config
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import odm_dataset_config
import datetime
import time
from urlparse import urlparse
import json
import collections

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from . import helpers, validators


class Odm_Dataset_ExtPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IActions)

    #  IValidators
    def get_validators(self):
        return {
            'odm_dataset_if_empty_new_id': validators.if_empty_new_id,
            'odm_dataset_numeric': validators.convert_numeric,
            'odm_dataset_urlencode': validators.urlencode,
            'odm_dataset_clean_taxonomy_tags': validators.clean_taxonomy_tags,
            'odm_dataset_sanitize_list': validators.sanitize_list,
            'odm_dataset_convert_to_multilingual': helpers.convert_to_multilingual,
            'odm_dataset_if_empty_same_as_name_if_not_empty': validators.if_empty_same_as_name_if_not_empty,
            'odm_dataset_if_empty_same_as_description_if_not_empty': validators.if_empty_same_as_description_if_not_empty,
            'odm_dataset_fluent_required': validators.fluent_required,
            'odm_dataset_record_does_not_exist_yet': validators.record_does_not_exist_yet,
            'odm_dataset_convert_csv_to_array': validators.convert_csv_to_array,
            'odm_dataset_remove_topics': validators.remove_topics,
            'extra_key_not_in_root_schema': validators.extra_key_not_in_root_schema,
          }

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'odm_dataset_get_current_time': helpers.get_current_time,
            'odm_dataset_get_localized_tag': helpers.get_localized_tag,
            'odm_dataset_get_current_language': helpers.get_current_language,
            'odm_dataset_retrieve_taxonomy_from_tags': helpers.retrieve_taxonomy_from_tags,
            'odm_dataset_convert_to_multilingual': helpers.convert_to_multilingual,
            'odm_dataset_clean_taxonomy_tags': helpers.clean_taxonomy_tags,
            'odm_dataset_get_resource_from_datatable': helpers.get_resource_from_datatable,
            'odm_dataset_get_dataset_name': helpers.get_dataset_name,
            'odm_dataset_get_dataset_notes': helpers.get_dataset_notes,
            'odm_dataset_get_resource_id_for_field' : odm_dataset_config.get_resource_id_for_field,
            'odm_dataset_validate_fields' : helpers.validate_fields,
            'odm_dataset_detail_page_url': helpers.detail_page_url,
            'odm_dataset_get_required': helpers.get_required,
          }

        ## IActions
    def get_actions(self):

        return {'package_search': action.package_search}


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

    def after_show(self, context, pkg_dict):
        # UNDONE notes/abstract, odm_dataset_spatial
        def _decode(s):
            try:
                return json.loads(s)
            except:
                return s
        extras = dict([(l['key'], _decode(l['value'])) for l in pkg_dict['extras']])
        pkg_dict.update(extras)
        try:
            pkg_dict['EX_Geoname'] = pkg_dict['odm_spatial_range']
            
        except:
            log.debug('Exception: %s' % msg)
            log.debug(extras)
            
        pkg_dict['CI_ResponsibleParty'] = pkg_dict['organization']
        pkg_dict['CI_Citation_title'] = pkg_dict.get('title_translated', {'en': pkg_dict['title']})
        if pkg_dict.get('notes_translated', None) and not pkg_dict.get('MD_DataIdentification_abstract_translated', None):
            pkg_dict['MD_DataIdentification_abstract_translated'] = pkg_dict['notes_translated']

        for f in ('EX_GeographicBoundingBox_north',
                  'EX_GeographicBoundingBox_east',
                  'EX_GeographicBoundingBox_south',
                  'EX_GeographicBoundingBox_west'):
            if not pkg_dict[f] or pkg_dict[f] == "{}":
                pkg_dict[f] = ''
             
        return pkg_dict

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
