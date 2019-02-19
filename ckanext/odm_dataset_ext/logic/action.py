
import ckan.logic.action.get as get_actions
from ckan.common import config
from ckan.plugins import toolkit

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@toolkit.side_effect_free
def package_search(context, data_dict):

    try:
        query = data_dict.get('fq_list', [])
        query.extend(['extras_odm_spatial_range:%s' % config.get('ckanext-odm_dataset_ext.country_code')])
        data_dict['fq_list'] = query
        return get_actions.package_search(context, data_dict)

    except Exception as e:
        log.error('Something wrong with dataset fileter - ', e)
        return get_actions.package_search(context, data_dict)



