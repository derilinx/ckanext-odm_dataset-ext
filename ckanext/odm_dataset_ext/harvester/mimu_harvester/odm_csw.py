from ckanext.spatial.harvesters.gemini import GeminiCswHarvester
from ckanext.spatial.harvesters.base import text_traceback
from ckanext.spatial.model.harvested_metadata import ISODocument, ISOElement, \
    ISOResourceLocator, ISOResponsibleParty, ISOReferenceDate, ISOKeyword, ISOUsage, \
    ISOAggregationInfo, ISOBoundingBox, ISOCoupledResources, ISODataFormat, ISOBrowseGraphic

from ckanext.harvest.model import HarvestObject

from sqlalchemy.sql import update, bindparam

from ckan import model
from ckan.model import Session

from ckanext.spatial.model import GeminiDocument
from ckanext.odm_dataset_ext.harvester.mimu_harvester import metadata_mapping
from ckan import logic
from ckan.logic import get_action, ValidationError
from ckan.lib.navl.validators import not_empty

from lxml import etree
from lxml.etree import XMLSyntaxError

import difflib
import uuid
from datetime import datetime
from dateutil.parser import parse
import json
from numbers import Number
# exception handling
import socket

import logging
log = logging.getLogger(__name__)

TIMEOUT = 30

#ISDE has a lot of non-conforming datasets, turn off xml validation at the source. 
VALIDATE = False


# the stock gemini harvester prints out the entire xml as part of the HarvestObject into the logs.
# this disables that logging.
logging.getLogger('ckanext.spatial.harvesters.gemini.import').setLevel(logging.ERROR)


