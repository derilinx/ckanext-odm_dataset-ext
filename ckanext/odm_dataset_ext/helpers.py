#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import ckan
import urllib
import datetime
import re
import uuid
import os
from ckan.plugins import toolkit
from ckan.plugins.toolkit import request
from ckan.common import config

import logging
log = logging.getLogger(__name__)

def create_default_issue_dataset(pkg_info):
    ''' Uses CKAN API to add a default Issue as part of the vetting workflow for datasets'''
    try:

        extra_vars = {}

        issue_message = ckan.lib.base.render('messages/default_issue_dataset.txt',extra_vars=extra_vars)

        params = {'title':'User Dataset Upload Checklist','description':issue_message,'dataset_id':pkg_info['id']}
        toolkit.get_action('issue_create')(data_dict=params)

    except KeyError:

        log.error("Action 'issue_create' not found. Please make sure that ckanext-issues plugin is installed.")

def convert_to_multilingual(data):
    '''Converts strings to multilingual with the current language set'''

    if data:
        log.debug('convert_to_multilingual: %s' % data)

    if isinstance(data, basestring):
        multilingual_data = {}
        multilingual_data[get_current_language()] = data;
    else:
        multilingual_data = data

    return multilingual_data


def get_multilingual_data(field_name, data):
    # may be in data[field_name],
    # may be in data[field_name-lang], especially coming from a new submission
    # may be in data['extras'] somewhere
    log.debug("%s: %s" % (field_name, data))
    if field_name in data:
        # could be that we have a blank dictionary. If we're checking a translated field
        # then we want to return the base field info if there's anything there.
        value = data[field_name]
        if not value and '_translated' in field_name:
            base_field_name = field_name.replace('_translated','')
            log.debug('base_field_name: %s ' % base_field_name)
            if base_field_name in data:
                log.debug('base_field_name: %s ' % {get_current_language(): data[base_field_name]} )
                return {get_current_language(): data[base_field_name]}
        if isinstance(value, dict):
            return value
        return {get_current_language(): value}

    # check data[field_name-lang]
    base = '%s-' % field_name
    items = {key[len(base):]: data[key] for key in data.keys() if key.startswith(base)}
    if items:
        return items

    if 'extras' in data:
        for elt in data['extras']:
            if elt['key'] == field_name:
                try:
                    return json.loads(elt['value'])
                except:
                    return {get_current_language(): elt['value']}
    return {}

def get_currentlang_data(fieldname, data):
    return get_multilingual_data(fieldname, data).get(get_current_language(), '')

def dataset_display_name(pkg):
    log.debug('dataset_display_name: %s' % pkg)
    return get_currentlang_data('title_translated', pkg) or pkg['title'] or pkg['name']

def get_list_data(field_name, data):
    # may be in data[field_name], may be in data['extras'] somewhere
    if field_name in data:
        return data[field_name]
    if 'extras' in data:
        for elt in data['extras']:
            if elt['key'] == field_name:
                try:
                    return json.loads(elt['value'])
                except:
                    return [elt['value']]
    return []

def get_field_langs(field_data, current_langs):
    # Complicated. We want to include all the current langs defined by the ckan install,
    # as well as any of the other languages that are already defined, in a consistent order
    langs = list(current_langs)
    langs.extend([l for l,val in field_data.items() if l not in current_langs and val])
    return langs

def clean_taxonomy_tags(value):
    '''Cleans taxonomy field before storing it'''

    if isinstance(value, basestring):
        return json.dumps([value])

    return json.dumps(list(value))

def get_localized_tag(tag):
    '''Looks for a term translation for the specified tag. Returns the tag untranslated if no term found'''

    log.debug('odm_dataset_get_localized_tag: %s', str(tag))

    desired_lang_code = request.environ['CKAN_LANG']

    translations = ckan.logic.action.get.term_translation_show(
                    {'model': ckan.model},
                    {'terms': (tag)})

    # Transform the translations into a more convenient structure.
    for translation in translations:
        if translation['lang_code'] == desired_lang_code:
            return translation['term_translation']

    return str(tag)

