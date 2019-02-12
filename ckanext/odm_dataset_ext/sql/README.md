## schema_conversion.sql

- sql script to do the conversion from the existing ODM1 database to the new schema
- `psql -f schema_conversion -U ckan -h db ckan`

## cleanup.sql
- routines to fixup as much as possible the EIA/asdf issue.
