from ckan.lib.mailer import mail_recipient
from ckan.lib.dictization.model_dictize import _get_members, user_list_dictize
from ckan.common import config
import ckan.model as model
import json
import logging

log = logging.getLogger(__name__)

_roles_to_send_email = (
    'admin',
    'editor'
)


def get_email_dict(harvester_type, user_name, title, pkg_id):
    """
    Prepare header and body to send an email notification.
    :return:
    """
    site_url = config.get('ckan.site_url')

    _harvesters_msg = {
        "mimu": {
            "subject": "MIMU Harvester added a new dataset.",
            "body": """
Hi {user_name},

MIMU harvester added a new private dataset {title}. 
Please visit the below url to make the dataset active.

Dataset URL: {site_url}/dataset/{pkg_id}

Thank you,

The Opendevelopment Mekong team.
                    
                    """.format(
                site_url=site_url,
                user_name=user_name,
                title=title,
                pkg_id=pkg_id
            )
        }
    }

    return _harvesters_msg[harvester_type]


def get_users_for_group(context, owner_org):
    """

    :param context:
    :param owner_org:
    :return:
    """
    context['with_capacity'] = True
    group = model.Group.get(owner_org)
    users = user_list_dictize(_get_members(context, group, 'users'), context)

    return users


def notify_users(context, pkg_dict, harvester_type="mimu"):
    """

    :param context:
    :param pkg_dict:
    :param harvester_type:
    :return:
    """
    _users_to_notify = get_users_for_group(context, pkg_dict.get('owner_org'))
    try:
        pkg_title = json.loads(pkg_dict.get('title_translated', {})).get('en', 'NA')
    except Exception as e:
        log.error(e)
        pkg_title = "NA"

    for user in _users_to_notify:
        if user['capacity'] in _roles_to_send_email:
            _user_object = model.User.get(user['id'])
            user_fullname = _user_object.fullname
            user_email = _user_object.email
            email_dict = get_email_dict(harvester_type, user_fullname, pkg_title, pkg_dict['id'])

            mail_recipient(
                user_fullname,
                user_email,
                email_dict['subject'].strip(),
                email_dict['body'].strip()
            )

    return None





