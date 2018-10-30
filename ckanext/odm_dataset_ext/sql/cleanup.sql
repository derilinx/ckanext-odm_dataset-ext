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
