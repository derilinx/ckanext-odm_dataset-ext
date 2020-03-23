# -*- coding: utf-8 -*-
from dateutil.parser import parse
import urllib
import time
import sys
import warnings
import os
import re
import mimetypes
import urllib2
import json
import itertools
import cgitb
from string import Template
from datetime import datetime
from urlparse import urlparse, urlunparse, parse_qs
from pylons import config
from owslib import wms
from bs4 import BeautifulSoup
from urlparse import urlparse, parse_qs
import logging

log = logging.getLogger(__name__)

frequency_map = {
    "continual": "continual",
    "daily": "daily",
    "weekly": "weekly",
    "fortnightly": "fortnightly",
    "monthly": "monthly",
    "quarterly": "quarterly",
    "biannually": "biannually",
    "annually": "annually",
    "asneeded": "asneeded",
    "irregular": "irregular",
    "notplanned": "notplanned",
    "unknown": "Unknown",
}

# List used for normalization and filtering of the machine readable formats
machine_readable_formats = {
    'shapefile': 'shapefile',
    'tab': 'TAB',
    'esri': 'shapefile',
    'arcgis': 'shapefile',
    'nc': 'NetCDF',
    'cdf': 'NetCDF',
    'access': 'Microsoft Access',
    'acess': 'Microsoft Access',
    'arcgis': 'shp',
    'aspx': 'HTML',
    'autocad': 'AutoCAD',
    'cdf': 'NetCDF',
    'csv': 'CSV',
    'database': 'database',
    'dbf': 'database',
    'esri': 'shp',
    'excel': 'XLS',
    'gml': 'GML',
    'gml+xml': 'GML',
    'kml': 'KML',
    'mapinfo': 'TAB',
    'nc': 'NetCDF',
    'netcdf': 'NetCDF',
    'ogc:wms-1.1.1-http-get-map': 'WMS',
    'ogc:wfs-1.0.0-http-get-capabilities': 'WFS',
    'ogc:wms-1.3.0-http-get-capabilities': 'WMS',
    'ogc:wms': "wms",
    'ogc:wfs': "wfs",
    'pdf': 'PDF',
    'php': 'HTML',
    'png': 'PNG',
    'shapefile': 'shp',
    'sql': 'database',
    'tab': 'TAB',
    'tsv': 'TSV',
    'various': 'various formats',
    'vnd.geo+json': 'JSON',
    'vnd.google-earth.kml+xml': 'KML',
    'vnd.ms-excel': 'XLS',
    'wms': 'WMS',
    'www:link-1.0-http--link': 'HTML',
    'x-netcdf': 'NetCDF',
    'x-qgis': 'shp',
    'zip': 'zip'
}

HOMEPAGES = set()


def convert_date_format(value):
    """
    Convert the date to mm/dd/yyyy
    :param value: str
    :return: str
    """
    try:
        _date = parse(value)
        date = _date.strftime("%m/%d/%Y")
        return date
    except Exception as e:
        log.error(e)
        return ''


def convert_to_multilingual(val):
    """
    Covert english to multi lingual data structure
    :param val: str
    :return: dict
    """
    return {
        "lo": "",
        "km": "",
        "th": "",
        "vi": "",
        "my": "",
        "en": val
    }


def get_temporal_date(val):

    if val and isinstance(val, list):
        value = val[0]
        return convert_date_format(value)
    else:
        return ''


def get_package_name(iso_values, package):
    if package is None or package.title != iso_values['title']:
        pkg_name = normalize_name(iso_values['title'])
    else:
        pkg_name = normalize_name(package.name)
    if len(pkg_name) > 100:
        pkg_name = pkg_name[0:100]
    return pkg_name


def test_is_wms(url):
    """
    Checks if the provided URL actually points to a Web Map Service.
    Uses owslib WMS reader to parse the response.
    :param url:
    :return:
    """

    try:
        capabilities_url = wms.WMSCapabilitiesReader().capabilities_url(url)
        res = urllib2.urlopen(capabilities_url, None, 10)
        xml = res.read()
        s = wms.WebMapService(url, xml=xml)
        return isinstance(s.contents, dict) and s.contents != {}
    except Exception, e:
        log.error('WMS check for %s failed with exception: %s' % (url, str(e)))
    return False


