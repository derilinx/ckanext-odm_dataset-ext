
import ckan.logic.action.get as get_actions
import ckan.logic.action.create as create_core
from ckan.common import config
from ckan.plugins import toolkit
import ckan.authz as authz
from paste.deploy.converters import asbool
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.logic as logic

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
NotFound = logic.NotFound
ValidationError = logic.ValidationError


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
                                                             'fq_list': ["type:(%s)" %" OR ".join(s for s in pkg_types)]}
                                                   )

    return [{'name': pkg['name'],
             'title': pkg.get('title_translated',{}).get(lang) or pkg['title'],
             } for pkg in results['results']]

@toolkit.side_effect_free
def dataset_autocomplete_exact(context, data_dict):
    q = data_dict.get('q')
    lang = data_dict.get('lang', 'en')
    pkg_types = [s.strip() for s in data_dict.get('type','').split(',')]
    if not (q and pkg_types): return []

    pkg = toolkit.get_action('package_show')(context, {'id':q }
                                                   )
    if pkg:
        return [{'name': pkg['name'],
                 'title': pkg.get('title_translated',{}).get(lang) or pkg['title'],
        }]
    return []

@toolkit.side_effect_free
def odm_keyword_autocomplete(context, data_dict):
    q = data_dict.get('q')
    pkg_types = [s.strip() for s in data_dict.get('type','').split(',')]
    if not (q and pkg_types): return []

    results = toolkit.get_action('package_search')(context, {
                                                             'rows': 0,
                                                             'fq_list': ["extras_odm_keywords_text:%s" % q],
                                                             'facet': 'true',
                                                             'facet.field': ['extras_odm_keywords']}
                                                   )

    q = q.lower()
    facets = results['search_facets']['extras_odm_keywords']['items']
    return sorted([{'name': item['name'],
                    'title': item['display_name'],
                    'count': item['count']
    } for item in facets if q in item['name'].lower()], key=lambda x: x['count'], reverse=True)


@toolkit.side_effect_free
def unsafe_user_show(context, data_dict):

    '''Return a user account.
        Either the ``id`` or the ``user_obj`` parameter must be given.
        :param id: the id or name of the user (optional)
        :type id: string
        :param user_obj: the user dictionary of the user (optional)
        :type user_obj: user dictionary
        :param include_datasets: Include a list of datasets the user has created.
            If it is the same user or a sysadmin requesting, it includes datasets
            that are draft or private.
            (optional, default:``False``, limit:50)
        :type include_datasets: bool
        :param include_num_followers: Include the number of followers the user has
            (optional, default:``False``)
        :type include_num_followers: bool
        :param include_password_hash: Include the stored password hash
            (sysadmin only, optional, default:``False``)
        :type include_password_hash: bool
        :returns: the details of the user. Includes email_hash, number_of_edits and
            number_created_packages (which excludes draft or private datasets
            unless it is the same user or sysadmin making the request). Excludes
            the password (hash) and reset_key. If it is the same user or a
            sysadmin requesting, the email and apikey are included.
        :rtype: dictionary
        '''

    model = context['model']

    try:
        unsafe_show = asbool(context.get('unsafe_user_show', 'False'))
        if not unsafe_show:
            raise ValidationError('There is no context setup for unsafe_user_show')
    except ValueError:
        raise ValidationError("Context unsafe_user_show should be boolean True or False")

    id = data_dict.get('id', None)
    provided_user = data_dict.get('user_obj', None)
    if id:
        user_obj = model.User.get(id)
        context['user_obj'] = user_obj
        if user_obj is None:
            raise NotFound
    elif provided_user:
        context['user_obj'] = user_obj = provided_user
    else:
        raise NotFound

    #_check_access('user_show', context, data_dict)

    # include private and draft datasets?
    requester = context.get('user')
    sysadmin = False
    if requester:
        sysadmin = authz.is_sysadmin(requester)
        requester_looking_at_own_account = requester == user_obj.name
        include_private_and_draft_datasets = (
                sysadmin or requester_looking_at_own_account)
    else:
        include_private_and_draft_datasets = False
    context['count_private_and_draft_datasets'] = \
        include_private_and_draft_datasets

    include_password_hash = sysadmin and asbool(
        data_dict.get('include_password_hash', False))

    user_dict = model_dictize.user_dictize(
        user_obj, context, include_password_hash)

    if context.get('return_minimal'):
        log.warning('Use of the "return_minimal" in user_show is '
                    'deprecated.')
        return user_dict

    if asbool(data_dict.get('include_datasets', False)):
        user_dict['datasets'] = []

        fq = "+creator_user_id:{0}".format(user_dict['id'])

        search_dict = {'rows': 50}

        if include_private_and_draft_datasets:
            search_dict.update({
                'include_private': True,
                'include_drafts': True})

        search_dict.update({'fq': fq})

        user_dict['datasets'] = \
            logic.get_action('package_search')(context=context,
                                               data_dict=search_dict) \
                .get('results')

    if asbool(data_dict.get('include_num_followers', False)):
        user_dict['num_followers'] = logic.get_action('user_follower_count')(
            {'model': model, 'session': model.Session},
            {'id': user_dict['id']})

    return user_dict