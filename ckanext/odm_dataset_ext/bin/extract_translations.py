import json
import csv

languages = ["en", "th", "km", "vi", "my"]
fields = ["field_name", "label"]
fields.extend(languages)


def extract_one(source, dest):

    with open (source, 'r') as f:
        schema = json.load(f)

    translations = []

    for field in schema['dataset_fields']:
        if field.get('preset',None) == 'text_hidden': continue


        for item in ('label', 'form_placeholder', 'help_text'):
            if not item in field: continue
            elt = { 'field_name': field['field_name'],
                    'label': item
            }
            if type(field[item]) == type({}):
                for lang in languages:
                    elt[lang] = field[item].get(lang, '').encode('utf-8')
            else:
                elt['en'] = field[item].encode('utf-8')
                for lang in languages[1:]:
                    elt[lang] = ''

            translations.append(elt)


    with open(dest, 'w') as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        for item in translations:
            writer.writerow(item)

extract_one('../odm_dataset_schema.json', 'odm_dataset_schema.csv')
extract_one('../../../../' + 'ckanext-odm_laws/ckanext/odm_laws/odm_laws_schema.json', 'odm_laws_schema.csv')
extract_one('../../../../' + 'ckanext-odm_library/ckanext/odm_library/odm_library_schema.json', 'odm_library_schema.csv')
extract_one('../../../../' + 'ckanext-odm_agreement/ckanext/odm_agreement/odm_agreement_schema.json', 'odm_agreement_schema.csv')