def add_package_contact(package_dict, iso_values):
    contact_data = iso_values.get('metadata-point-of-contact')
    package_dict['CI_ResponsibleParty_contact'] = convert_to_multilingual("NA")

    if contact_data and len(contact_data) > 0:
        _name = contact_data[0].get('individual-name')
        _email = contact_data[0]['contact-info'].get('email')
        _phone = contact_data[0]['contact-info'].get('phone')

        package_dict['CI_ResponsibleParty_contact'] = convert_to_multilingual(
            "{} , Email: {}, Tel: {}".format(_name, _email, _phone)
        )
    return package_dict


def get_md_metadata_contact():
    """
    This is hardcoded to opendevelopmentmekong net.
    :return:
    """
    contact = "This is harvested from http://geonode.themimu.info/ to MIMU organization."
    contact = convert_to_multilingual(contact)
    return contact


def add_temporal_coverage(package_dict, iso_values):
    if 'temporal-extent-begin' in iso_values and len(iso_values['temporal-extent-begin']) > 0:
        package_dict['temporal_start'] = iso_values['temporal-extent-begin'][0]
    if 'temporal-extent-end' in iso_values and len(iso_values['temporal-extent-end']) > 0:
        package_dict['temporal_end'] = iso_values['temporal-extent-end'][0]
    return package_dict


def find_tag(xml, tag):
    val = xml.find(tag)
    if val:
        return val.text.strip()
    else:
        return None


def normalize_url(urlstring):
    return urllib.quote(urlstring, safe="%/:=&?~#+!$,;'@()*[]")


def normalize_name(string):
    string = string.strip().lower()
    string = re.sub('\s*&\s*', ' and ', string)
    string = re.sub('\s+', ' ', string)  # squeeze whitespace
    string = string.replace(' ', '_')  # space to underscore
    string = string.replace('-', '_')  # dash to underscore
    string = string.encode('utf-8')
    # Remove fadas from Irish names ('Met Éireann' => 'met-eireann')
    string = string.replace('Á', 'a').replace('á', 'a')
    string = string.replace('É', 'e').replace('é', 'e')
    string = string.replace('Í', 'i').replace('í', 'i')
    string = string.replace('Ó', 'o').replace('ó', 'o')
    string = string.replace('Ú', 'u').replace('ú', 'u')
    string = string.replace('D\xc4\x82\xc5\x9fn', 'Dun').replace('d\xc4\x82\xc5\x9fn', 'dun')
    string = re.sub('\W', '', string)  # remove non-alphanumeric
    string = re.sub('\_+', '_', string)  # squeeze underscore
    string = string.replace('_', '-')  # underscore to dash
    # we use the last 100 chars as its marginally less likely to cause collision
    return string[-100:]  # url names have max length of 100 chars


def normalize_tag(string):
    string = string.lower()
    # remove some stop words
    stop_words = ['&', 'and', 'the']
    for word in stop_words:
        regexp = ''.join(['\s*', word, '\s*'])
        string = re.sub(regexp, ' ', string)
    return normalize_name(string)


def text_traceback():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = 'the original traceback:'.join(
            cgitb.text(sys.exc_info()).split('the original traceback:')[1:]
        ).strip()
    return res


# Remove abbreviations from the end, and expand "&" to "and"
def normalize_publisher(name):
    name = re.sub(' \\([A-Za-z]+\\)$', '', name.strip())
    name = re.sub(' & ', ' and ', name)
    name = name.strip()
    # StatCentral has a technically incorrect name for the department
    if name == 'Department of Environment, Community and Local Government':
        name = 'Department of the Environment, Community and Local Government'
    return name


def urlify(s):
    s = re.sub('[^0-9a-zA-Z]+', ' ', s)
    s = s.lower().replace(" ", "-")
    s = re.sub('-+', '-', s)
    s = re.sub('-+$', '', s)
    s = s.strip()
    if len(s) > 100:
        s = s[:100]
    return s


def guess_standard(content):
    lowered = content.lower()
    if '</gmd:MD_Metadata>'.lower() in lowered:
        return 'iso'
    if '</gmi:MI_Metadata>'.lower() in lowered:
        return 'iso'
    if '</metadata>'.lower() in lowered:
        return 'fgdc'
    return 'unknown'


