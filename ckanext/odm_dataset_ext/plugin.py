# encoding: utf-8
from ckan.common import config
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import json

from .logic import action
from . import helpers, validators

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Odm_Dataset_Resource(plugins.SingletonPlugin):
    plugins.implements(plugins.IResourceController, inherit=True)

    def after_update(self, context, resource):
        if not (resource['format'] == 'WMS'): return
        log.info('resource after_create: %s' % resource['id'])
        return self._core(context, resource)

    def after_create(self, context, resource):
        if not (resource['format'] == 'WMS'): return
        log.info('resource after_create: %s' % resource['id'])
        return self._core(context, resource)

    def _core(self, context, resource):
        try:
            package = toolkit.get_action('package_show')(context, {'id':resource['package_id']})
            if package.get('EX_GeographicBoundingBox_north', None): return
            try:
                geo_info = toolkit.get_action('vectorstorer_spatial_metadata_for_resource')(context, {'resource_id': resource['id']})
            except Exception as msg:
                return
            if not geo_info: return
            crs = geo_info['crs'][0].lower()
            # crs:84 is shorthand for epsg:4326, aka, lat/lon
            if crs == 'crs:84':
                crs = 'epsg:4326'
            update = {'id': resource['package_id'],
                      'MD_DataIdentification_spatialReferenceSystem': crs,
                      'EX_GeographicBoundingBox_north': geo_info['EX_GeographicBoundingBox']['northBoundLatitude'],
                      'EX_GeographicBoundingBox_south': geo_info['EX_GeographicBoundingBox']['southBoundLatitude'],
                      'EX_GeographicBoundingBox_west': geo_info['EX_GeographicBoundingBox']['westBoundLongitude'],
                      'EX_GeographicBoundingBox_east': geo_info['EX_GeographicBoundingBox']['eastBoundLongitude'],
                      }
            log.debug("Setting Bounding Box: %s" % update)
            return toolkit.get_action('package_patch')(context, update)
        except Exception as msg:
            log.error("Error updating resource after_create: %s" %msg)
            raise



class Odm_Dataset_ExtPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IRoutes, inherit=True)

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
            'odm_dataset_get_resource_id_for_field' : helpers.get_resource_id_for_field,
            'odm_dataset_validate_fields' : helpers.validate_fields,
            'odm_dataset_get_required': helpers.get_required,
            'odm_dataset_get_multilingual_data': helpers.get_multilingual_data,
            'odm_dataset_get_currentlang_data': helpers.get_currentlang_data,
            'odm_dataset_get_list_data': helpers.get_list_data,
            'odm_dataset_get_field_langs': helpers.get_field_langs,
            'odm_dataset_get_package_type_label': helpers.get_package_type_label,
            'odm_dataset_listify': helpers.listify,
            'odm_dataset_autocomplete_full_options': helpers.autocomplete_multi_dataset_full_options,
            'odm_dataset_multi_dataset_values': helpers.multi_dataset_values,

        }

    ## IActions
    def get_actions(self):
        custom_actions = {
            'package_create': action.package_create,
            'odm_dataset_autocomplete': action.dataset_autocomplete,
            'odm_dataset_autocomplete_exact': action.dataset_autocomplete_exact,
        }

        if False: # to enable splitting the sites by odm_spatial_range
            custom_actions['package_search'] = action.package_search
            return custom_actions
        return custom_actions

    #IRoutes
    def before_map(self, m):
        log.debug("odm_dataset_ext.before_map")
        controller = "ckanext.odm_dataset_ext.controllers:OdmDataset"
        m.connect('odm_dataset_reference', '/dataset/reference/{reference}', controller=controller,
                  type='dataset', action='read_reference')

        m.connect('odm_dataset_detail', '/dataset/{id}/resource/{rid}/detail', controller=controller,
                  type='dataset', action='resource_read_detail')

        controller = "ckanext.odm_dataset_ext.controllers:OdmAutocomplete"
        m.connect('odm_dataset_autocomplete', '/dataset/autocomplete', controller=controller,
                  action='dataset')

        return m

    # IPackageController
    def before_create(self, context, resource):

        dataset_type = context['package'].type if 'package' in context else ''
        if dataset_type == 'dataset':
            log.info('before_create')

    def after_create(self, context, pkg_dict):
        dataset_type = context['package'].type if 'package' in context else pkg_dict['type']
        review_system = toolkit.asbool(config.get("ckanext.issues.review_system", False))
        if dataset_type == 'dataset' and review_system:
            log.info('after_create: %s', pkg_dict['name'])
            description_link = config.get('ckanext.issues.new.description_link')
            anchor_tag = config.get('ckanext.issues.anchor_tag.'+str(dataset_type), '')
            description = "Thank you for uploading this item. Instruction on vetting "\
                          "system available on: {}".format(description_link+anchor_tag)
            data_dict = {'title':'User {} Upload Checklist'.format(helpers.get_package_type_label(dataset_type)),
                        'description': description,
                        'dataset_id':pkg_dict['id']}
            try:
                toolkit.get_action('issue_create')(context, data_dict)
            except Exception as msg:
                log.error('Exception: %s' % msg)

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

        try:
            extras = dict([(l['key'], _decode(l['value'])) for l in pkg_dict['extras']])
            pkg_dict['EX_Geoname'] = extras.get('odm_spatial_range', [])
        except Exception as msg:
            log.debug('Exception: %s' % msg)
            extras = {}

        pkg_dict['CI_ResponsibleParty'] = pkg_dict['organization']
        pkg_dict['CI_Citation_title'] = pkg_dict.get('title_translated', {'en': pkg_dict['title']})
        # Taxonomy is stored in tags, but obtained in taxonomy in library & such,
        # return it in MD_DataIdentification_topicCategory on read to match ISO schema
        pkg_dict["MD_DataIdentification_topicCategory"] = [t['name'] for t in pkg_dict.get('tags', [])]
        # https://github.com/OpenDevelopmentMekong/IssuesManagement/issues/175
        pkg_dict["taxonomy"] = [t['name'] for t in pkg_dict.get('tags', [])]

        log.debug('after_show: taxonomy: %s' % pkg_dict.get('taxonomy',''))
        if extras.get('notes_translated', None) and not pkg_dict.get('MD_DataIdentification_abstract', None):
            pkg_dict['MD_DataIdentification_abstract'] = extras['notes_translated']

        # UNDONE unclear if we really need this, it seems important on staging but not on a clean import.
        for f in ('EX_GeographicBoundingBox_north',
                  'EX_GeographicBoundingBox_east',
                  'EX_GeographicBoundingBox_south',
                  'EX_GeographicBoundingBox_west',
                  'MD_DataIdentification_spatialResolution'):
            if not pkg_dict.get(f,None) or pkg_dict.get(f,'') == "{}":
                pkg_dict[f] = ''

        return pkg_dict

    def before_index(self, pkg_dict):
        # Take this out of solr indexing, unless we want to make this a multivalued field.
        # tag searching should still work.
        if 'MD_DataIdentification_topicCategory' in pkg_dict:
            del(pkg_dict['MD_DataIdentification_topicCategory'])

        # https://github.com/OpenDevelopmentMekong/IssuesManagement/issues/175
        log.debug('Before Index: %s' % pkg_dict.get('taxonomy',''))
        if pkg_dict.get('taxonomy', None) and pkg_dict.get('tags', None):
            pkg_dict["taxonomy"] = [t['name'] for t in pkg_dict.get('tags', [])]

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
