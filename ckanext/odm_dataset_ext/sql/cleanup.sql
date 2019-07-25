begin;
update resource_revision set current=(revision_id in (select revision_id from resource));
commit;

--select id, revision_id in (select revision_id from resource) from resource_revision;


with rh (id, revision_id, name, description, extras) 
as (select distinct on (id)  id, revision_id, name, description, extras
from resource_revision
where 
current='f'
and trim(name) != 'EIA'
and name not like '%asdf%'
and trim(description) != 'EIA'
and description not like '%asdf%'
order by id, revision_timestamp desc)
select package_id, resource.id, trim(resource.description), trim(rh.description)
from resource inner join rh using (id)
   where trim(resource.name) = 'EIA'
   or trim(resource.description) = 'EIA'
   or resource.name like '%asdf%'
   or resource.description like '%asdf%';


--
-- What does the previous version look like for these?
-- including the name_translated

with rh (id, revision_id, name, description, extras) 
as (
  select distinct on (id)  id, revision_id, name, description, extras
  from resource_revision
  where 
    current='f'
    and trim(name) != 'EIA'
    and name not like '%asdf%'
    and trim(description) != 'EIA'
    and description not like '%asdf%'
  order by id, revision_timestamp desc)
select
  package_id,
  resource.name,
  rh.name,
  trim(both '"' from resource.extras::json->>'name_translated')::json->>'en' as name_translated_en,
  trim(both '"' from rh.extras::json->>'name_translated')::json->>'en' as rh_name_translated_en
from resource inner join rh using (id)
   where
   resource.name = 'EIA'
;

--
-- The case where the translated title is actually correct, and only non-translated one has EIA
--
begin;

-- select

with res (id, extras, name_translated_en)
as (select
  id,
  extras,
  trim(both '"' from resource.extras::json->>'name_translated')::json->>'en' as name_translated_en
from resource
where name = 'EIA'
and trim(both '"' from resource.extras::json->>'name_translated')::json->>'en' != ''
and trim(both '"' from resource.extras::json->>'name_translated')::json->>'en' != 'EIA'
)
select id, name, name_translated_en
from resource inner join res using (id)
where name = 'EIA';

-- update returning id,name
with res (id, extras, name_translated_en)
as (select
  id,
  extras,
  trim(both '"' from resource.extras::json->>'name_translated')::json->>'en' as name_translated_en
from resource
where name = 'EIA'
and trim(both '"' from resource.extras::json->>'name_translated')::json->>'en' != ''
and trim(both '"' from resource.extras::json->>'name_translated')::json->>'en' != 'EIA'
)
update resource set name=name_translated_en
from res
where res.id = resource.id
and name = 'EIA'
returning resource.id, name;

commit;

--
-- And after
--

with rh (id, revision_id, name, description, extras)
as (select distinct on (id)  id, revision_id, name, description, extras
from resource_revision
where
current='f'
and trim(name) != 'EIA'
and name not like '%asdf%'
and trim(description) != 'EIA'
and description not like '%asdf%'
order by id, revision_timestamp desc)
select
  package_id,
  resource.name,
  trim(both '"' from resource.extras::json->>'name_translated')::jsonb || '{"en":"Unnamed Resource"}'::jsonb as name_translated,
  jsonb_set(resource.extras::jsonb,
            '{name_translated}',
             to_jsonb(replace(resource.extras::json->>'name_translated', 'EIA', 'Unnamed Resource'))
             )
from resource inner join rh using (id)
   where
   resource.name = 'EIA'
;


--
-- Lets put the "lo" one into the name if that's what we have
--

begin;

with res (id, extras, name_translated_lo)
as (select
  id,
  extras,
  trim(both '"' from resource.extras::json->>'name_translated')::json->>'lo' as name_translated_lo
from resource
where name = 'EIA'
and trim(both '"' from resource.extras::json->>'name_translated')::json->>'lo' != ''
and trim(both '"' from resource.extras::json->>'name_translated')::json->>'lo' != 'EIA'
)
update resource
set
  name=name_translated_lo,
  extras = jsonb_set(resource.extras::jsonb,
            '{name_translated}',
             to_jsonb(replace(resource.extras::json->>'name_translated', 'EIA', 'Unnamed Resource'))
             )
from res
where
  res.id = resource.id
  and name = 'EIA'
returning
  resource.id,
  name,
  trim(both '"' from resource.extras::json->>'name_translated')::json->>'en' as name_translated_en
;

commit;


--
-- Now pull from previous revision
-- including the name_translated