def guess_resource_format(resource_locator_protocol, resource_name):
    """
    Guess resource format
    :param resource_name:
    :param resource_locator_protocol:
    :return:
    """

    # If no resource name return none
    if not resource_name:
        return None

    # Guess resource from the name
    if resource_name:
        _ext = os.path.splitext(resource_name)
        if _ext:
            rsc_format = _ext[-1].replace(".", "")
            if rsc_format in machine_readable_formats.keys():
                return machine_readable_formats.get(rsc_format)

    # WMS and WFS resources
    if resource_locator_protocol and "wms" in resource_locator_protocol.lower():
        # Not really the wms resource
        return None

    if resource_locator_protocol and "wfs" in resource_locator_protocol.lower():
        # Not really the wms resource
        return None

    # nothing found
    return None


def get_package_frequency(iso_values):
    """
    Get package update frequency
    :param iso_values: dict
    :return: str
    """
    freq = iso_values.get('frequency-of-update').strip()
    if freq and freq.lower() in frequency_map.keys():
        freq = frequency_map.get(freq.lower())
    return freq


def get_package_theme(iso_values, getmap=True):
    if 'mdr-theme' not in iso_values:
        log.debug('No theme property for ' + iso_values['title'])
        return 'Environment'
    elif iso_values['mdr-theme'] == 'Population':
        return 'Society'  # we call it society, but it's the Population one
    else:
        return iso_values['mdr-theme']


def get_package_tags(iso_values, default_tags):
    def normalize_tag(tag):
        return tag.lower().strip().replace("'", "")[:99]

    tags = []
    if 'tags' in iso_values:
        tag_strings = set(x for x in itertools.chain(*[tag.split(',') for tag in iso_values['tags']]))
        tags = [{'name': normalize_tag(t)} for t in tag_strings if t]

    theme = get_package_theme(iso_values, getmap=False)
    if theme:
        tags.append({'name': normalize_tag(theme)})
    # topic tags
    if 'topic-category' in iso_values:
        for tag in iso_values['topic-category']:
            tags.append({'name': normalize_tag(tag)})
    # Add default_tags from the config
    if default_tags:
        for tag in default_tags:
            tags.append({'name': normalize_tag(tag)})

    return tags


def get_package_rights(iso_values, multilingual=False):
    use_constraints = iso_values.get('use-constraints', '')
    use_constraints += iso_values.get('limitations-on-public-access', '')
    use_constraints += iso_values.get('access-constraints', '')
    use_constraints += iso_values.get('other-constraints', '')

    if multilingual:
        if isinstance(use_constraints, list):
            use_constraints = " ".join(use_constraints)
        return convert_to_multilingual(use_constraints or "NA")
    return use_constraints


def get_package_license(iso_values):

    use_constraints = get_package_rights(iso_values)
    license_id = "other-at"

    for const in use_constraints:
        if 'creativecommons.org/licenses/by/4.0' in const:
            license_id = 'CC-BY-4.0'
            return license_id
        elif 'creativecommons.org/licenses/by-nc-nd' in const:
            license_id = 'cc-by-nc-nd'
            return license_id
        elif 'creativecommons.org/licenses/by-nc' in const:
            license_id = 'cc-by-nc'
            return license_id
        elif 'creativecommons.org/licenses/by-nd' in const:
            license_id = 'cc-by-nd'
            return license_id

        else:
            license_id = 'other-at'

    return license_id


def extract_first_license_url(licences):
    for licence in licences:
        o = urlparse(licence)
        if o.scheme and o.netloc:
            return licence
    return None


def add_extras_license(extras_dict, iso_values):
    extras_dict['access_constraints'] = iso_values.get('limitations-on-public-access', '')
    extras_dict['licence'] = iso_values.get('use-constraints', '')
    if len(extras_dict['licence']) > 0:
        license_url_extracted = extract_first_license_url(extras_dict['licence'])
        if license_url_extracted:
            extras_dict['licence_url'] = license_url_extracted
    return extras_dict


