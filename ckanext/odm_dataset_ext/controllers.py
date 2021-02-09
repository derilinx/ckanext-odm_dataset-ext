from ckan.controllers.package import PackageController
from ckan.lib.base import abort, BaseController
from ckanext.odm_dataset_ext import utils


class OdmDataset(PackageController):

    def read_reference(self, reference):
        return utils.read_reference(reference, controller_instance=self)

    def resource_read_detail(self, id, rid):
        return utils.resource_read_detail(id, rid)


class OdmAutocomplete(BaseController):

    def dataset(self):
        data = utils.odm_autocomplete_dataset()
        toolkit.response.headers['Content-Type'] = 'application/json;charset=utf-8'
        return data

    def keyword(self):
        data = odm_auto_complete_keyword()
        toolkit.response.headers['Content-Type'] = 'application/json;charset=utf-8'
        return data
