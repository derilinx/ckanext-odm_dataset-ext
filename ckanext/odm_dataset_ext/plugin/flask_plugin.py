import ckan.plugins as plugins
from ckan.plugins import toolkit
from ckanext.odm_dataset_ext.views import odm_dataset_views
import logging
log = logging.getLogger(__name__)


class Odm_Dataset_ExtMixinPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IBlueprint)

    def get_blueprint(self):
        return [odm_dataset_views]