def add_extras_graphics(extras_dict, iso_values):
    # Graphic preview
    browse_graphic = iso_values.get('browse-graphic')
    if browse_graphic:
        browse_graphic = browse_graphic[0]
        extras_dict['graphic-preview-file'] = browse_graphic.get('file')
        if browse_graphic.get('description'):
            extras_dict['graphic-preview-description'] = browse_graphic.get('description')
        if browse_graphic.get('type'):
            extras_dict['graphic-preview-type'] = browse_graphic.get('type')
    return extras_dict


def get_vertical_extent(iso_values):
    xml_data = iso_values.get('vertical-extent')
    if len(xml_data) > 0:
        xml_data = xml_data[0]
    if not xml_data:
        return None
    xml = BeautifulSoup(xml_data)
    obj = {
        'verticalDomainName': find_tag(xml, 'gml:name'),
        'minVerticalExtent': find_tag(xml, 'gmd:minimumvalue'),
        'maxVerticalExtent': find_tag(xml, 'gmd:maximumvalue')
    }
    return json.dumps(obj)


def add_package_spatial(package_dict, iso_values, harvest_object=None, save_object_error=None):
    """
    Add spatial reference and bounding box to the package dict
    :param package_dict: dict
    :param iso_values: dict
    :param harvest_object: class instance
    :param save_object_error: class instance
    :return: dict
    """
    if 'spatial-reference-system' in iso_values and iso_values['spatial-reference-system']:
        if '/' in iso_values['spatial-reference-system']:
            package_dict['MD_DataIdentification_spatialReferenceSystem'] = \
                'epsg:' + iso_values['spatial-reference-system'].split('/')[-1]
        elif ':' in iso_values['spatial-reference-system']:
            package_dict['MD_DataIdentification_spatialReferenceSystem'] = \
                'epsg:' + iso_values['spatial-reference-system'].split(':')[-1]
        else:
            package_dict['MD_DataIdentification_spatialReferenceSystem'] = \
                'epsg:' + iso_values['spatial-reference-system']

    scale = iso_values.get('equivalent-scale')
    if scale and len(scale) > 0:
        scale = scale[0]
    if scale == '':
        scale = None
    package_dict['MD_DataIdentification_spatialResolution'] = scale

    if len(iso_values['bbox']) > 0:
        bbox = iso_values['bbox'][0]

        try:
            package_dict['EX_GeographicBoundingBox_west'] = str(bbox['west'])
            package_dict['EX_GeographicBoundingBox_east'] = str(bbox['east'])
            package_dict['EX_GeographicBoundingBox_south'] = str(bbox['south'])
            package_dict['EX_GeographicBoundingBox_north'] = str(bbox['north'])
        except ValueError, e:
            if save_object_error is not None:
                save_object_error('Error parsing bounding box value: {0}'.format(str(e)), harvest_object, 'Import')
            else:
                log.error('Error parsing bounding box value: {0}'.format(str(e)))
    return package_dict


def get_package_citation_date(iso_value, type="publication"):
    """
    Get CI citation publication date or revision date
    :param iso_value: xml data
    :param type: str type of date to be extracted
    :return: str
    """
    date_dict = iso_value.get('dataset-reference-date', {})

    if date_dict:
        for _item in date_dict:
            if _item['type'] == type:
                val = _item['value']
                return convert_date_format(val)

    return ''


def get_dataset_keywords(iso_values, type="odm_keywords"):
    """
    Prepare the keywords for the field odm_keywords and MD_DataIdentification_keywords

    MD_DataIdentification_keywords: contains all the keywors and the types as multilingual string
    :param iso_values: dict
    :param type: str
    :return: string
    """
    _keywords_list = iso_values.get('keywords', [])
    res = []

    if _keywords_list:
        for _item_dict in _keywords_list:
            _keywords = _item_dict.get('keyword')
            res += _keywords

    result = ",".join(res)

    if type == "odm_keywords":
        return result
    else:
        return convert_to_multilingual(result)


def clean_resource_title(title):
    """
    Clean the resource title. Remove resource format
    :param:title: str
    :return: str
    """

    try:
        if title:
            resource_title = " ".join(title.split("_"))
            resource_title = os.path.splitext(resource_title)[0]
            return resource_title
    except Exception as e:
        pass

    return title


