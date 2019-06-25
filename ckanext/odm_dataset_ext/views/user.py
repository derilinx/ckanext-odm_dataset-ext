from ckan.views.user import user
from flask import Blueprint
import ckan.model as model
from ckan.common import _, config, g
import ckan.lib.mailer as mailer
import ckan.lib.helpers as h
import logging
from ckan.views.user import RequestResetView
from ckan.views.user import PerformResetView
log = logging.getLogger(__name__)


def request_reset_post(self):
    context, data_dict = self._prepare()
    id = data_dict[u'id']

    context = {u'model': model, u'user': g.user, u'unsafe_user_show': u'True'}
    user_obj = None
    try:
        logic.get_action(u'unsafe_user_show')(context, data_dict)
        user_obj = context[u'user_obj']
    except logic.NotFound:
        # Try searching the user
        h.flash_error(_(u'No such user found - please contact system admin: %s') % id)

    if user_obj:
        try:
            # FIXME: How about passing user.id instead? Mailer already
            # uses model and it allow to simplify code above
            mailer.send_reset_link(user_obj)
            h.flash_success(
                _(u'Please check your inbox for '
                  u'a reset code.'))
            return h.redirect_to(u'/')
        except mailer.MailerException as e:
            h.flash_error(_(u'Could not send reset link: %s') %
                          text_type(e))
    return self.get()


def request_perform_reset_view_prepare(self, id):
    # FIXME 403 error for invalid key is a non helpful page
    context = {
        u'model': model,
        u'session': model.Session,
        u'user': id,
        u'keep_email': True,
        u'unsafe_user_show': u'True'
    }

    try:
        logic.check_access(u'user_reset', context)
    except logic.NotAuthorized:
        base.abort(403, _(u'Unauthorized to reset password.'))

    try:
        user_dict = logic.get_action(u'unsafe_user_show')(context, {u'id': id})
    except logic.NotFound:
        base.abort(404, _(u'User not found'))
    user_obj = context[u'user_obj']
    g.reset_key = request.params.get(u'key')
    if not mailer.verify_reset_link(user_obj, g.reset_key):
        msg = _(u'Invalid reset key. Please try again.')
        h.flash_error(msg)
        base.abort(403, msg)
    return context, user_dict

