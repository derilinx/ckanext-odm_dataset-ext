#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import re
import uuid

from ckan import model

import ckan
from ckan.plugins import toolkit
from ckan.common import _

from ckan.lib.navl.dictization_functions import missing, Invalid


import logging
log = logging.getLogger(__name__)


def clean_taxonomy_tags(value):
    '''Cleans taxonomy field before storing it'''

    if isinstance(value, basestring):
        return json.dumps([value])

    return json.dumps(list(value))

def convert_csv_to_array(value):
    '''Splits elements of a csv string'''

    return list(value.replace(" ", "").split(','))


def if_empty_same_as_name_if_not_empty(key, data, errors, context):

    log.debug('if_empty_same_as_name_if_not_empty: %s', str(key))

    value = data.get(key)
    if not value or value is missing:
        value_replacement = data[key[:-1] + ("name",)]
        if value_replacement:
            data[key] = value_replacement

def if_empty_same_as_description_if_not_empty(key, data, errors, context):

    log.debug('if_empty_same_as_description_if_not_empty: %s', str(key))

    value = data.get(key)
    if not value or value is missing:
        value_replacement = data[key[:-1] + ("description",)]
        if value_replacement:
            data[key] = value_replacement


def sanitize_list(value):
    '''Converts strings to list'''

    log.debug('sanitize_list: %s', str(value))

    result = []

    if isinstance(value, list):
        for item in value:
            result.append(str(item))

    if isinstance(value, set):
        for item in value:
            result.append(item)

    if isinstance(value, basestring):
        new_value = value.encode("ascii")
        new_value = new_value.replace("[u'","")
        new_value = new_value.replace(" u'","")
        new_value = new_value.replace("']","")
        new_value = new_value.replace("'","")
        new_value = new_value.replace("{","")
        new_value = new_value.replace("}","")
        result = new_value.split(",")

    return json.dumps(result)


def fluent_required(value):
    '''Checks that the value inputed is a json object with at least "en" among its keys'''

    log.debug('fluent_required: %s', str(value))

    value_json = {}

    try:
        value_json = json.loads(value);
    except:
        raise toolkit.Invalid("This multilingual field is mandatory. Please specify a value, at least in English.")

    if "en" not in value_json or not value_json["en"]:
        raise toolkit.Invalid("This multilingual field is mandatory. Please specify a value, at least in English.")

    return value


def record_does_not_exist_yet(value, context):
    '''Checks whether the value corresponds to an existing record name, if so raises Invalid'''

    found = True

    log.debug('record_does_not_exist_yet: %s %s', str(value), str(context))

    if 'package' in context:
        current_package = context['package']
        if current_package.name == value:
            return value

    s = """SELECT * FROM package p
                    WHERE p.name = '%(name)s'""" % {'name': value}
    count = model.Session.execute(s).rowcount

    if count > 0:
        raise toolkit.Invalid("There is a record already with that name, please adapt URL.")

    return value


def urlencode(value):
    log.debug('urlencode: %s', str(value))

    value = re.sub(' ','-',value)
    pattern = re.compile('[^a-zA-Z0-9_-]', re.UNICODE)
    value = re.sub(pattern, '', value)
    return value.lower()[0:99]

def if_empty_new_id(value):

    log.debug('if_empty_new_id: %s', str(value))

    if not value:
        value = str(uuid.uuid4());
    return value

def convert_numeric(value, context):

    if not value: return ''
    try:
        return float(value)
    except ValueError:
        raise toolkit.Invalid(_('Please enter a numeric value'))



def remove_topics(value):

    topics = toolkit.get_action('tag_list')(data_dict={"vocabulary_id":"taxonomy"})
    lowercase_topics = [x.lower() for x in topics]
    tags = value.split(",")
    clean_tags = []
    for tag in tags:
        if tag.lower() not in lowercase_topics:
            clean_tags.append(tag)

    return ",".join(clean_tags)

# hack. UNDONE
# It's trying to validate the extras fields that they're not in the schema, but
# scheming has added all the extras fields to the base schema.
# so just get the default ones, and check against them.
# DEBUG:ckan.logic.action.update:got validattion error: {u'extras': [{}, {'key': [u'There is a schema field with the same name: DQ_PositionalAccuracy']}, {'key': [u'There is a schema field with the same name: LI_Lineage']}, {'key': [u'There is a schema field with the same name: LI_ProcessStep']}]}

_default_fields = set(ckan.logic.schema.default_create_package_schema().keys())
def extra_key_not_in_root_schema(key, data, errors, context):
    if data[key] in _default_fields:
        log.debug(' default fields keys: %s' % _default_fields)
        raise Invalid(_('There is a schema field with the same name: %s'% data[key]))
        
        