def generate_wms_resource_from_layer(resources):
    """
    Generate WMS resource from url.
    Check if the url is of type geo server and contains a layer information.
    :param resources: list
    :return: list
    """
    # Required to validate unique WMS resource
    _unique_names = []
    url_format = "{scheme}://{host}{path}?service={service}&request=GetCapabilities&layers={layers}"
    wms_resources = []

    for resource in resources:
        _url = resource.get('url')

        try:
            _url_parts = urlparse(_url)
            # Change scheme to https. Not sure if this is the right way
            #_scheme = _url_parts.scheme
            _scheme = "https"
            _path = _url_parts.path
            _host = _url_parts.hostname

            # Parse the query to dict
            _query_dict = parse_qs(_url_parts.query)

            # url should contain path and layer information
            # layer parameter can be either LAYER (for png), layers (for KML)
            if _path == "/geoserver/wms" and ("layers" in _query_dict
                                             or "layer" in _query_dict
                                             or "LAYER" in _query_dict):

                original_res_name = resource.get('name', '')

                # Check if WMS resource already exists
                if original_res_name not in _unique_names:
                    layers = _query_dict.get("layer", '') or \
                             _query_dict.get('layers', '') or _query_dict.get('LAYER', '')

                    # Create new resource only if layer information exists
                    if layers:
                        _name = "WMS from {resource_name}".format(resource_name=resource.get('name'))
                        _description = "WMS file generated from {}".format(resource.get('name'))
                        res_url = url_format.format(
                            scheme=_scheme,
                            host=_host,
                            path=_path,
                            service="WMS",
                            layers=layers[0]
                        )

                        new_resource = dict(
                            url=normalize_url(res_url),
                            name=_name,
                            format="WMS",
                            name_translated=convert_to_multilingual(_name),
                            description=_description,
                            description_translated=convert_to_multilingual(_description),
                            resource_locator_protocol="wms",
                            resource_locator_function='',
                            odm_language=["en"]
                        )

                        # New unique WMS resource
                        _unique_names.append(original_res_name)
                        wms_resources.append(new_resource)

        except Exception as e:
            log.error(e)
            pass

    return wms_resources


def get_package_resources(iso_values):

    resources = []
    resource_locators = iso_values.get('resource-locator', []) + iso_values.get('resource-locator-identification', [])
    _resource_name_unique = []

    if len(resource_locators) > 0:
        for resource_locator in resource_locators:
            url = resource_locator.get('url', '').strip()
            if url:
                resource = {}
                _resource_name = resource_locator.get('name', '')
                _resource_locator_protocol = resource_locator.get('protocol', 'unknown').strip().lower()
                res_format = guess_resource_format(_resource_locator_protocol, _resource_name)

                # Parse resources with name and resource format
                if res_format and (_resource_name not in _resource_name_unique):
                    _resource_name_unique.append(_resource_name)
                    resource['format'] = res_format
                    if resource['format'] == 'WMS' and config.get('ckanext.spatial.harvest.validate_wms', False):
                        # Check if the service is a view service
                        test_url = url.split('?')[0] if '?' in url else url
                        if test_is_wms(test_url):
                            resource['verified'] = True
                            resource['verified_date'] = datetime.now().isoformat()

                    resource_description = resource_locator.get('description', '') or 'Available as ' + resource['format']
                    resource_title = clean_resource_title(_resource_name)  # Clean the resource name to be title

                    resource.update({
                        'url': normalize_url(url),
                        'name': resource_title,
                        'name_translated': convert_to_multilingual(resource_title),
                        'description': resource_description,
                        'description_translated': convert_to_multilingual(resource_description),
                        'resource_locator_protocol': resource_locator.get('protocol') or '',
                        'resource_locator_function': resource_locator.get('function') or '',
                        'odm_language': ["en"]
                    })

                    data_formats = iso_values.get('data-format', [])
                    if (resource['format'].lower() == 'zip') and data_formats:

                        data_formats = data_formats[0]  # usually(>) there's only one item in the array
                        format_names = data_formats.get('name', '')  # may be a list separated by , or a single element

                        if 'esri' in format_names.lower():
                            resource['format'] = 'SHP'
                            resources.append(resource)
                        else:
                            resources.append(resource)
                    else:
                        resources.append(resource)

    # Create WMS resource if the url contains necessary information.
    wms_resources = generate_wms_resource_from_layer(resources)
    return resources + wms_resources
