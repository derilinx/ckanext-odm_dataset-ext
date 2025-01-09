#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from ckan.plugins.toolkit import config

log = logging.getLogger(__name__)

def get_resource_id_for_field(field):

	resource_id = config.get('odm.resource_id.'+field)

	return resource_id