with rh (id, revision_id, name, description, extras, name_translated_en)
as (
  select distinct on (id)
    id,
    revision_id,
    name,
    description,
    extras,
    trim(both '"' from extras::json->>'name_translated')::json->>'en'
  from resource_revision
  where
    current='f'
    and trim(name) != 'EIA'
    and trim(description) != 'EIA'
  order by id, revision_timestamp desc)
select
  package_id,
  resource.name,
  case when rh.name != '' then rh.name else rh.name_translated_en end,
  rh.extras::json->>'name_translated'
from resource inner join rh using (id)
   where
   resource.name = 'EIA'
   and (rh.name != ''
        or ( rh.name_translated_en != '' and rh.name_translated_en != 'EIA'))
;

--
-- update from the previous versions
--

begin;

with rh (id, revision_id, name, description, extras, name_translated_en)
as (
  select distinct on (id)
    id,
    revision_id,
    name,
    description,
    extras,
    trim(both '"' from extras::json->>'name_translated')::json->>'en'
  from resource_revision
  where
    current='f'
    and trim(name) != 'EIA'
    and trim(description) != 'EIA'
  order by id, revision_timestamp desc)
update resource
  set name = case when rh.name != '' then rh.name else rh.name_translated_en end,
  extras = jsonb_set(resource.extras::jsonb,
            '{name_translated}',
             (rh.extras::json->'name_translated')::jsonb
             )
from rh
   where
   resource.id = rh.id
   and resource.name = 'EIA'
   and (rh.name != ''
        or ( rh.name_translated_en != '' and rh.name_translated_en != 'EIA'))
returning
  resource.id,
  resource.name,
  trim(both '"' from resource.extras::json->>'name_translated')::json->>'en' as name_translated_en
;

commit;

--
-- And clear out the rest of them
--
with rh (id, revision_id, name, description, extras) 
as (
  select distinct on (id)  id, revision_id, name, description, extras
  from resource_revision
  where 
    current='f'
    and trim(name) != 'EIA'
    and trim(description) != 'EIA'
  order by id, revision_timestamp desc)
select
  package_id,
  resource.name,
  rh.name,
  trim(both '"' from resource.extras::json->>'name_translated')::json->>'en' as name_translated_en,
  trim(both '"' from rh.extras::json->>'name_translated')::json->>'en' as rh_name_translated_en
from resource inner join rh using (id)
   where
   resource.name = 'EIA'
;


begin;

update resource
set
  name='Unnamed Resource',
  extras = jsonb_set(resource.extras::jsonb,
            '{name_translated}',
             to_jsonb(replace(resource.extras::json->>'name_translated', 'EIA', 'Unnamed Resource'))
             )
where
  name = 'EIA'
returning
  resource.id,
  name,
  resource.extras::json->>'name_translated' as name_translated
;

commit;


--
-- ASDF
--

--
-- The case where the translated description is actually correct, and only non-translated one has asdf
--

-- select

with res (id, extras, description_translated_en)
as (select
  id,
  extras,
  trim(both '"' from resource.extras::json->>'description_translated')::json->>'en' as description_translated_en
from resource
where description = 'asdf'
and trim(both '"' from resource.extras::json->>'description_translated')::json->>'en' != ''
and trim(both '"' from resource.extras::json->>'description_translated')::json->>'en' != 'asdf'
)
select id, description, description_translated_en
from resource inner join res using (id)
where description = 'asdf';


begin;

-- update returning id,name
with res (id, extras, description_translated_en)
as (select
  id,
  extras,
  trim(both '"' from resource.extras::json->>'description_translated')::json->>'en' as description_translated_en
from resource
where description = 'asdf'
and trim(both '"' from resource.extras::json->>'description_translated')::json->>'en' != ''
and trim(both '"' from resource.extras::json->>'description_translated')::json->>'en' != 'asdf'
)
update resource set description=description_translated_en
from res
where res.id = resource.id
and description = 'asdf'
returning resource.id, description;

commit;



--
-- Now pull from previous revision
-- including the name_translated

with rh (id, revision_id, description, extras, description_translated_en)
as (
  select distinct on (id)
    id,
    revision_id,
    description,
    extras,
    trim(both '"' from extras::json->>'description_translated')::json->>'en'
  from resource_revision
  where
    current='f'
    and trim(description) != 'asdf'
  order by id, revision_timestamp desc)
select
  package_id,
  resource.description,
  case when rh.description != '' then rh.description else rh.description_translated_en end,
  rh.extras::json->>'description_translated'
from resource inner join rh using (id)
   where
   resource.description = 'asdf'
   and (rh.description != ''
        or ( rh.description_translated_en != '' and rh.description_translated_en != 'asdf'))
