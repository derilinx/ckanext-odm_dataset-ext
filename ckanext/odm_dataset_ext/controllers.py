from ckan.controllers.package import PackageController
from ckan.plugins import toolkit
from ckan.common import _
from ckan.lib.base import abort

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class OdmDataset(PackageController):
    def read_reference(self, reference):
        log.debug('Checking for reference: %s' % reference)
        package = toolkit.get_action('package_search')({}, {'fq': 'odm_reference_document:%s' % reference})
        if package['results']:
            return self.read(package['results'][0]['id'])
        else:
            abort(404, _('Dataset not found'))
        
        
                             
