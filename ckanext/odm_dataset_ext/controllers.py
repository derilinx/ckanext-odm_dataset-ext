from ckan.controllers.package import PackageController
from ckan.plugins import toolkit
from ckan.plugins.toolkit import c, _
from ckan.common import request
from ckan.lib.base import abort



import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class OdmDataset(PackageController):
    def read_reference(self, reference):
        log.debug('OdmDataset.read_reference: Checking for reference: %s' % reference)
        package = toolkit.get_action('package_search')({}, {'fq': 'odm_reference_document:%s' % reference})
        if package['results']:
            return self.read(package['results'][0]['id'])
        else:
            abort(404, _('Dataset not found'))
        
    def resource_read_detail(self, id, rid):
        """ url should be dataset/[id]/resource/[rid]/detail?field=value """
        log.debug('OdmDataset read_detail: %s' % id)

        params = dict(request.params)

        log.debug(params)
        
        resource = toolkit.get_action('resource_show')({}, {'id': rid})
        if not resource:
            abort(404, _('Resource not found'))

        if not resource.get('datastore_active', None):
            abort(404, _('Resource not found in datastore'))

        results = toolkit.get_action('datastore_search')({}, {'resource_id': rid,
                                                           'q': params,
                                                           'limit': 1})

        if results['total']:
            c.line = results['records'][0]
            c.resource = resource
            c.pkg_dict = toolkit.get_action('package_show')({}, {'id': id})

            return toolkit.render('package/resource_detail.html')
        else:
            abort(404, _('Detail item not found in datastore'))
        
                             