;

--
-- update from the previous versions
--

begin;

with rh (id, revision_id, description, extras, description_translated_en)
as (
  select distinct on (id)
    id,
    revision_id,
    description,
    extras,
    trim(both '"' from extras::json->>'description_translated')::json->>'en'
  from resource_revision
  where
    current='f'
    and trim(description) != 'asdf'
  order by id, revision_timestamp desc)
update resource
  set description = case when rh.description != '' then rh.description else rh.description_translated_en end,
  extras = jsonb_set(resource.extras::jsonb,
            '{description_translated}',
             (rh.extras::json->'description_translated')::jsonb
             )
from rh
   where
   resource.id = rh.id
   and resource.description = 'asdf'
   and (rh.description != ''
        or ( rh.description_translated_en != '' and rh.description_translated_en != 'asdf'))
returning
  resource.id,
  resource.description,
  trim(both '"' from resource.extras::json->>'description_translated')::json->>'en' as description_translated_en
;

commit;


--
-- And the rest of them.
--

begin;

update resource
set
  description='No Description Provided',
  extras = jsonb_set(resource.extras::jsonb,
            '{description_translated}',
             to_jsonb(replace(resource.extras::json->>'description_translated', 'asdf', 'No Description Provided'))
             )
where
  description = 'asdf'
returning
  resource.id,
  description,
  resource.extras::json->>'description_translated' as description_translated
;

commit;


-- The translated items don't appear to have been updated.

with rh (id, revision_id, name_translated, description_translated)
as (
  select distinct on (id)
    id,
    revision_id,
    trim(both '"' from extras::json->>'name_translated')::json,
    trim(both '"' from extras::json->>'description_translated')::json
  from resource_revision
  where
    not (extras like '%asdf%' or extras like '%EIA%')
  order by id, revision_timestamp desc)
 select
  id,
  name,
  rh.name_translated,
  rh.description_translated
  from resource inner join rh using (id)
  where (extras like '%asdf%' or extras like '%EIA%')
  and trim(both '"' from extras::json->>'name_translated')::jsonb @> '{"en": "EIA", "vi": "", "km": "", "th": "", "lo": "", "my": ""}'::jsonb
  and trim(both '"' from extras::json->>'description_translated')::jsonb @> '{"en": "asdf", "vi": "", "km": "", "th": "", "lo": "", "my": ""}'::jsonb
  and name_translated is not null and description_translated is not null;


select
  id,
  trim(both '"' from extras::json->>'name_translated')::json,
  trim(both '"' from extras::json->>'description_translated')::json
from resource
  where (extras like '%asdf%' or extras like '%EIA%')


begin;

  
with rh (id, revision_id, name_translated, description_translated)
as (
  select distinct on (id)
    id,
    revision_id,
    trim(both '"' from extras::json->>'name_translated')::jsonb,
    trim(both '"' from extras::json->>'description_translated')::jsonb
  from resource_revision
  where
    not (extras like '%asdf%' or extras like '%EIA%')
  order by id, revision_timestamp desc)
 update resource
 set
 !!!Undone -- this should be a string of a json object!!!
   extras = jsonb_set(
              jsonb_set(resource.extras::jsonb,
                        '{description_translated}',
                        rh.description_translated
                        ),
              '{name_translated}',
              rh.name_translated)
  from rh 
  where
  rh.id = resource.id
  and (extras like '%asdf%' or extras like '%EIA%')
  and trim(both '"' from extras::json->>'name_translated')::jsonb @> '{"en": "EIA", "vi": "", "km": "", "th": "", "lo": "", "my": ""}'::jsonb
  and trim(both '"' from extras::json->>'description_translated')::jsonb @> '{"en": "asdf", "vi": "", "km": "", "th": "", "lo": "", "my": ""}'::jsonb
  and name_translated is not null and description_translated is not null;

commit;




-- Those items where there's a junk name/description_translated, and nothing in the history, but something in the name/description
 select
  id,
  name,
  description,
  jsonb_set(
       jsonb_set(extras::jsonb,
                 '{description_translated}',
                 to_jsonb(jsonb_set(trim(both '"' from extras::json->>'description_translated')::jsonb,
                                '{en}', to_jsonb(description))::text)),
       '{name_translated}',
       to_jsonb(jsonb_set(trim(both '"' from extras::json->>'name_translated')::jsonb,
                '{en}', to_jsonb(name))::text)) as extras
  from resource
  where (extras like '%EIA%' or extras like '%asdf%')
  and trim(both '"' from extras::json->>'name_translated')::jsonb @> '{"en": "EIA", "vi": "", "km": "", "th": "", "lo": "", "my": ""}'::jsonb
  and trim(both '"' from extras::json->>'description_translated')::jsonb @> '{"en": "asdf", "vi": "", "km": "", "th": "", "lo": "", "my": ""}'::jsonb
  and description is not null and description != ''
  and name is not null and name != ''
