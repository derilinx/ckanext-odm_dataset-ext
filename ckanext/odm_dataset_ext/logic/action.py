
import ckan.logic.action.get as get_actions
import ckan.logic.action.create as create_core
from ckan.common import config
from ckan.plugins import toolkit

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@toolkit.side_effect_free
def package_search(context, data_dict):

    try:
        query = data_dict.get('fq_list', [])
        if not any('odm_spatial_range' in q for q in query):
            query.extend(['extras_odm_spatial_range:%s' % config.get('ckanext-odm_dataset_ext.country_code')])
            data_dict['fq_list'] = query
        return get_actions.package_search(context, data_dict)

    except Exception as e:
        log.error('Something wrong with dataset filter - ', e)
        return get_actions.package_search(context, data_dict)

def package_create(context, data_dict):
    try:
        toolkit.check_access('sysadmin', context, data_dict)
        return create_core.package_create(context, data_dict)
    except toolkit.NotAuthorized:
        data_dict['private']=True
        return create_core.package_create(context, data_dict)


@toolkit.side_effect_free
def dataset_autocomplete(context, data_dict):
    limit = data_dict.get('limit', 10)
    q = data_dict.get('q')
    lang = data_dict.get('lang', 'en')
    pkg_types = [s.strip() for s in data_dict.get('type','').split(',')]
    if not (q and pkg_types): return []

    results = toolkit.get_action('package_search')(context, {'q':q,
                                                             'rows': limit,
                                                             'fq_list': ["type:%s" %s for s in pkg_types]}
                                                   )

    return [{'name': pkg['name'],
             'title': pkg.get('title_translated',{}).get(lang) or pkg['title'],
             } for pkg in results['results']]
