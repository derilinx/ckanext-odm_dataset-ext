# encoding: utf-8
from ckan.common import config
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import json

from .logic import action
from . import helpers, validators

import logging
log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)

I18N_FIELDS={ 'title_translated', 'notes_translated',
              'MD_Constraints', 'description_translated',
              'DQ_PositionalAccuracy', 'DQ_QuantitativeAttribute',
              'DQ_LogicalConsistency', 'DQ_Completeness',
              'LI_ProcessStep', 'LI_Lineage',
              'CI_ResponsibleParty_contact', 'MD_Metadata_contact',
              'MD_ScopeDescription_attributes',
              'MD_DataIdentification_keywords',
              'CI_Citation_identAuth', 'MD_LegalConstraints',
              'MD_Format_version',
              'odm_agreement_participating_share',
              'odm_agreement_concession_name',
              'odm_access_and_use_constraints',
              'odm_metadata_reference_information',
              'odm_agreement_short_notes_of_change', 'odm_contact',
              'odm_agreement_notes',
              'odm_agreement_parties_obligations',
              'odm_agreement_job_creation_summary',
              'odm_agreement_training_summary',
              'odm_agreement_environmental_protection',
              'odm_agreement_sociocultural_protection',
              'odm_agreement_fiscal_duties_summary',
              'odm_agreement_environmental_fund_summary',
              'odm_agreement_suspension_revocation_termination',
              'odm_agreement_suspension_related_project',
              'odm_short_title', 'odm_laws_previous_changes_notes',
              'odm_laws_notes', 'marc21_246', 'marc21_100', 'marc21_110',
              'marc21_700', 'marc21_710', 'marc21_260a', 'marc21_260b',
              'marc21_300', 'marc21_500' 'mid_page_data_translated'
              }


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
            'odm_dataset_validate_title_or_url': validators.validate_title_or_url,
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
        import ckan.lib.helpers
        return {
            'odm_dataset_get_current_time': helpers.get_current_time,
            'odm_dataset_get_localized_tag': helpers.get_localized_tag,
            'odm_dataset_get_current_language': ckan.lib.helpers.lang,
            'odm_dataset_retrieve_taxonomy_from_tags': helpers.retrieve_taxonomy_from_tags,
            'odm_dataset_convert_to_multilingual': helpers.convert_to_multilingual,
            'odm_dataset_clean_taxonomy_tags': helpers.clean_taxonomy_tags,
            'odm_dataset_get_resource_id_for_field' : helpers.get_resource_id_for_field,
            'odm_dataset_get_resource_from_datatable': helpers.get_resource_from_datatable,
            'odm_dataset_get_resource_for_field': helpers.get_resource_for_field,
            'odm_dataset_get_resource_for_field_as_dict': helpers.get_resource_for_field_as_dict,
            'odm_dataset_get_resource_for_field_for_form': helpers.get_resource_for_field_for_form,
            'odm_dataset_get_resource_name_for_field_value': helpers.get_resource_name_for_field_value,
            'odm_dataset_spatial_range_list': helpers.get_spatial_range_list,
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
            'odm_dataset_package_for_legacy_reference': helpers.package_for_legacy_reference,
            'odm_dataset_link_for_legacy_reference': helpers.link_for_legacy_reference,
            'odm_dataset_convert_num_to_year': helpers.convert_num_to_year,
            # overrides
            'dataset_display_name': helpers.dataset_display_name,
            'resource_display_name': helpers.resource_display_name,
            'fluent_form_label': helpers.fluent_form_label,
        }

    ## IActions
    def get_actions(self):
        custom_actions = {
            'package_create': action.package_create,
            'odm_dataset_autocomplete': action.dataset_autocomplete,
            'odm_keyword_autocomplete': action.odm_keyword_autocomplete,
            'odm_dataset_autocomplete_exact': action.dataset_autocomplete_exact,
            'unsafe_user_show': action.unsafe_user_show
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
        m.connect('odm_keyword_autocomplete', '/dataset/keyword_autocomplete', controller=controller,
                  action='keyword')

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

        try:
            pkg_dict['odm_language_list'] = json.loads(pkg_dict.get('odm_language', pkg_dict.get('MD_DataIdentification_language','[]')))
            pkg_dict['odm_spatial_range_list'] = pkg_dict.get('EX_Geoname',[])
            if type(pkg_dict['odm_spatial_range_list']) == type(set()) or '{' in pkg_dict['odm_spatial_range_list']:
                # Messed up data on staging, not on preprod
                del(pkg_dict['odm_spatial_range_list'])

        except Exception as msg:
            log.debug(msg)

        try:
            pkg_dict['extras_odm_keywords'] = pkg_dict.get('odm_keywords', '').split(',')
            pkg_dict['extras_odm_keywords_text'] = pkg_dict.get('odm_keywords', '')
        except Exception as msg:
            log.debug(msg)

        # normalize translated fields
        fields = [k for k in pkg_dict.keys() if k in I18N_FIELDS
                  or k.replace("extras_",'') in I18N_FIELDS ]
        for field in fields:
            try:
                vals = json.loads(pkg_dict.get(field, '{}').strip() or '{}')
                for k,v in vals.items():
                    if v:
                        pkg_dict['%s_%s' %(field, k)] = v
                del(pkg_dict[field])
            except Exception as msg:
                if pkg_dict.get('field', None):
                    log.error("Error extracting translated fields (pkg): %s, '%s', %s, %s",
                              field, pkg_dict.get('field',''), msg, pkg_dict['name'])

        # same for the resources
        try:
            resources = json.loads(pkg_dict.get('validated_data_dict','{}')).get('resources')
            for resource in resources:
                fields = [k for k in resource.keys() if k in I18N_FIELDS ]
                for field in fields:
                    try:
                        vals = resource.get(field, '{}')
                        for k,v in vals.items():
                            if v:
                                index_field_name = 'res_extras_%s_%s' %(field, k)
                                orig_val = pkg_dict.get(index_field_name, [])
                                orig_val.append(v)
                                pkg_dict[index_field_name] = orig_val
                    except Exception as msg:
                        log.error("Error extracting translated fields: %s", msg)
        except Exception as msg:
            log.error("Error extracting resources: %s" %msg)

        #log.debug(pkg_dict)
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