;


begin;

update resource
set extras = jsonb_set(
       jsonb_set(extras::jsonb,
                 '{description_translated}',
                 to_jsonb(jsonb_set(trim(both '"' from extras::json->>'description_translated')::jsonb,
                                '{en}', to_jsonb(description))::text)),
       '{name_translated}',
       to_jsonb(jsonb_set(trim(both '"' from extras::json->>'name_translated')::jsonb,
                '{en}', to_jsonb(name))::text)) 
  where (extras like '%EIA%' or extras like '%asdf%')
  and trim(both '"' from extras::json->>'name_translated')::jsonb @> '{"en": "EIA", "vi": "", "km": "", "th": "", "lo": "", "my": ""}'::jsonb
  and trim(both '"' from extras::json->>'description_translated')::jsonb @> '{"en": "asdf", "vi": "", "km": "", "th": "", "lo": "", "my": ""}'::jsonb
  and description is not null and description != ''
  and name is not null and name != ''
;

commit;


-- Those items where there's a junk name_translated, no description and nothing in the history, but something in the name
 select
  id,
  name,
  description,
  jsonb_set(
       jsonb_set(extras::jsonb,
                 '{description_translated}',
                 to_jsonb(jsonb_set(trim(both '"' from extras::json->>'description_translated')::jsonb,
                                '{en}', to_jsonb(description))::text)),
       '{name_translated}',
       to_jsonb(jsonb_set(trim(both '"' from extras::json->>'name_translated')::jsonb,
                '{en}', to_jsonb(name))::text)) as extras
  from resource
  where (extras like '%EIA%' or extras like '%asdf%')
  and trim(both '"' from extras::json->>'name_translated')::jsonb @> '{"en": "EIA", "vi": "", "km": "", "th": "", "lo": "", "my": ""}'::jsonb
  and trim(both '"' from extras::json->>'description_translated')::jsonb @> '{"en": "asdf", "vi": "", "km": "", "th": "", "lo": "", "my": ""}'::jsonb
  and name is not null and name != ''
;


begin;

 update resource set
   extras = jsonb_set(
       jsonb_set(extras::jsonb,
                 '{description_translated}',
                 to_jsonb(jsonb_set(trim(both '"' from extras::json->>'description_translated')::jsonb,
                                '{en}', to_jsonb(description))::text)),
       '{name_translated}',
       to_jsonb(jsonb_set(trim(both '"' from extras::json->>'name_translated')::jsonb,
                '{en}', to_jsonb(name))::text))
  where (extras like '%EIA%' or extras like '%asdf%')
  and trim(both '"' from extras::json->>'name_translated')::jsonb @> '{"en": "EIA", "vi": "", "km": "", "th": "", "lo": "", "my": ""}'::jsonb
  and trim(both '"' from extras::json->>'description_translated')::jsonb @> '{"en": "asdf", "vi": "", "km": "", "th": "", "lo": "", "my": ""}'::jsonb
  and name is not null and name != ''
;

commit;



-- format names

-- # sql for updating
update resource set format=tr.translated
  from  ( VALUES
    ('.pdf', 'PDF'),
    ('website', 'HTML'),
    ('Website', 'HTML'),
    ('archived webpage', 'HTML'),
    ('url', 'URL'),
    ('.html', 'HTML'),
    ('geotiff', 'GeoTIFF'),
    ('pdf', 'PDF'),
    ('zipped shapefile', 'SHP'),
    ('.zip', 'ZIP'),
    ('csv', 'CSV'),
    ('application/x-msdos-program', 'Unknown'),
    ('PFD', 'PDF'),
    ('.htm', 'HTML'),
    ('GeoTiff', 'GeoTIFF'),
    ('HTLM', 'HTML'),
    ('application/msword', 'DOC'),
    ('psf', 'PDF'),
    ('JEPG', 'JPEG'),
    ('tif', 'TIFF'),
    ('Geotiff', 'GeoTIFF'),
    ('word', 'DOC'),
    ('xml', 'XML'),
    ('ipg', 'JPEG'),
    ('KMZ', 'KML'),
    ('xlsm', 'XLSX')
) as tr (original, translated)
where
resource.format = tr.original;
