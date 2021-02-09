import ckan.plugins as plugins
from ckan.plugins import toolkit
import logging
log = logging.getLogger(__name__)


class Odm_Dataset_ExtMixinPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    implements(p.IRoutes, inherit=True)

    # IRoutes
    def before_map(self, m):
        log.debug("odm_dataset_ext.before_map")
        controller = "ckanext.odm_dataset_ext.controllers:OdmDataset"
        m.connect('odm_dataset_reference', '/dataset/reference/{reference}', controller=controller,
                  type='dataset', action='read_reference')

        m.connect('odm_dataset_detail', '/dataset/{id}/resource/{rid}/detail', controller=controller,
                  type='dataset', action='resource_read_detail')

        controller = "ckanext.odm_dataset_ext.controllers:OdmAutocomplete"
        m.connect('odm_dataset_autocomplete', '/dataset/autocomplete', controller=controller,
                  action='dataset')
        m.connect('odm_keyword_autocomplete', '/dataset/keyword_autocomplete', controller=controller,
                  action='keyword')

        return m
