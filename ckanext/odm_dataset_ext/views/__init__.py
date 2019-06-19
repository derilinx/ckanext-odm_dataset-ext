from ckan.views.user import RequestResetView
from ckan.views.user import PerformResetView
from . import user

RequestResetView.post = user.request_reset_post
PerformResetView._prepare = user.request_perform_reset_view_prepare