class ODMMimuSpatialCSW(GeminiCswHarvester):
    def info(self):
        return {
            'name': 'odmcsw',
            'title': 'ODM MIMU CSW',
            'description': 'Gemini Harvester customised for omd mimu dataset harvester'
        }

    def import_gemini_object(self, gemini_string):
        '''Imports the Gemini metadata into CKAN.
        The harvest_source_reference is an ID that the harvest_source uses
        for the metadata document. It is the same ID the Coupled Resources
        use to link dataset and service records.
        Some errors raise Exceptions.
        '''
        log = logging.getLogger(__name__ + '.import')

        # gemini_string is unicode, but lxml doesn't like it when you tell it what
        # encoding to use. So we need to force it to use utf-8 encoding at all times.

        utf8_parser = etree.XMLParser(encoding='utf-8')

        def parse_from_unicode(unicode_str):
            s = unicode_str.encode('utf-8')
            return etree.fromstring(s, parser=utf8_parser)

        xml = parse_from_unicode(gemini_string)
        if VALIDATE:
            valid, profile, errors = self._get_validator().is_valid(xml)
            if not valid:
                out = errors[0][0] + ':\n' + '\n'.join(e[0] for e in errors[1:])
                log.error('Errors found for object with GUID %s:' % self.obj.guid)
                self._save_object_error(out, self.obj, 'Import')

        unicode_gemini_string = etree.tostring(xml, encoding=unicode)

        # may raise Exception for errors
        self.write_package_from_gemini_string(unicode_gemini_string)

    def gather_stage(self, harvest_job):
        # Changes from original -- additional error handling to skip the SyntaxError and Socket Timeouts
        
        log = logging.getLogger(__name__ + '.CSW.gather')
        log.debug('GeminiCswHarvester gather_stage for job: %r', harvest_job)
        # Get source URL
        url = harvest_job.source.url

        try:
            self._setup_csw_client(url)
        except Exception, e:
            self._save_gather_error('IError contacting the CSW server: %s' % e, harvest_job)
            return None

        log.debug('Starting gathering for %s' % url)
        used_identifiers = []
        ids = []
        try:
            for identifier in self.csw.getidentifiers(page=10):
                try:
                    log.info('Got identifier %s from the CSW', identifier)
                    if identifier in used_identifiers:
                        log.error('CSW identifier %r already used, skipping...' % identifier)
                        continue
                    if identifier is None:
                        log.error('CSW returned identifier %r, skipping...' % identifier)
                        # log an error here? happens with the dutch data
                        continue

                    # Create a new HarvestObject for this identifier
                    obj = HarvestObject(guid=identifier, job=harvest_job)
                    obj.save()
                    ids.append(obj.id)
                    used_identifiers.append(identifier)
                except Exception, e:
                    log.error(e)
                    self._save_gather_error('Error for the identifier %s [%r]' % (identifier, e), harvest_job)
                    continue
        except XMLSyntaxError as e:
            log.error("XML Syntax error gathering the identifiers from the CSW server [%s]", str(e))
        except socket.timeout as e:
            log.error("Timeout error gathering the identifiers from the CSW server [%s]", str(e))
        except Exception, e:
            log.error('Exception: %s' % text_traceback())
            self._save_gather_error('Error gathering the identifiers from the CSW server [%s]' % str(e), harvest_job)
            return None

        if len(ids) == 0:
            self._save_gather_error('No records received from the CSW server', harvest_job)
            return None

        log.info("\nGather stage summary: ")
        log.info("TOTAL IDs: {}".format(str(len(ids))))
        return ids

    def _create_package_from_data(self, package_dict, package=None):
        """
        Create or update package dict
        :param package_dict: dict
        :param package: dict (old package if exists)
        :return:
        """
        if not package:
            package_schema = logic.schema.default_create_package_schema()
        else:
            package_schema = logic.schema.default_update_package_schema()

        # The default package schema does not like Upper case tags
        tag_schema = logic.schema.default_tags_schema()
        tag_schema['name'] = [not_empty, unicode]
        package_schema['tags'] = tag_schema

        context = {'model': model,
                   'session': model.Session,
                   'user': self._get_user_name(),
                   'schema': package_schema,
                   'extras_as_string': True,
                   'api_version': '2'}
        if not package:
            # We need to explicitly provide a package ID, otherwise ckanext-spatial
            # won't be be able to link the extent to the package.
            package_dict['id'] = unicode(uuid.uuid4())
            package_schema['id'] = [unicode]

            try:
                package_dict = get_action('package_create')(context, package_dict)
                log.info(package_dict.get('owner_org', 'NO OWNER ORG'))
                log.info(package_dict.get('organization', 'NO ORG'))
                return package_dict
            except ValidationError as e:
                if "There is a record already with that name, please adapt URL." in str(e):
                    log.debug('Package validation error: %s, looking for a package with that name: %s' %
                             (e, package_dict['name']))
                    package = get_action('package_show')(context, {'id':package_dict['name']})
                    if package:
                        log.debug('updating existing package')
                        del(package_dict['id'])
                        del(package_schema['id'])

                        return self._create_package_from_data(package_dict, package)
                else:
                    log.error("Unexpected error: skipping dataset %s" % e)
                # bail out
                return {}

        else:
            action_function = get_action('package_update')
            try:
                package_dict['id'] = package.id
                package_dict['name'] = package.name
            except AttributeError:
                package_dict['id'] = package['id']
                package_dict['name'] = package['name']

        try:
            returned_package_dict = action_function(context, package_dict)
            return returned_package_dict
        except ValidationError as e:
            log.error("Validation error: %s" % e)
            if 'Organization does not exist' in str(e):
                log.info("Package validation error: couldn't find organization %s for package %s" % (
                    package_dict['owner_org'], package_dict['name']))
            return {}
        except Exception as e:
            log.error("Unexpected error %s: skipping dataset %s, " % (e, package_dict['name']))
            return {}

    def write_package_from_gemini_string(self, content):
        '''Create or update a Package based on some content that has
        come from a URL.
        Returns the package_dict of the result.
        If there is an error, it returns None or raises Exception.
        '''

        log = logging.getLogger(__name__ + '.import')
        package = None
        gemini_document = metadata_mapping.OdmMimuISODocument(content)
        gemini_values = gemini_document.read_values()
        gemini_guid = gemini_values['guid']

        # Save the metadata reference date in the Harvest Object
        try:
            metadata_modified_date = parse(gemini_values['metadata-date']).utcnow()
        except ValueError:
            print 'Could not extract reference date using dateutil parser ' \
                  'for GUID %s (%s)' % (gemini_guid, gemini_values['metadata-date'])
            return

        self.obj.metadata_modified_date = metadata_modified_date
        self.obj.save()

        last_harvested_object = Session.query(HarvestObject) \
                                       .filter(HarvestObject.guid == gemini_guid) \
                                       .filter(HarvestObject.state == 'COMPLETE') \
                                       .order_by(HarvestObject.gathered.desc()) \
                                       .limit(1).offset(1).first()

        reactivate_package = False
        if last_harvested_object:
            # We've previously harvested this (i.e. it's an update)

            # Use metadata modified date instead of content to determine if the package
            # needs to be updated
            if last_harvested_object.metadata_modified_date is None \
                or last_harvested_object.metadata_modified_date < self.obj.metadata_modified_date \
                or self.force_import \
                or (last_harvested_object.metadata_modified_date == self.obj.metadata_modified_date and
                    last_harvested_object.source.active is False):

                if self.force_import:
                    log.info('Import forced for object %s with GUID %s' % (self.obj.id, gemini_guid))
                else:
                    log.info('Package for object with GUID %s needs to be created or updated' % gemini_guid)

                package = last_harvested_object.package

                # If the package has a deleted state, we will only update it and reactivate it if the
                # new document has a more recent modified date
                if package and package.state == u'deleted':
                    if last_harvested_object.metadata_modified_date < self.obj.metadata_modified_date:
                        log.info('Package for object with GUID %s will be re-activated' % gemini_guid)
                        reactivate_package = True
                    else:
                        log.info('Remote record with GUID %s is not more recent than a '
                                 'deleted package, skipping... ' % gemini_guid)
                        return None

            else:
                if last_harvested_object.content != self.obj.content and \
                   last_harvested_object.metadata_modified_date == self.obj.metadata_modified_date:
                    diff_generator = difflib.unified_diff(
                        last_harvested_object.content.split('\n'),
                        self.obj.content.split('\n'))
                    diff = '\n'.join([line for line in diff_generator])
                    log.error('The contents of document with GUID %s changed, '
                              'but the metadata date has not been updated.\nDiff:\n%s' % (gemini_guid, diff))
                    return None
                else:
                    # The content hasn't changed, no need to update the package
                    log.info('Document with GUID %s unchanged, skipping...' % (gemini_guid))
                return None
        else:
            log.info('No package with GEMINI guid %s found, let\'s create one' % gemini_guid)

        package_dict = self.get_package_dict(gemini_values, gemini_guid, package, reactivate_package=reactivate_package)

        if package_dict is None:
            log.info('Failed dictizing, probably blacklisted, %s' % gemini_guid)
            return

        try:
            if package is None:
                # Create new package from data.
                package = self._create_package_from_data(package_dict)
                log.info('Created new package ID %s with GEMINI guid %s', package['id'], gemini_guid)
            else:
                package = self._create_package_from_data(package_dict, package=package)
                log.info('Updated existing package ID %s with existing GEMINI guid %s', package['id'], gemini_guid)
        except KeyError:
            log.info("Unrecoverable error parsing the package, skipping")
            return None
        
        if package is None or not package.get('id', None):
            log.info("Unrecoverable error parsing the package, skipping")
            return None
            
        # Set reference to package in the HarvestObject and flag it as
        # the current one
        if not self.obj.package_id:
            self.obj.package_id = package['id']

        self.obj.current = True
        self.obj.save()

        if last_harvested_object:
            last_harvested_object.current = False
            last_harvested_object.save()

        return package
