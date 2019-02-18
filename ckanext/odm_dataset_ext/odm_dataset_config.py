#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from genshi.template.text import NewTextTemplate
from ckan.lib.base import render
from ckan.common import config

log = logging.getLogger(__name__)

def get_resource_id_for_field(field):

	resource_id = config.get('odm.resource_id.'+field)

	return resource_id