def get_current_language():
    '''Returns the current language code'''

    log.debug('get_current_language %s', str(request.environ['CKAN_LANG']))

    return request.environ['CKAN_LANG']

def get_localized_tags_string(tags_string):
    '''Returns a comma separated string with the translation of the tags specified. Calls get_localized_tag'''

    log.debug('get_localized_tags_string: %s', str(tags_string))

    translated_array = []
    for tag in tags_string.split(', '):
        translated_array.append(get_localized_tag(tag))

    if len(translated_array)==0:
        return ''

    return ','.join(translated_array)

def get_required(schema, field):
     return field.get('odm_required', False)

def validate_fields(package):
    '''Checks that the package has all fields marked with validate = true on schema'''

    log.debug('validate_fields: %s', str(package))

    missing = dict({"package" : [], "resources": [] })

    schema_path = os.path.abspath(os.path.join(__file__, '../../','odm_dataset_schema.json'))
    with open(schema_path) as f:
        try:
            schema_json = json.loads(f.read())

            for field in schema_json['dataset_fields']:
                if "validate" in field and field["validate"] == "true":
                    if field["field_name"] not in package or not package[field["field_name"]]:
                        missing["package"].append(field["field_name"])
                    elif "multilingual" in field and field["multilingual"] == "true":
                        json_field = package[field["field_name"]];
                        if json_field and "en" not in json_field or json_field["en"] == "":
                            missing["package"].append(field["field_name"])

            for resource_field in schema_json['resource_fields']:
                for resource in package["resources"]:
                    if "validate" in resource_field and resource_field["validate"] == "true":
                        if resource_field["field_name"] not in resource or not resource[resource_field["field_name"]]:
                            missing["resources"].append(resource_field["field_name"])
                        elif "multilingual" in resource_field and resource_field["multilingual"] == "true":
                            json_resource_field = resource[resource_field["field_name"]];
                            if json_resource_field and "en" not in json_resource_field or json_resource_field["en"] == "":
                                missing["resources"].append(resource_field["field_name"])

        except ValueError as e:
            log.info('invalid json: %s' % str(e))

    return missing


def retrieve_taxonomy_from_tags(tags_array):
    '''Looks into the dataset's tags and set the taxonomy array out of their display_name property'''

    log.debug('map_odm_language: %s', str(tags_array))

    if type(tags_array) is not list:
        return []

    taxonomy = []
    for tag in tags_array:
        taxonomy.append(tag['display_name'])

    return taxonomy

def get_current_time():
    return datetime.datetime.utcnow().isoformat()


def get_resource_from_datatable(resource_id):
    ''' pulls tabular data from datastore '''

    result = toolkit.get_action('datastore_search')(data_dict={'resource_id': resource_id,'limit':1000})

    return result['records']

def get_resource_id_for_field(field):
    resource_id = config.get('odm.resource_id.'+field)
    return resource_id

def get_resource_for_field(field):
    return get_resource_from_datatable(get_resource_id_for_field(field))

def get_resource_for_field_as_dict(field):
    return {e['id']:e['name'] for e in get_resource_from_datatable(get_resource_id_for_field(field))}

def get_package_type_label(dataset_type):
    package_label_dict = {'dataset': 'Dataset', 'laws_record': 'Laws Record',
                          'agreement': 'Agreement', 'library_record': 'Library Record'}
    return package_label_dict.get(dataset_type, '')

def listify(s):
    if isinstance(s, (str, unicode)):
        return
    if isinstance(s, (list, set)):
        return ','.join(s)
    if not s:
        return ''
    return json.dumps(s)

def autocomplete_multi_dataset_full_options(arr):
    return urllib.quote(json.dumps(multi_dataset_values(arr)))

def multi_dataset_values(arr):
    if isinstance(arr, (str, unicode)):
        arr = list(arr)

    lang = get_current_language()
    ret = []
    for name in arr:
        ret.extend(toolkit.get_action('odm_dataset_autocomplete_exact')({}, {'q': name,
                                                                             'lang': lang}))
    return ret
