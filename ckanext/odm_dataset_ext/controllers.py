from ckan.controllers.package import PackageController
from ckan.plugins import toolkit
from ckan.plugins.toolkit import c, _
from ckan.common import request
from ckan.lib.base import abort, BaseController

import requests
import json
import decimal

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)

class _helpers(object):
    def __getattr__(self, key):
        return toolkit.h[key]
h = _helpers()


class OdmDataset(PackageController):
    def read_reference(self, reference):
        log.debug('OdmDataset.read_reference: Checking for reference: %s' % reference)
        package = h.odm_dataset_package_for_legacy_reference(reference)
        if package:
            return self.read(package['id'])
        else:
            abort(404, _('Dataset not found'))


    def _preflight_wms(self, params, wms_resource):
        try:
            log.debug("Preflighting wms for %s %s %s", wms_resource['wms_layer'], wms_resource['id'], params)
            params = {"cql_filter": " AND ".join(["%s='%s'" % s for s in params.items()]),
                      "exceptions":'application/vnd.ogc.se_xml',
                      'feature_count':'101',
                      'service':'WMS',
                      'version':'1.1.1',
                      'request':'GetMap',
                      'layers': wms_resource['wms_layer'],
                      'width':'1',
                      'height':'1',
                      'format':'image/png',
                      'bbox':'0,0,1,1',
            }
            resp = requests.get(wms_resource['wms_server'], params=params)
            return resp.headers['Content-Type'] == 'image/png'
        except Exception as msg:
            log.error("Error preflighting cql request: %s" % msg)
            return False

    def _get_wfs_bounding_box(self, params, wms_resource):
        try:
            log.debug("Getting bounding box for %s %s %s", wms_resource['wms_layer'], wms_resource['id'], params)
            params = {"cql_filter": " AND ".join(["%s='%s'" % s for s in params.items()]),
                      'maxFeatures':'101',
                      'service':'WFS',
                      'version':'1.1.0',
                      'request':'GetFeature',
                      'typeName': wms_resource['wms_layer'],
                      'outputFormat':'application/json',
                      'srsName':'EPSG:4326',
            }
            resp = requests.get(wms_resource['wms_server'], params=params)
            log.debug(resp.text)
            return resp.json()['bbox']
        except Exception as msg:
            log.error("Error getting bounding box: %s" % msg)
            return False


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
            c.fields = results['fields']
            c.resource = resource
            c.pkg_dict = toolkit.get_action('package_show')({}, {'id': id})
            c.params = params
            try:
                c.wms_resource = [r for r in h.odm_profile_wms_for_lang(c.pkg_dict, h.lang())
                                  if self._preflight_wms(params, r)]
                # in this case, we've got one feature and possibly multiple layers.
                # the bounding box for one should be ok.
                bb = self._get_wfs_bounding_box(params, c.wms_resource[0])
                log.debug(bb)
                #[ w, s, e, n ]
                scale = decimal.Decimal('0.3')
                precision = decimal.Decimal('0.1')
                c.bounding_box = [ float((decimal.Decimal(bb[0]) - scale).quantize(precision)),
                                   float((decimal.Decimal(bb[1]) - scale).quantize(precision)),
                                   float((decimal.Decimal(bb[2]) + scale).quantize(precision)),
                                   float((decimal.Decimal(bb[3]) + scale).quantize(precision))]
                log.debug(c.bounding_box)
            except Exception as msg:
                log.error("Exception preflighting resource: %s", msg)
                c.wms_resource = None

            return toolkit.render('package/resource_detail.html')
        else:
            abort(404, _('Detail item not found in datastore'))


class OdmAutocomplete(BaseController):

    def dataset(self):
        params = dict(request.params)
        toolkit.response.headers['Content-Type'] = 'application/json;charset=utf-8'

        if 'exact:' in params.get('q',''):
            params['q'] = params['q'].replace('exact:','')
            return json.dumps(toolkit.get_action('odm_dataset_autocomplete_exact')({},params))

        return json.dumps(toolkit.get_action('odm_dataset_autocomplete')({},params))

    def keyword(self):
        params = dict(request.params)
        toolkit.response.headers['Content-Type'] = 'application/json;charset=utf-8'
        return json.dumps(toolkit.get_action('odm_keyword_autocomplete')({},params))
