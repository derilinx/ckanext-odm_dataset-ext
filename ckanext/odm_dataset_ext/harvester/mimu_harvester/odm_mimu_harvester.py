# -*- coding: utf-8 -*-
from ckanext.odm_dataset_ext.harvester.mimu_harvester.odm_csw import ODMMimuSpatialCSW
from pylons import config
from ckan import model
from ckan import plugins as p
from ckanext.odm_dataset_ext.harvester.mimu_harvester import helper as h
import logging

log = logging.getLogger(__name__)

# List of the Departments / Organisations we want to publish
department_normalize = {
}

department_blacklist = [
]

dataset_blacklist = [
]


class ODMMimuSpatialHarvester(ODMMimuSpatialCSW):
    force_import = True or p.toolkit.asbool(
        p.toolkit.config.get('ckanext.dgithree.harvester_ignore_metadata_modified', False))

    def info(self):
        return {
            'name': 'odmmimuspatial',
            'title': 'ODM MIMU Spatial',
            'description': 'Gemini Harvester customised for omd mimu dataset harvester'
        }

    def get_package_dict(self, iso_values, gemini_guid, package, reactivate_package=False, save_object_error=None):
        """
        Mapping of MIMU metadata to ODM metadata is done here
        :param iso_values:
        :param gemini_guid:
        :param package:
        :param reactivate_package:
        :param save_object_error:
        :return:
        """

        package_dict = {
            'id': h.get_package_name(iso_values, package),
            'name': h.get_package_name(iso_values, package),
            'title_translated': h.convert_to_multilingual(iso_values['title']),
            'notes_translated': h.convert_to_multilingual(iso_values['abstract']),
            'private': True,
            'license_id': h.get_package_license(iso_values),
            'taxonomy': ["Infrastructure"],  # TODO
            'MD_DataIdentification_language': iso_values.get('dataset-language') or ["en"],
            'MD_Constraints': h.get_md_constraints(),
            'owner_org': 'mimu',  # All the data set belongs to mimu
            'CI_Citation_date': h.get_package_citation_date(iso_values),
            'MD_Metadata_dateStamp': iso_values.get('metadata-date'),
            'CI_Citation_lastRevision': h.get_package_citation_date(iso_values, type="revision"),
            'EX_TemporalExtent_startDate': h.get_temporal_date(iso_values.get('temporal-extent-begin')),
            'EX_TemporalExtent_endDate': h.get_temporal_date(iso_values.get('temporal-extent-end')),
            'odm_spatial_range': ["mm"],
            'EX_GeographicBoundingBox_west': '',  # This will be added by helper
            'EX_GeographicBoundingBox_east': '',  # This will be added by helper
            'EX_GeographicBoundingBox_south': '',  # This will be added by helper
            'EX_GeographicBoundingBox_north': '',  # This will be added by helper
            'MD_DataIdentification_spatialResolution': '',  # This will be added by helper
            'MD_DataIdentification_spatialReferenceSystem': '',  # This will be added by helper
            'DQ_PositionalAccuracy': h.convert_to_multilingual(''),
            'DQ_QuantitativeAttribute': h.convert_to_multilingual(''),
            'DQ_LogicalConsistency':  h.convert_to_multilingual(''),
            'DQ_Completeness':  h.get_dq_completeness(),
            'LI_ProcessStep':  h.convert_to_multilingual(''),
            'LI_Lineage': h.get_li_lineage(),
            'CI_ResponsibleParty_contact': '',
            'MD_Metadata_contact': h.get_md_metadata_contact(),
            'MD_ScopeDescription_attributes': h.convert_to_multilingual(''),
            'MD_DataIdentification_keywords': h.get_dataset_keywords(iso_values,
                                                                     type="MD_DataIdentification_keywords"),
            'CI_Citation_identAuth': h.convert_to_multilingual(''),
            'MD_LegalConstraints': h.convert_to_multilingual(" ".join(iso_values.get(
                'limitations-on-public-access', []))),
            'MD_Format_version': h.convert_to_multilingual(" ".join(iso_values.get('data-format', []))),
            'CI_Citation_updateFreq': h.ci_citation_update_freq(),
            'odm_copyright': h.odm_copyright(),
            'version': '',
            'odm_province': '',
            'odm_reference_document': '',
            'odm_keywords': h.get_dataset_keywords(iso_values),
            'resources': h.get_package_resources(iso_values)
        }

        # Add package contact
        h.add_package_contact(package_dict, iso_values)

        # Update package bounding box
        package_dict = h.add_package_spatial(package_dict, iso_values)

        # If the dataset does not meet the criteria we mark the datase as invisible
        # The harvester does not allow to "skip" the dataset without errors
        # Only active datasets show up in search results and other lists of datasets
        # To permanently delete ('purge') a dataset, go to the dataset's 'Edit' page, and delete it.
        # The list of deleted datasets is available at http://<my-ckan-url>/ckan-admin/trash/
        if len(package_dict['resources']) == 0:
            package_dict['state'] = 'deleted'

        package_dict['author'] = "Myanmar Information Management Unit MIMU"

        if package_dict['name'] in dataset_blacklist:
            package_dict['state'] = 'deleted'
            log.info("Dataset %s in blacklist, not adding", package_dict['name'])
            with open('/var/log/supervisor/blacklist.log', 'a+') as bfile:
                bfile.write('\ndataset_blacklist\n')
                bfile.write(
                    '%s -- %s' % (package_dict['author'], package_dict.get('author_email', 'No email provided')))
                bfile.write('\n')
                bfile.write(package_dict['name'])
                bfile.write('\n')
            if save_object_error is not None:
                save_object_error('Dataset in blacklist', package_dict['name'], 'Import')
            return
        else:
            if package_dict['author'] in department_normalize:
                package_dict['author'] = department_normalize.get(package_dict['author'])

            package_dict['owner_org'] = h.normalize_name(package_dict['author'].encode('utf-8'))

            with open('/var/log/supervisor/blacklist.log', 'a+') as bfile:
                bfile.write('\nprocessed\n')
                bfile.write(
                    '%s -- %s' % (package_dict['author'], package_dict.get('author_email', 'No email provided')))
                bfile.write('\n')
                bfile.write(package_dict['name'])
                bfile.write('\n')

            return package_dict
