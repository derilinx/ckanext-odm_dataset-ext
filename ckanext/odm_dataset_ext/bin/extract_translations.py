import json
import csv

languages = ["en", "th", "km", "vi", "my", 'lo']
fields = ["field_name", "label", 'en', 'Context']
fields.extend(languages[1:])


def extract_one(source, dest, field_type='dataset_fields'):

    with open (source, 'r') as f:
        schema = json.load(f)

    translations = []

    for field in schema[field_type]:
        if field.get('preset',None) == 'text_hidden': continue


        for item in ('label', 'form_placeholder', 'help_text'):
            if not item in field: continue
            elt = { 'field_name': field['field_name'],
                    'label': item,
                    'Context': "%s.%s" % (field['field_name'], item),
            }
            if type(field[item]) == type({}):
                for lang in languages:
                    elt[lang] = field[item].get(lang, '').encode('utf-8')
            else:
                elt['en'] = field[item].encode('utf-8')
                for lang in languages[1:]:
                    elt[lang] = ''

            translations.append(elt)
    
    print(dest)
    with open(dest, 'w') as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        for item in translations:
            writer.writerow(item)

def import_one(dest_json, src_csv, field_type='dataset_fields'):
    with open(src_csv, 'r') as f:
        f.readline()
        reader = csv.DictReader(f, fields)
        translations = { r['Context']: [r[l] for l in languages] for r in reader if r['Context'] }

    with open('translations.json', 'w') as f:
        json.dump(translations, f, indent=4)

    with open(dest_json, 'r') as f:
        schema = json.load(f)

    for field in schema[field_type]:
        for item in ('label', 'form_placeholder', 'help_text'):
            try:
                del(field['form_languages'])
            except: pass
            context = '.'.join((field['field_name'], item))
            print "Context: %s" % context
            if context in translations:
                existing = field.get(item,{})
                if type(existing) != type({}):
                    existing = {'en':existing}
                existing.update({l:v.decode('utf-8') for l,v in zip(languages, translations[context]) if v})
                field[item] = existing

    with open (dest_json, 'w') as f:
        json.dump(schema,f, indent=4)

def extract_all_dataset():
    extract_one('../odm_dataset_schema.json', 'odm_dataset_schema.csv')
    extract_one('../../../../' + 'ckanext-odm_laws/ckanext/odm_laws/odm_laws_schema.json', 'odm_laws_schema.csv')
    extract_one('../../../../' + 'ckanext-odm_library/ckanext/odm_library/odm_library_schema.json', 'odm_library_schema.csv')
    extract_one('../../../../' + 'ckanext-odm_agreement/ckanext/odm_agreement/odm_agreement_schema.json', 'odm_agreement_schema.csv')
    extract_one('../../../../' + 'ckanext-odm_profiles/ckanext/odm_profiles/odm_profiles_schema.json', 'odm_profile.csv')
    extract_one('../../../../' + 'ckanext-odm_profiles/ckanext/odm_profiles/odm_map_schema.json', 'odm_map.csv')

def extract_all_resource():
    extract_one('../odm_dataset_schema.json', 'odm_dataset_resource_schema.csv', 'resource_fields')
    extract_one('../../../../' + 'ckanext-odm_laws/ckanext/odm_laws/odm_laws_schema.json', 'odm_laws_resource_schema.csv', 'resource_fields')
    extract_one('../../../../' + 'ckanext-odm_library/ckanext/odm_library/odm_library_schema.json', 'odm_library_resource_schema.csv', 'resource_fields')
    extract_one('../../../../' + 'ckanext-odm_agreement/ckanext/odm_agreement/odm_agreement_schema.json', 'odm_agreement_resource_schema.csv', 'resource_fields')

def import_all_dataset():
    import_one('../odm_dataset_schema_not_required.json', 'odm_dataset_schema.csv')
    import_one('../odm_dataset_schema_required.json', 'odm_dataset_schema.csv')
    import_one('../../../../' + 'ckanext-odm_laws/ckanext/odm_laws/odm_laws_schema.json', 'odm_laws_schema.csv')
    import_one('../../../../' + 'ckanext-odm_library/ckanext/odm_library/odm_library_schema.json', 'odm_library_schema.csv')
    import_one('../../../../' + 'ckanext-odm_agreement/ckanext/odm_agreement/odm_agreement_schema.json', 'odm_agreement_schema.csv')
    import_one('../../../../' + 'ckanext-odm_profiles/ckanext/odm_profiles/odm_profiles_schema.json', 'odm_profile.csv')
    import_one('../../../../' + 'ckanext-odm_profiles/ckanext/odm_profiles/odm_map_schema.json', 'odm_map.csv')

def import_all_resource():
    import_one('../odm_dataset_schema_not_required.json', 'odm_dataset_resource_schema.csv', 'resource_fields')
    import_one('../odm_dataset_schema_required.json', 'odm_dataset_resource_schema.csv', 'resource_fields')
    import_one('../../../../' + 'ckanext-odm_laws/ckanext/odm_laws/odm_laws_schema.json', 'odm_laws_resource_schema.csv', 'resource_fields')
    import_one('../../../../' + 'ckanext-odm_library/ckanext/odm_library/odm_library_schema.json', 'odm_library_resource_schema.csv', 'resource_fields')
    import_one('../../../../' + 'ckanext-odm_agreement/ckanext/odm_agreement/odm_agreement_schema.json', 'odm_agreement_resource_schema.csv', 'resource_fields')

def import_all_resource():
    # This is the corrected one because changes in odm_dataset_schema_required.json or odm_dataset_schema_not_required.json
    # is not reflecting in odm_dataset_schema.json
    import_one('../odm_dataset_schema_not_required.json', 'odm_dataset_resource_schema.csv', 'resource_fields')
    import_one('../odm_dataset_schema_required.json', 'odm_dataset_resource_schema.csv', 'resource_fields')
    import_one('../odm_dataset_schema.json', 'odm_dataset_resource_schema.csv', 'resource_fields')
    import_one('../../../../' + 'ckanext-odm_laws/ckanext/odm_laws/odm_laws_schema.json', 'odm_laws_resource_schema.csv', 'resource_fields')
    import_one('../../../../' + 'ckanext-odm_library/ckanext/odm_library/odm_library_schema.json', 'odm_library_resource_schema.csv', 'resource_fields')
    import_one('../../../../' + 'ckanext-odm_agreement/ckanext/odm_agreement/odm_agreement_schema.json', 'odm_agreement_resource_schema.csv', 'resource_fields')

import_all_resource()
#extract_all_dataset()
#extract_all_resource()
#import_all_dataset()
